import cv2
import numpy as np
import time
import collections
from pykinect2 import PyKinectRuntime, PyKinectV2
from telemetrix import telemetrix

# --- PARCHES DE COMPATIBILIDAD PYTHON 3.10+ ---
if not hasattr(time, 'clock'):
    time.clock = time.perf_counter
import numpy

numpy.object = object


class PCA9685_Controller:
    def __init__(self, board, address=0x40):
        self.board = board
        self.addr = address
        self.last_angles = {}

        self.board.set_pin_mode_i2c()
        time.sleep(0.1)

        self.board.i2c_write(self.addr, [0x00, 0x10])
        time.sleep(0.005)
        self.board.i2c_write(self.addr, [0xFE, 121])
        self.board.i2c_write(self.addr, [0x00, 0x21])
        time.sleep(0.005)

    def set_angle(self, channel, angle):
        SAFE_MIN = 15
        SAFE_MAX = 165
        angle = max(SAFE_MIN, min(SAFE_MAX, angle))

        if self.last_angles.get(channel) == angle:
            return
        self.last_angles[channel] = angle

        tick_min = 150
        tick_max = 600
        tick = int(tick_min + (angle / 180.0) * (tick_max - tick_min))

        reg = 0x06 + 4 * channel
        self.board.i2c_write(self.addr, [reg, 0, 0, tick & 0xFF, tick >> 8])


class ArabotsPuppetMonitor:
    def __init__(self):
        print("Iniciando sensor Kinect V2...")
        self._kinect = PyKinectRuntime.PyKinectRuntime(
            PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body
        )
        self._kinect.bodies = numpy.ndarray((6), dtype=object)
        self.view_w, self.view_h = 960, 540
        self._bodies = None
        self.target_body_id = None

        print("Conectando con Arduino UNO R4...")
        self.board = telemetrix.Telemetrix()

        def ignora_ruido(*args, **kwargs):
            pass

        self.board.spi_callback = ignora_ruido
        if hasattr(self.board, 'report_dispatch'):
            for i in range(256):
                if i not in self.board.report_dispatch or self.board.report_dispatch[i] is None:
                    self.board.report_dispatch[i] = ignora_ruido

        self.board.dht_callbacks = collections.defaultdict(lambda: ignora_ruido)
        self.board.sonar_callbacks = collections.defaultdict(lambda: ignora_ruido)

        self.board.set_pin_mode_digital_output(13)
        for _ in range(3):
            self.board.digital_write(13, 1)
            time.sleep(0.1)
            self.board.digital_write(13, 0)
            time.sleep(0.1)
        self.board.digital_write(13, 1)

        print("\n==========================================")
        print(" [✓] ARDUINO CONECTADO EXITOSAMENTE  (ツ) ")
        print("==========================================")

        self.pca = PCA9685_Controller(self.board)

        self.servo_channels = {
            "MANO D": {"X": 0, "Y": 1},
            "MANO I": {"X": 2, "Y": 3},
            "PIE D": {"X": 4, "Y": 5},
            "PIE I": {"X": 6, "Y": 7},
            "CABEZA": {"Y": 8}
        }

        self.system_state = "ESPERANDO_BODY"
        self.calibrated_refs = {}
        self.last_update_time = time.time()
        self.calibration_start_time = None
        self.current_matrix_text = ""

        self.set_matrix_text("ARABOTS LISTO", 60)

        print("Mandando a posición de reposo inicial...")
        self.go_to_rest_pose()

    def set_matrix_text(self, text, scroll_speed=50):
        if text == self.current_matrix_text:
            return

        self.current_matrix_text = text
        text_clean = str(text).upper().strip()[:25]

        payload = [58, len(text_clean), scroll_speed] + [ord(c) for c in text_clean]

        if hasattr(self.board, '_send_command'):
            try:
                self.board._send_command(payload)
            except Exception as e:
                print(f"Error matriz LED: {e}")

    def go_to_rest_pose(self):
        for part, channels in self.servo_channels.items():
            if "X" in channels:
                self.pca.set_angle(channels["X"], 90)
            if "Y" in channels:
                if part == "CABEZA":
                    self.pca.set_angle(channels["Y"], 90)
                else:
                    self.pca.set_angle(channels["Y"], 15)

    def map_to_servo(self, value, in_min, in_max):
        angle = int((value - in_min) * (180 - 0) / (in_max - in_min) + 0)
        return angle

    def get_color_joint_points(self, joints):
        joint_points = numpy.ndarray((PyKinectV2.JointType_Count), dtype=object)
        for j in range(0, PyKinectV2.JointType_Count):
            joint_points[j] = self._kinect._mapper.MapCameraPointToColorSpace(joints[j].Position)
        return joint_points

    def is_raising_hands(self, joints):
        head_y = joints[PyKinectV2.JointType_Head].Position.y
        return (joints[PyKinectV2.JointType_HandLeft].Position.y > head_y and
                joints[PyKinectV2.JointType_HandRight].Position.y > head_y)

    def is_touching_foot(self, joints):
        hand_l = joints[PyKinectV2.JointType_HandLeft].Position
        foot_l = joints[PyKinectV2.JointType_FootLeft].Position
        dist = np.sqrt((hand_l.x - foot_l.x) ** 2 + (hand_l.y - foot_l.y) ** 2 + (hand_l.z - foot_l.z) ** 2)
        return dist < 0.20

    def draw_skeleton(self, img, joints, joint_points):
        connections = [
            (PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck),
            (PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder),
            (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft),
            (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight),
            (PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft),
            (PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft),
            (PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight),
            (PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight),
            (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid),
            (PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase),
            (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft),
            (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight),
            (PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft),
            (PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft),
            (PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight),
            (PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)
        ]

        for j1, j2 in connections:
            if joints[j1].TrackingState == PyKinectV2.TrackingState_Tracked and \
                    joints[j2].TrackingState == PyKinectV2.TrackingState_Tracked:
                start = (int(joint_points[j1].x * self.view_w / 1920), int(joint_points[j1].y * self.view_h / 1080))
                end = (int(joint_points[j2].x * self.view_w / 1920), int(joint_points[j2].y * self.view_h / 1080))
                if not np.isinf(start).any() and not np.isinf(end).any():
                    cv2.line(img, start, end, (255, 255, 0), 2)

    def run(self):
        print("\nSISTEMA ARABOTS INICIADO")

        puntos = {
            "CABEZA": PyKinectV2.JointType_Head,
            "MANO D": PyKinectV2.JointType_HandRight,
            "MANO I": PyKinectV2.JointType_HandLeft,
            "PIE D": PyKinectV2.JointType_FootRight,
            "PIE I": PyKinectV2.JointType_FootLeft
        }

        while True:
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                img = frame.reshape((1080, 1920, 4))
                img = cv2.resize(img, (self.view_w, self.view_h))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            else:
                img = np.zeros((self.view_h, self.view_w, 3), np.uint8)

            if self._kinect.has_new_body_frame():
                self._bodies = self._kinect.get_last_body_frame()

            if self._bodies is not None:

                any_body_tracked = False
                for i in range(0, self._kinect.max_body_count):
                    if self._bodies.bodies[i].is_tracked:
                        any_body_tracked = True
                        break

                if not any_body_tracked:
                    self.system_state = "ESPERANDO_BODY"
                    self.target_body_id = None
                    self.set_matrix_text("HOLA", 50)
                    cv2.putText(img, "ESPERANDO BODY - PONTE FRENTE A LA CAMARA", (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (255, 0, 0), 2)
                else:
                    selected_body = None
                    if self.target_body_id is not None:
                        for i in range(0, self._kinect.max_body_count):
                            body = self._bodies.bodies[i]
                            if body.is_tracked and body.tracking_id == self.target_body_id:
                                selected_body = body
                                break

                    if self.system_state == "ESPERANDO_BODY":
                        self.set_matrix_text("ARABOTS", 60)
                        cv2.putText(img, "LEVANTA LAS MANOS PARA CAPTURAR", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                    (0, 255, 255), 2)

                        for i in range(0, self._kinect.max_body_count):
                            body = self._bodies.bodies[i]
                            if body.is_tracked and self.is_raising_hands(body.joints):
                                self.target_body_id = body.tracking_id
                                print(f"\n[+] BODY CAPTURADO: {self.target_body_id}. Esperando Calibracion...")
                                self.system_state = "ESPERANDO_CALIBRACION"
                                self.calibration_start_time = None
                                selected_body = body
                                break

                    if selected_body:
                        joints = selected_body.joints
                        joint_points = self.get_color_joint_points(joints)
                        self.draw_skeleton(img, joints, joint_points)

                        color_R = (0, 255, 0) if selected_body.hand_right_state == 2 else \
                            (0, 0, 255) if selected_body.hand_right_state == 3 else (0, 255, 255)
                        color_L = (0, 255, 0) if selected_body.hand_left_state == 2 else \
                            (0, 0, 255) if selected_body.hand_left_state == 3 else (0, 255, 255)

                        # --- ESTADO 2: CALIBRACIÓN ---
                        if self.system_state == "ESPERANDO_CALIBRACION":
                            self.set_matrix_text("PUNO", 40)

                            # CAMBIO: Usamos "or" en lugar de "and" para que baste con un solo puño
                            one_hand_closed = (
                                        selected_body.hand_right_state == 3 or selected_body.hand_left_state == 3)

                            if one_hand_closed:
                                if self.calibration_start_time is None:
                                    self.calibration_start_time = time.time()

                                elapsed_time = time.time() - self.calibration_start_time
                                progress = min(elapsed_time / 3.0, 1.0)  # Reducido a 3 segundos

                                bar_w = 400
                                bar_h = 30
                                bar_x = (self.view_w - bar_w) // 2
                                bar_y = 40

                                cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
                                cv2.rectangle(img, (bar_x, bar_y), (bar_x + int(bar_w * progress), bar_y + bar_h),
                                              (0, 255, 0), -1)
                                cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (255, 255, 255), 2)
                                cv2.putText(img, f"CALIBRANDO: {int(progress * 100)}%", (bar_x + 100, bar_y + 22),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                                if elapsed_time >= 3.0:  # Calibración a los 3 segundos
                                    print("\n[+] CALIBRANDO... Guardando punto cero.")
                                    for nombre, jt_id in puntos.items():
                                        pos = joints[jt_id].Position
                                        self.calibrated_refs[nombre] = {"x": pos.x, "y": pos.y}

                                    self.go_to_rest_pose()
                                    self.system_state = "TRACKING"
                                    self.calibration_start_time = None
                                    print("[+] ¡SISTEMA CALIBRADO Y TRACKEANDO!")
                                    time.sleep(0.5)
                            else:
                                self.calibration_start_time = None
                                cv2.putText(img, "MANTEN UN PUNO CERRADO POR 3 SEGUNDOS", (20, 30),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

                        # --- ESTADO 3: TRACKING ---
                        elif self.system_state == "TRACKING":
                            self.set_matrix_text("TRACKING", 50)
                            cv2.putText(img, "TRACKEANDO - TOCA TU PIE IZQUIERDO PARA SOLTAR", (20, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                            if self.is_touching_foot(joints):
                                print(f"\n[!] OBJETIVO {self.target_body_id} LIBERADO")
                                self.target_body_id = None
                                self.system_state = "ESPERANDO_BODY"
                                self.go_to_rest_pose()
                                continue

                            needs_recalibration = False
                            for nombre, jt_id in puntos.items():
                                pos = joints[jt_id].Position
                                ref = self.calibrated_refs[nombre]
                                canales = self.servo_channels[nombre]

                                if "X" in canales and abs(pos.x - ref['x']) > 2.0:
                                    needs_recalibration = True
                                    break
                                if "Y" in canales and abs(pos.y - ref['y']) > 2.0:
                                    needs_recalibration = True
                                    break

                            if needs_recalibration:
                                print("[!] Entrando en Modo Seguro. Solicitando RECALIBRACION.")
                                self.system_state = "ESPERANDO_CALIBRACION"
                                self.go_to_rest_pose()
                                continue

                            current_time = time.time()
                            if current_time - self.last_update_time > 0.1:
                                for nombre, jt_id in puntos.items():
                                    pos = joints[jt_id].Position
                                    ref = self.calibrated_refs[nombre]
                                    canales = self.servo_channels[nombre]

                                    if "X" in canales:
                                        ax = self.map_to_servo(pos.x, ref['x'] - 0.5, ref['x'] + 0.5)
                                        self.pca.set_angle(canales["X"], ax)

                                    if "Y" in canales:
                                        if nombre == "CABEZA":
                                            pos_neck = joints[PyKinectV2.JointType_Neck].Position
                                            inclinacion = pos_neck.z - pos.z
                                            y_virtual = pos.y - (inclinacion * 1.5)
                                            ay = self.map_to_servo(y_virtual, ref['y'] - 0.15, ref['y'] + 0.15)
                                        else:
                                            ay = self.map_to_servo(pos.y, ref['y'], ref['y'] + 0.7)

                                        self.pca.set_angle(canales["Y"], ay)

                                self.last_update_time = current_time

                        # --- DIBUJOS EN PANTALLA ---
                        for nombre, jt_id in puntos.items():
                            jp = joint_points[jt_id]
                            if not np.isinf(jp.x):
                                px = int(jp.x * self.view_w / 1920)
                                py = int(jp.y * self.view_h / 1080)

                                dot_color = color_R if "MANO D" in nombre else \
                                    color_L if "MANO I" in nombre else (255, 255, 255)

                                cv2.circle(img, (px, py), 15, dot_color, -1)
                                cv2.circle(img, (px, py), 18, (255, 255, 255), 2)

                                if self.system_state == "TRACKING":
                                    pos = joints[jt_id].Position
                                    ref = self.calibrated_refs[nombre]
                                    canales = self.servo_channels[nombre]

                                    txt_x = str(max(15, min(165, self.map_to_servo(pos.x, ref['x'] - 0.5, ref[
                                        'x'] + 0.5)))) if "X" in canales else "--"

                                    if nombre == "CABEZA":
                                        pos_neck = joints[PyKinectV2.JointType_Neck].Position
                                        inclinacion = pos_neck.z - pos.z
                                        y_virtual = pos.y - (inclinacion * 1.5)
                                        txt_y = str(max(15, min(165, self.map_to_servo(y_virtual, ref['y'] - 0.15,
                                                                                       ref['y'] + 0.15))))
                                    else:
                                        txt_y = str(max(15, min(165, self.map_to_servo(pos.y, ref['y'], ref[
                                            'y'] + 0.7)))) if "Y" in canales else "--"

                                    cv2.putText(img, f"{nombre}: X{txt_x} Y{txt_y}", (px + 20, py),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            cv2.imshow('Arabots Puppet Master', img)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        print("\nApagando sistema...")
        self.set_matrix_text(" ", 0)
        self.board.digital_write(13, 0)
        self.board.shutdown()
        self._kinect.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    ArabotsPuppetMonitor().run()