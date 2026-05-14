import cv2
import numpy as np
import time
import collections
import threading
import customtkinter as ctk
from PIL import Image
from pykinect2 import PyKinectRuntime, PyKinectV2
from telemetrix import telemetrix

# --- PARCHES DE COMPATIBILIDAD PYTHON 3.10+ ---
if not hasattr(time, 'clock'):
    time.clock = time.perf_counter
import numpy
numpy.object = object

# ======================================================================
# CONTROLADORES DE HARDWARE (PCA9685 y ARDUINO)
# ======================================================================
class PCA9685_Controller:
    def __init__(self, board, address=0x40):
        self.board = board
        self.addr = address
        self.last_angles = {}
        self.smoothed_angles = {}

        self.board.set_pin_mode_i2c()
        time.sleep(0.1)
        self.board.i2c_write(self.addr, [0x00, 0x10])
        time.sleep(0.005)
        self.board.i2c_write(self.addr, [0xFE, 121])
        self.board.i2c_write(self.addr, [0x00, 0x21])
        time.sleep(0.005)

    def set_angle(self, channel, target_angle, smoothing=1.0):
        SAFE_MIN = 15
        SAFE_MAX = 165
        target_angle = max(SAFE_MIN, min(SAFE_MAX, target_angle))

        if channel not in self.smoothed_angles:
            self.smoothed_angles[channel] = target_angle

        current_smoothed = (smoothing * target_angle) + ((1.0 - smoothing) * self.smoothed_angles[channel])
        self.smoothed_angles[channel] = current_smoothed

        final_angle = int(current_smoothed)

        if self.last_angles.get(channel) == final_angle:
            return
        self.last_angles[channel] = final_angle

        tick_min = 150
        tick_max = 600
        tick = int(tick_min + (final_angle / 180.0) * (tick_max - tick_min))

        reg = 0x06 + 4 * channel
        self.board.i2c_write(self.addr, [reg, 0, 0, tick & 0xFF, tick >> 8])

# ======================================================================
# MOTOR LÓGICO DEL KINECT (Corre en un Hilo Separado)
# ======================================================================
class ArabotsCore(threading.Thread):
    def __init__(self, gui_app):
        super().__init__()
        self.gui = gui_app
        self.daemon = True
        self.running = True

        # Banderas para los botones del GUI
        self.force_release = False
        self.force_reset = False

        self.system_state = "ESPERANDO_BODY"
        self.target_body_id = None
        self.calibrated_refs = {}
        self.last_update_time = time.time()
        self.calibration_start_time = None
        self.current_matrix_text = ""

        self.servo_channels = {
            "MANO D": {"X": 0, "Y": 1},
            "MANO I": {"X": 2, "Y": 3},
            "PIE D":  {"X": 4, "Y": 5},
            "PIE I":  {"X": 6, "Y": 7},
            "CABEZA": {"Y": 8}
        }

        self.puntos = {
            "CABEZA": PyKinectV2.JointType_Head,
            "MANO D": PyKinectV2.JointType_HandRight,
            "MANO I": PyKinectV2.JointType_HandLeft,
            "PIE D": PyKinectV2.JointType_FootRight,
            "PIE I": PyKinectV2.JointType_FootLeft
        }

        print("Iniciando Kinect...")
        self._kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        self._kinect.bodies = numpy.ndarray((6), dtype=object)

        print("Iniciando Arduino...")
        self.board = telemetrix.Telemetrix()
        def ignora_ruido(*args, **kwargs): pass
        self.board.spi_callback = ignora_ruido
        if hasattr(self.board, 'report_dispatch'):
            for i in range(256):
                if i not in self.board.report_dispatch or self.board.report_dispatch[i] is None:
                    self.board.report_dispatch[i] = ignora_ruido
        self.board.dht_callbacks = collections.defaultdict(lambda: ignora_ruido)
        self.board.sonar_callbacks = collections.defaultdict(lambda: ignora_ruido)

        self.board.set_pin_mode_digital_output(13)
        self.pca = PCA9685_Controller(self.board)

        self.set_matrix_text(self.gui.get_msg_ready(), 60)
        self.go_to_rest_pose()

    def set_matrix_text(self, text, scroll_speed=50):
        if text == self.current_matrix_text: return
        self.current_matrix_text = text
        text_clean = str(text).upper().strip()[:25]
        payload = [58, len(text_clean), scroll_speed] + [ord(c) for c in text_clean]
        if hasattr(self.board, '_send_command'):
            try: self.board._send_command(payload)
            except: pass

    def go_to_rest_pose(self):
        for part, channels in self.servo_channels.items():
            if "X" in channels: self.pca.set_angle(channels["X"], 90)
            if "Y" in channels:
                if part == "CABEZA": self.pca.set_angle(channels["Y"], 90)
                else: self.pca.set_angle(channels["Y"], 15)

    def map_to_servo(self, value, in_min, in_max):
        return int((value - in_min) * (180 - 0) / (in_max - in_min) + 0)

    def is_raising_hands(self, joints):
        head_y = joints[PyKinectV2.JointType_Head].Position.y
        return (joints[PyKinectV2.JointType_HandLeft].Position.y > head_y and
                joints[PyKinectV2.JointType_HandRight].Position.y > head_y)

    def is_touching_foot(self, joints):
        hand_l = joints[PyKinectV2.JointType_HandLeft].Position
        foot_l = joints[PyKinectV2.JointType_FootLeft].Position
        dist = np.sqrt((hand_l.x - foot_l.x)**2 + (hand_l.y - foot_l.y)**2 + (hand_l.z - foot_l.z)**2)
        return dist < 0.20

    def get_color_joint_points(self, joints):
        joint_points = numpy.ndarray((PyKinectV2.JointType_Count), dtype=object)
        for j in range(0, PyKinectV2.JointType_Count):
            joint_points[j] = self._kinect._mapper.MapCameraPointToColorSpace(joints[j].Position)
        return joint_points

    def run(self):
        while self.running:
            # --- EVALUAR BOTONES DEL GUI ---
            if self.force_reset:
                print("\n[!] RESET DE EMERGENCIA ACTIVADO")
                self.target_body_id = None
                self.system_state = "ESPERANDO_BODY"
                self.calibrated_refs = {}
                self.calibration_start_time = None
                self.go_to_rest_pose()
                self.force_reset = False

            if self.force_release:
                print("\n[!] SOLTANDO OBJETIVO (RELEASE)")
                self.target_body_id = None
                self.system_state = "ESPERANDO_BODY"
                self.calibration_start_time = None
                self.go_to_rest_pose()
                self.force_release = False

            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                img = frame.reshape((1080, 1920, 4))
                img = cv2.resize(img, (960, 540))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # Filtros
                if self.gui.get_mirror(): img = cv2.flip(img, 1)
                alpha = self.gui.get_contrast()
                beta = self.gui.get_brightness()
                if alpha != 1.0 or beta != 0:
                    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
            else:
                img = np.zeros((540, 960, 3), np.uint8)

            if self._kinect.has_new_body_frame():
                self._bodies = self._kinect.get_last_body_frame()

            status_text = ""
            calib_progress = 0.0

            if self._bodies is not None:
                any_body_tracked = any(self._bodies.bodies[i].is_tracked for i in range(self._kinect.max_body_count))

                if not any_body_tracked:
                    self.system_state = "ESPERANDO_BODY"
                    self.target_body_id = None
                    self.set_matrix_text(self.gui.get_msg_idle(), 50)
                    status_text = "ESPERANDO BODY - PONTE FRENTE A LA CAMARA"
                else:
                    selected_body = None
                    if self.target_body_id is not None:
                        for i in range(self._kinect.max_body_count):
                            body = self._bodies.bodies[i]
                            if body.is_tracked and body.tracking_id == self.target_body_id:
                                selected_body = body
                                break

                    if self.system_state == "ESPERANDO_BODY":
                        self.set_matrix_text(self.gui.get_msg_ready(), 60)
                        status_text = "LEVANTA LAS MANOS PARA CAPTURAR"

                        for i in range(self._kinect.max_body_count):
                            body = self._bodies.bodies[i]
                            if body.is_tracked and self.is_raising_hands(body.joints):
                                self.target_body_id = body.tracking_id
                                self.system_state = "ESPERANDO_CALIBRACION"
                                self.calibration_start_time = None
                                selected_body = body
                                break

                    if selected_body:
                        joints = selected_body.joints
                        joint_points = self.get_color_joint_points(joints)

                        # ESQUELETO
                        connections = [(PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck), (PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder), (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft), (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight), (PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft), (PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft), (PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight), (PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight), (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid), (PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase), (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft), (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight), (PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft), (PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft), (PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight), (PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)]
                        for j1, j2 in connections:
                            if joints[j1].TrackingState == PyKinectV2.TrackingState_Tracked and joints[j2].TrackingState == PyKinectV2.TrackingState_Tracked:
                                px1, py1 = int(joint_points[j1].x * 960 / 1920), int(joint_points[j1].y * 540 / 1080)
                                px2, py2 = int(joint_points[j2].x * 960 / 1920), int(joint_points[j2].y * 540 / 1080)
                                if self.gui.get_mirror():
                                    px1, px2 = 960 - px1, 960 - px2
                                if not np.isinf(px1) and not np.isinf(px2):
                                    cv2.line(img, (px1, py1), (px2, py2), (255, 255, 0), 2)

                        # COLORES DE MANOS
                        color_R = (0, 255, 0) if selected_body.hand_right_state == 2 else (0, 0, 255) if selected_body.hand_right_state == 3 else (0, 255, 255)
                        color_L = (0, 255, 0) if selected_body.hand_left_state == 2 else (0, 0, 255) if selected_body.hand_left_state == 3 else (0, 255, 255)

                        # --- ESTADO 2: CALIBRACIÓN ---
                        if self.system_state == "ESPERANDO_CALIBRACION":
                            self.set_matrix_text(self.gui.get_msg_calib(), 40)
                            if selected_body.hand_right_state == 3 or selected_body.hand_left_state == 3:
                                if self.calibration_start_time is None: self.calibration_start_time = time.time()
                                elapsed = time.time() - self.calibration_start_time
                                calib_progress = min(elapsed / 3.0, 1.0)
                                status_text = f"CALIBRANDO: {int(calib_progress*100)}%"

                                if elapsed >= 3.0:
                                    for nombre, jt_id in self.puntos.items():
                                        self.calibrated_refs[nombre] = {"x": joints[jt_id].Position.x, "y": joints[jt_id].Position.y}
                                    self.go_to_rest_pose()
                                    self.system_state = "TRACKING"
                                    self.calibration_start_time = None
                                    time.sleep(0.5)
                            else:
                                self.calibration_start_time = None
                                status_text = "MANTEN UN PUNO CERRADO POR 3 SEGUNDOS"

                        # --- ESTADO 3: TRACKING ---
                        elif self.system_state == "TRACKING":
                            self.set_matrix_text(self.gui.get_msg_track(), 50)
                            status_text = "TRACKEANDO - TOCA TU PIE IZQUIERDO PARA SOLTAR"

                            if self.is_touching_foot(joints):
                                self.force_release = True # Usamos la misma bandera del botón
                                continue

                            sensibilidad = self.gui.get_sensibilidad()
                            smoothing = self.gui.get_smoothing()
                            update_delay = self.gui.get_update_speed()

                            current_time = time.time()
                            if current_time - self.last_update_time > update_delay:
                                for nombre, jt_id in self.puntos.items():
                                    pos = joints[jt_id].Position
                                    ref = self.calibrated_refs[nombre]
                                    canales = self.servo_channels[nombre]

                                    if "X" in canales:
                                        ax = self.map_to_servo(pos.x, ref['x'] - sensibilidad, ref['x'] + sensibilidad)
                                        self.pca.set_angle(canales["X"], ax, smoothing)
                                    if "Y" in canales:
                                        if nombre == "CABEZA":
                                            pos_neck = joints[PyKinectV2.JointType_Neck].Position
                                            y_virt = pos.y - ((pos_neck.z - pos.z) * 1.5)
                                            ay = self.map_to_servo(y_virt, ref['y'] - (sensibilidad/2), ref['y'] + (sensibilidad/2))
                                        else:
                                            ay = self.map_to_servo(pos.y, ref['y'], ref['y'] + (sensibilidad*1.5))
                                        self.pca.set_angle(canales["Y"], ay, smoothing)
                                self.last_update_time = current_time

                        # PUNTOS Y TEXTOS EN VIDEO
                        for nombre, jt_id in self.puntos.items():
                            jp = joint_points[jt_id]
                            if not np.isinf(jp.x):
                                px, py = int(jp.x * 960 / 1920), int(jp.y * 540 / 1080)
                                if self.gui.get_mirror(): px = 960 - px

                                dot_color = color_R if "MANO D" in nombre else color_L if "MANO I" in nombre else (255, 255, 255)
                                cv2.circle(img, (px, py), 15, dot_color, -1)
                                cv2.circle(img, (px, py), 18, (255, 255, 255), 2)

                                if self.system_state == "TRACKING":
                                    pos = joints[jt_id].Position
                                    ref = self.calibrated_refs[nombre]
                                    sens = self.gui.get_sensibilidad()
                                    canales = self.servo_channels[nombre]

                                    txt_x = str(max(15, min(165, self.map_to_servo(pos.x, ref['x']-sens, ref['x']+sens)))) if "X" in canales else "--"
                                    if nombre == "CABEZA":
                                        pos_neck = joints[PyKinectV2.JointType_Neck].Position
                                        y_virt = pos.y - ((pos_neck.z - pos.z) * 1.5)
                                        txt_y = str(max(15, min(165, self.map_to_servo(y_virt, ref['y']-(sens/2), ref['y']+(sens/2)))))
                                    else:
                                        txt_y = str(max(15, min(165, self.map_to_servo(pos.y, ref['y'], ref['y']+(sens*1.5))))) if "Y" in canales else "--"

                                    cv2.putText(img, f"{nombre}: X{txt_x} Y{txt_y}", (px + 20, py), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            self.gui.push_frame_and_status(img, status_text, calib_progress)
            time.sleep(0.01)

        print("Cerrando hardware...")
        self.set_matrix_text(" ", 0)
        self.board.shutdown()
        self._kinect.close()

# ======================================================================
# INTERFAZ GRÁFICA (GUI)
# ======================================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ArabotsGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Arabots Puppet Master - Panel de Control")
        self.geometry("1000x750")

        self.tabview = ctk.CTkTabview(self, width=960, height=720)
        self.tabview.pack(padx=10, pady=10, expand=True, fill="both")

        self.tab_monitor = self.tabview.add("Monitor Principal")
        self.tab_settings = self.tabview.add("Ajustes y Calibración")

        # --- TAB 1: MONITOR ---
        self.video_label = ctk.CTkLabel(self.tab_monitor, text="Iniciando Cámara Kinect...")
        self.video_label.pack(pady=5)

        self.status_frame = ctk.CTkFrame(self.tab_monitor, fg_color="#1F2937", corner_radius=10)
        self.status_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = ctk.CTkLabel(self.status_frame, text="INICIANDO...", font=("Arial", 16, "bold"), text_color="#38BDF8")
        self.status_label.pack(side="left", padx=20, pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=200, progress_color="#22C55E", fg_color="#374151")
        self.progress_bar.set(0)
        self.progress_bar.pack(side="right", padx=20, pady=10)
        self.progress_bar.pack_forget()

        # --- BOTONERA DE ACCIÓN RÁPIDA ---
        self.action_frame = ctk.CTkFrame(self.tab_monitor, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=10, pady=5)

        self.btn_release = ctk.CTkButton(self.action_frame, text="Soltar Objetivo (Release)",
                                         fg_color="#F59E0B", hover_color="#D97706",
                                         font=("Arial", 14, "bold"), height=40,
                                         command=self.cmd_release)
        self.btn_release.pack(side="left", padx=10, expand=True, fill="x")

        self.btn_reset = ctk.CTkButton(self.action_frame, text="Reinicio de Emergencia (Reset)",
                                       fg_color="#EF4444", hover_color="#DC2626",
                                       font=("Arial", 14, "bold"), height=40,
                                       command=self.cmd_reset)
        self.btn_reset.pack(side="right", padx=10, expand=True, fill="x")

        # --- TAB 2: AJUSTES ---
        frame_cam = ctk.CTkFrame(self.tab_settings)
        frame_cam.pack(padx=20, pady=10, fill="x")
        ctk.CTkLabel(frame_cam, text="Ajustes de Cámara (Software)", font=("Arial", 16, "bold")).pack(pady=5)

        self.switch_mirror = ctk.CTkSwitch(frame_cam, text="Modo Espejo (Voltear Cámara)")
        self.switch_mirror.select()
        self.add_labeled_widget(frame_cam, "Orientación:", self.switch_mirror)

        self.slider_bright = ctk.CTkSlider(frame_cam, from_=-50, to=50, width=300)
        self.slider_bright.set(0)
        self.add_labeled_widget(frame_cam, "Brillo:", self.slider_bright)

        self.slider_contrast = ctk.CTkSlider(frame_cam, from_=1.0, to=3.0, width=300)
        self.slider_contrast.set(1.0)
        self.add_labeled_widget(frame_cam, "Contraste:", self.slider_contrast)

        frame_msg = ctk.CTkFrame(self.tab_settings)
        frame_msg.pack(padx=20, pady=10, fill="x")
        ctk.CTkLabel(frame_msg, text="Textos de Matriz LED", font=("Arial", 16, "bold")).pack(pady=5)

        self.entry_idle = ctk.CTkEntry(frame_msg, width=300)
        self.entry_idle.insert(0, "HOLA")
        self.add_labeled_widget(frame_msg, "Mensaje de Reposo:", self.entry_idle)

        self.entry_ready = ctk.CTkEntry(frame_msg, width=300)
        self.entry_ready.insert(0, "ARABOTS")
        self.add_labeled_widget(frame_msg, "Mensaje Listo:", self.entry_ready)

        self.entry_calib = ctk.CTkEntry(frame_msg, width=300)
        self.entry_calib.insert(0, "PUNO")
        self.add_labeled_widget(frame_msg, "Mensaje Calibrando:", self.entry_calib)

        self.entry_track = ctk.CTkEntry(frame_msg, width=300)
        self.entry_track.insert(0, "TRACKING")
        self.add_labeled_widget(frame_msg, "Mensaje Tracking:", self.entry_track)

        frame_mot = ctk.CTkFrame(self.tab_settings)
        frame_mot.pack(padx=20, pady=10, fill="x")
        ctk.CTkLabel(frame_mot, text="Física de los Motores", font=("Arial", 16, "bold")).pack(pady=5)

        self.slider_sens = ctk.CTkSlider(frame_mot, from_=0.2, to=1.0, width=300)
        self.slider_sens.set(0.5)
        self.add_labeled_widget(frame_mot, "Sensibilidad (Zona de Movimiento):", self.slider_sens)

        self.slider_smooth = ctk.CTkSlider(frame_mot, from_=0.05, to=1.0, width=300)
        self.slider_smooth.set(0.5)
        self.add_labeled_widget(frame_mot, "Suavizado (Smoothing):", self.slider_smooth)

        self.slider_speed = ctk.CTkSlider(frame_mot, from_=0.03, to=0.2, width=300)
        self.slider_speed.set(0.1)
        self.add_labeled_widget(frame_mot, "Delay de I2C (Velocidad de señal):", self.slider_speed)

        self.latest_frame = None
        self.backend = ArabotsCore(self)
        self.backend.start()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_labeled_widget(self, parent, text, widget):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(container, text=text, width=200, anchor="w").pack(side="left")
        widget.pack(side="left", padx=10)

    # --- Comandos de Botones ---
    def cmd_release(self):
        if hasattr(self, 'backend'): self.backend.force_release = True

    def cmd_reset(self):
        if hasattr(self, 'backend'): self.backend.force_reset = True

    # --- Getters ---
    def get_msg_idle(self): return self.entry_idle.get()
    def get_msg_ready(self): return self.entry_ready.get()
    def get_msg_calib(self): return self.entry_calib.get()
    def get_msg_track(self): return self.entry_track.get()
    def get_sensibilidad(self): return self.slider_sens.get()
    def get_smoothing(self): return self.slider_smooth.get()
    def get_update_speed(self): return self.slider_speed.get()
    def get_mirror(self): return self.switch_mirror.get() == 1
    def get_brightness(self): return int(self.slider_bright.get())
    def get_contrast(self): return self.slider_contrast.get()

    def push_frame_and_status(self, cv_img, status_text, calib_progress):
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        self.latest_frame = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(960, 540))
        self.after(0, self._render_ui, status_text, calib_progress)

    def _render_ui(self, status_text, calib_progress):
        if self.latest_frame:
            self.video_label.configure(image=self.latest_frame, text="")

        self.status_label.configure(text=status_text)

        if calib_progress > 0:
            self.progress_bar.set(calib_progress)
            self.progress_bar.pack(side="right", padx=20, pady=10)
        else:
            self.progress_bar.pack_forget()

    def on_closing(self):
        print("Solicitando cierre...")
        self.backend.running = False
        self.backend.join(timeout=2.0)
        self.destroy()

if __name__ == "__main__":
    app = ArabotsGUI()
    app.mainloop()