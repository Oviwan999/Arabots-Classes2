import cv2
import numpy as np
import time
import collections
import threading
import math
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
# DICCIONARIO INTERNACIONAL DE TRADUCCIONES
# ======================================================================
LANGUAGES = {
    "es": {"wait": "ESPERANDO BODY - PONTE FRENTE A LA CAMARA", "raise": "LEVANTA LAS MANOS PARA CAPTURAR",
           "fist": "JUNTA TUS MANOS POR 3 SEG", "calib": "CALIBRANDO",
           "track": "TRACKEANDO - TOCA TU PIE IZQUIERDO PARA SOLTAR"},
    "en": {"wait": "WAITING FOR BODY - STAND IN FRONT OF CAMERA", "raise": "RAISE YOUR HANDS TO CAPTURE",
           "fist": "BRING HANDS TOGETHER FOR 3 SEC", "calib": "CALIBRATING",
           "track": "TRACKING - TOUCH LEFT FOOT TO RELEASE"},
    "zh-cn": {"wait": "等待目标 - 请站在相机前", "raise": "举起双手进行捕捉", "fist": "将双手合十保持3秒",
              "calib": "校准中", "track": "跟踪中 - 触摸左脚释放"},
    "zh-tw": {"wait": "等待目標 - 請站在相機前", "raise": "舉起雙手進行捕捉", "fist": "將雙手合十保持3秒",
              "calib": "校準中", "track": "跟蹤中 - 觸摸左腳釋放"},
    "he": {"wait": "ממתין לגוף - עמוד מול המצלמה", "raise": "הרים ידיים ללכידה", "fist": "הצמד את הידיים למשך 3 שניות",
           "calib": "מכייל", "track": "עוקב - גע ברגל שמאל לשחרור"},
    "el": {"wait": "ΑΝΑΜΟΝΗ - ΣΤΑΘΕΙΤΕ ΜΠΡΟΣΤΑ ΣΤΗΝ ΚΑΜΕΡΑ", "raise": "ΣΗΚΩΣΤΕ ΤΑ ΧΕΡΙΑ ΓΙΑ ΚΑΤΑΓΡΑΦΗ",
           "fist": "ΕΝΩΣΤΕ ΤΑ ΧΕΡΙΑ ΣΑΣ ΓΙΑ 3 ΔΕΥΤ.", "calib": "ΒΑΘΜΟΝΟΜΗΣΗ",
           "track": "ΠΑΡΑΚΟΛΟΥΘΗΣΗ - ΑΓΓΙΞΤΕ ΤΟ ΑΡΙΣΤΕΡΟ ΠΟΔΙ ΓΙΑ ΑΠΕΛΕΥΘΕΡΩΣΗ"},
    "hi": {"wait": "शरीर की प्रतीक्षा - कैमरे के सामने खड़े हों", "raise": "कैप्चर करने के लिए अपने हाथ उठाएं",
           "fist": "3 सेकंड के लिए दोनों हाथ एक साथ लाएं", "calib": "कैलिब्रेटिंग",
           "track": "ट्रैकिंग - छोड़ने के लिए बाएं पैर को छुएं"},
    "ms": {"wait": "MENUNGGU BADAN - BERDIRI DI HADAPAN KAMERA", "raise": "ANGKAT TANGAN ANDA UNTUK MENANGKAP",
           "fist": "RAPATKAN KEDUA TANGAN SELAMA 3 SAAT", "calib": "MENENTUKUR",
           "track": "MENJEJAK - SENTUH KAKI KIRI UNTUK MELEPASKAN"},
    "tl": {"wait": "NAGHIHINTAY - TUMAYO SA HARAP NG KAMERA", "raise": "ITAAS ANG IYONG MGA KAMAY",
           "fist": "PAGDIKITIN ANG MGA KAMAY NG 3 SEGUNDO", "calib": "NAGKA-CALIBRATE",
           "track": "TRACKING - HAWAKAN ANG KALIWANG PAA UPANG BITAWAN"},
    "ar": {"wait": "في انتظار الجسم - قف أمام الكاميرا", "raise": "ارفع يديك للالتقاط",
           "fist": "اجمع يديك معًا لمدة 3 ثوانٍ", "calib": "معايرة", "track": "تتبع - المس القدم اليسرى للتحرير"},
    "ko": {"wait": "대상 대기 중 - 카메라 앞에 서십시오", "raise": "손을 들어 캡처하십시오", "fist": "3초 동안 양손을 모으십시오", "calib": "보정 중",
           "track": "추적 중 - 왼쪽 발을 터치하여 해제"},
    "sw": {"wait": "KUSUBIRI MWILI - SIMAMA MBELE YA KAMERA", "raise": "INUA MIKONO YAKO ILI KUNASA",
           "fist": "WEKA MIKONO PAMOJA KWA SEKUNDE 3", "calib": "KUREKEBISHA",
           "track": "KUFUATILIA - GUSA MGUU WA KUSHOTO ILI KUACHIA"}
}


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

        self.force_release = False
        self.force_reset = False

        self.system_state = "ESPERANDO_BODY"
        self.target_body_id = None
        self.calibrated_refs = {}
        self.last_update_time = time.time()
        self.calibration_start_time = None
        self.current_matrix_text = ""

        # Variables para la animación de la Estrella
        self.star_animation_start = 0
        self.star_pos = (480, 270)

        self.servo_channels = {
            "MANO D": {"X": 0, "Y": 1},
            "MANO I": {"X": 2, "Y": 3},
            "PIE D": {"X": 4, "Y": 5},
            "PIE I": {"X": 6, "Y": 7},
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
        self._kinect = PyKinectRuntime.PyKinectRuntime(
            PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body)
        self._kinect.bodies = numpy.ndarray((6), dtype=object)

        print("Iniciando Arduino...")
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
        self.pca = PCA9685_Controller(self.board)

        self.set_matrix_text(self.gui.get_msg_ready(), 60)
        self.go_to_rest_pose()

    def set_matrix_text(self, text, scroll_speed=50):
        if text == self.current_matrix_text: return
        self.current_matrix_text = text
        text_clean = str(text).upper().strip()[:25]
        payload = [58, len(text_clean), scroll_speed] + [ord(c) for c in text_clean]
        if hasattr(self.board, '_send_command'):
            try:
                self.board._send_command(payload)
            except:
                pass

    def go_to_rest_pose(self):
        for part, channels in self.servo_channels.items():
            if "X" in channels: self.pca.set_angle(channels["X"], 90)
            if "Y" in channels:
                if part == "CABEZA":
                    self.pca.set_angle(channels["Y"], 90)
                else:
                    self.pca.set_angle(channels["Y"], 15)

    def map_to_servo(self, value, in_min, in_max):
        return int((value - in_min) * (180 - 0) / (in_max - in_min) + 0)

    def is_raising_hands(self, joints):
        head_y = joints[PyKinectV2.JointType_Head].Position.y
        return (joints[PyKinectV2.JointType_HandLeft].Position.y > head_y and
                joints[PyKinectV2.JointType_HandRight].Position.y > head_y)

    def is_touching_foot(self, joints):
        hand_l = joints[PyKinectV2.JointType_HandLeft].Position
        foot_l = joints[PyKinectV2.JointType_FootLeft].Position
        dist = np.sqrt((hand_l.x - foot_l.x) ** 2 + (hand_l.y - foot_l.y) ** 2 + (hand_l.z - foot_l.z) ** 2)
        return dist < 0.20

    def are_hands_together(self, joints):
        hand_l = joints[PyKinectV2.JointType_HandLeft].Position
        hand_r = joints[PyKinectV2.JointType_HandRight].Position
        dist = np.sqrt((hand_l.x - hand_r.x) ** 2 + (hand_l.y - hand_r.y) ** 2 + (hand_l.z - hand_r.z) ** 2)
        return dist < 0.15

    def get_color_joint_points(self, joints):
        joint_points = numpy.ndarray((PyKinectV2.JointType_Count), dtype=object)
        for j in range(0, PyKinectV2.JointType_Count):
            joint_points[j] = self._kinect._mapper.MapCameraPointToColorSpace(joints[j].Position)
        return joint_points

    def run(self):
        while self.running:
            lang_dict = LANGUAGES.get(self.gui.current_lang, LANGUAGES["en"])

            if self.force_reset:
                self.target_body_id = None
                self.system_state = "ESPERANDO_BODY"
                self.calibrated_refs = {}
                self.calibration_start_time = None
                self.go_to_rest_pose()
                self.force_reset = False

            if self.force_release:
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

                if self.gui.get_mirror(): img = cv2.flip(img, 1)
                alpha_cam = self.gui.get_contrast()
                beta_cam = self.gui.get_brightness()
                if alpha_cam != 1.0 or beta_cam != 0:
                    img = cv2.convertScaleAbs(img, alpha=alpha_cam, beta=beta_cam)
            else:
                img = np.zeros((540, 960, 3), np.uint8)

            if self._kinect.has_new_body_frame():
                self._bodies = self._kinect.get_last_body_frame()

            status_text = ""
            calib_progress = 0.0
            hands_joined = False  # Variable de estado para los colores

            if self._bodies is not None:
                any_body_tracked = any(self._bodies.bodies[i].is_tracked for i in range(self._kinect.max_body_count))

                if not any_body_tracked:
                    self.system_state = "ESPERANDO_BODY"
                    self.target_body_id = None
                    self.set_matrix_text(self.gui.get_msg_idle(), 50)
                    status_text = lang_dict["wait"]
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
                        status_text = lang_dict["raise"]

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
                        hands_joined = self.are_hands_together(joints)

                        connections = [(PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck),
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
                                       (PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)]
                        for j1, j2 in connections:
                            if joints[j1].TrackingState == PyKinectV2.TrackingState_Tracked and joints[
                                j2].TrackingState == PyKinectV2.TrackingState_Tracked:
                                px1, py1 = int(joint_points[j1].x * 960 / 1920), int(joint_points[j1].y * 540 / 1080)
                                px2, py2 = int(joint_points[j2].x * 960 / 1920), int(joint_points[j2].y * 540 / 1080)
                                if self.gui.get_mirror():
                                    px1, px2 = 960 - px1, 960 - px2
                                if not np.isinf(px1) and not np.isinf(px2):
                                    cv2.line(img, (px1, py1), (px2, py2), (255, 255, 0), 2)

                        # --- ESTADO 2: CALIBRACIÓN ---
                        if self.system_state == "ESPERANDO_CALIBRACION":
                            self.set_matrix_text(self.gui.get_msg_calib(), 40)

                            if hands_joined:
                                if self.calibration_start_time is None: self.calibration_start_time = time.time()
                                elapsed = time.time() - self.calibration_start_time
                                calib_progress = min(elapsed / 3.0, 1.0)
                                status_text = f"{lang_dict['calib']}: {int(calib_progress * 100)}%"

                                if elapsed >= 3.0:
                                    for nombre, jt_id in self.puntos.items():
                                        self.calibrated_refs[nombre] = {"x": joints[jt_id].Position.x,
                                                                        "y": joints[jt_id].Position.y}

                                    # Configurar animación de estrella en el centro de las manos
                                    jp_l = joint_points[PyKinectV2.JointType_HandLeft]
                                    jp_r = joint_points[PyKinectV2.JointType_HandRight]
                                    px_star = int(((jp_l.x + jp_r.x) / 2) * 960 / 1920)
                                    py_star = int(((jp_l.y + jp_r.y) / 2) * 540 / 1080)
                                    if self.gui.get_mirror(): px_star = 960 - px_star
                                    self.star_pos = (px_star, py_star)
                                    self.star_animation_start = time.time()

                                    self.go_to_rest_pose()
                                    self.system_state = "TRACKING"
                                    self.calibration_start_time = None
                                    time.sleep(0.5)
                            else:
                                self.calibration_start_time = None
                                status_text = lang_dict["fist"]

                        # --- ESTADO 3: TRACKING ---
                        elif self.system_state == "TRACKING":
                            self.set_matrix_text(self.gui.get_msg_track(), 50)
                            status_text = lang_dict["track"]

                            if self.is_touching_foot(joints):
                                self.force_release = True
                                continue

                            raw_sens = self.gui.get_sensibilidad()
                            raw_smooth = self.gui.get_smoothing()
                            update_delay = self.gui.get_update_speed()

                            rango_x = 0.8 - (raw_sens * 0.7)
                            alpha_ema = 1.0 - (raw_smooth * 0.95)

                            current_time = time.time()
                            if current_time - self.last_update_time > update_delay:
                                for nombre, jt_id in self.puntos.items():
                                    pos = joints[jt_id].Position
                                    ref = self.calibrated_refs[nombre]
                                    canales = self.servo_channels[nombre]

                                    if "X" in canales:
                                        ax = int((pos.x - (ref['x'] - rango_x)) * (0 - 180) / ((ref['x'] + rango_x) - (ref['x'] - rango_x)) + 180)
                                        self.pca.set_angle(canales["X"], ax, smoothing=alpha_ema)
                                    if "Y" in canales:
                                        if nombre == "CABEZA":
                                            pos_neck = joints[PyKinectV2.JointType_Neck].Position
                                            y_virt = pos.y - ((pos_neck.z - pos.z) * 1.5)
                                            ay = self.map_to_servo(y_virt, ref['y'] - (rango_x / 2),
                                                                   ref['y'] + (rango_x / 2))
                                        else:
                                            ay = self.map_to_servo(pos.y, ref['y'], ref['y'] + (rango_x * 1.5))
                                        self.pca.set_angle(canales["Y"], ay, smoothing=alpha_ema)
                                self.last_update_time = current_time

                        # TEXTOS FÍSICOS Y COLORES EN LA IMAGEN
                        for nombre, jt_id in self.puntos.items():
                            jp = joint_points[jt_id]
                            if not np.isinf(jp.x):
                                px, py = int(jp.x * 960 / 1920), int(jp.y * 540 / 1080)
                                if self.gui.get_mirror(): px = 960 - px

                                # Lógica de colores de las manos
                                if "MANO D" in nombre:
                                    dot_color = (0, 255, 0) if hands_joined else (255, 0, 255)  # Verde (Junto) o Magenta
                                elif "MANO I" in nombre:
                                    dot_color = (0, 255, 0) if hands_joined else (255, 255, 0)# Verde (Junto) o Cyan
                                elif "PIE D" in nombre:
                                    dot_color = (0,255, 0) if hands_joined else (0, 255, 255)
                                elif "PIE I" in nombre:
                                    dot_color = (0, 255, 0) if hands_joined else (0, 0,255)
                                elif "CABEZA" in nombre:
                                    dot_color = (0, 255, 0) if hands_joined else (255, 0, 0)
                                else:
                                    dot_color = (255, 255, 255)  # Blanco para Cabeza y Pies

                                cv2.circle(img, (px, py), 15, dot_color, -1)
                                cv2.circle(img, (px, py), 18, (255, 255, 255), 2)

                                if self.system_state == "TRACKING":
                                    pos = joints[jt_id].Position
                                    ref = self.calibrated_refs[nombre]
                                    canales = self.servo_channels[nombre]

                                    raw_sens = self.gui.get_sensibilidad()
                                    rango_x = 0.8 - (raw_sens * 0.7)

                                    txt_x = str(max(15, min(165, self.map_to_servo(pos.x, ref['x'] - rango_x, ref[
                                        'x'] + rango_x)))) if "X" in canales else "--"
                                    if nombre == "CABEZA":
                                        pos_neck = joints[PyKinectV2.JointType_Neck].Position
                                        y_virt = pos.y - ((pos_neck.z - pos.z) * 1.5)
                                        txt_y = str(max(15, min(165, self.map_to_servo(y_virt, ref['y'] - (rango_x / 2),
                                                                                       ref['y'] + (rango_x / 2)))))
                                    else:
                                        txt_y = str(max(15, min(165, self.map_to_servo(pos.y, ref['y'], ref['y'] + (
                                                    rango_x * 1.5))))) if "Y" in canales else "--"

                                    cv2.putText(img, f"{nombre}: X{txt_x} Y{txt_y}", (px + 20, py),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # --- RENDERIZAR ESTRELLA DE MARIO (FADE OUT) ---
            if self.star_animation_start > 0:
                elapsed_star = time.time() - self.star_animation_start
                fade_duration = 1.5  # La animación dura 1.5 segundos

                if elapsed_star < fade_duration:
                    # Calcula la opacidad (empieza en 1.0, termina en 0.0)
                    alpha = max(0.0, 1.0 - (elapsed_star / fade_duration))

                    # La estrella crece mientras gira
                    r_out = 80 + (elapsed_star * 60)
                    r_in = r_out * 0.4
                    angle_offset = elapsed_star * 5  # Velocidad de giro

                    overlay = img.copy()
                    pts = []
                    # Generar los 10 picos de la estrella
                    for i in range(10):
                        angle = i * math.pi / 5 - math.pi / 2 + angle_offset
                        r = r_out if i % 2 == 0 else r_in
                        pts.append(
                            [int(self.star_pos[0] + math.cos(angle) * r), int(self.star_pos[1] + math.sin(angle) * r)])

                    pts = np.array([pts], dtype=np.int32)

                    # Rellenar de amarillo BGR(0, 215, 255) y borde blanco
                    cv2.fillPoly(overlay, pts, (0, 215, 255))
                    cv2.polylines(overlay, pts, True, (255, 255, 255), 4)

                    # Mezclar la capa con el nivel de transparencia actual (Fade Out)
                    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
                else:
                    self.star_animation_start = 0

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
        self.title("Arabots Puppet Master - International Competition Edition")
        self.geometry("1200x800")

        self.current_lang = "es"
        self.video_size = (960, 540)

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        self.sidebar = ctk.CTkScrollableFrame(self.main_container, width=120, corner_radius=10)
        self.sidebar.pack(side="right", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="LANGUAGE", font=("Arial", 12, "bold")).pack(pady=10)

        countries = [
            ("🇲🇽 MEX", "es"), ("🇺🇸 USA", "en"), ("🇨🇳 CHN", "zh-cn"), ("🇹🇼 TWN", "zh-tw"),
            ("🇮🇱 ISR", "he"), ("🇬🇷 GRE", "el"), ("🇮🇳 IND", "hi"), ("🇲🇾 MYS", "ms"),
            ("🇵🇭 PHL", "tl"), ("🇶🇦 QAT", "ar"), ("🇩🇿 ALG", "ar"), ("🇸🇦 KSA", "ar"),
            ("🇪🇬 EGY", "ar"), ("🇰🇷 KOR", "ko"), ("🇰🇪 KEN", "sw")
        ]

        for flag_text, lang_code in countries:
            btn = ctk.CTkButton(self.sidebar, text=flag_text, font=("Arial", 16),
                                fg_color="#374151", hover_color="#2563EB",
                                command=lambda c=lang_code: self.change_language(c))
            btn.pack(pady=5, padx=5, fill="x")

        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(side="left", padx=10, pady=10, expand=True, fill="both")

        self.tab_monitor = self.tabview.add("Monitor Principal")
        self.tab_settings = self.tabview.add("Ajustes y Calibración")

        # --- TAB 1: MONITOR ---
        self.video_label = ctk.CTkLabel(self.tab_monitor, text="Iniciando Cámara Kinect...")
        self.video_label.pack(padx=5, pady=5, expand=True, fill="both")
        self.video_label.bind("<Configure>", self.on_video_resize)

        self.status_frame = ctk.CTkFrame(self.tab_monitor, fg_color="#1F2937", corner_radius=10, height=50)
        self.status_frame.pack_propagate(False)
        self.status_frame.pack(fill="x", padx=10, pady=5)

        # TEXTO CENTRADO ABSOLUTO
        self.status_label = ctk.CTkLabel(self.status_frame, text="INICIANDO...", font=("Arial", 18, "bold"),
                                         text_color="#38BDF8")
        self.status_label.place(relx=0.5, rely=0.5, anchor="center")

        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=200, progress_color="#22C55E",
                                               fg_color="#374151")
        self.progress_bar.set(0)
        self.progress_bar.pack(side="right", padx=20, pady=10)
        self.progress_bar.pack_forget()

        self.action_frame = ctk.CTkFrame(self.tab_monitor, fg_color="transparent")
        self.action_frame.pack(fill="x", padx=10, pady=5)

        self.btn_release = ctk.CTkButton(self.action_frame, text="Soltar Objetivo / Release",
                                         fg_color="#F59E0B", hover_color="#D97706",
                                         font=("Arial", 14, "bold"), height=40,
                                         command=self.cmd_release)
        self.btn_release.pack(side="left", padx=10, expand=True, fill="x")

        self.btn_reset = ctk.CTkButton(self.action_frame, text="Reinicio Total / Hard Reset",
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
        self.entry_calib.insert(0, "JUNTAR")
        self.add_labeled_widget(frame_msg, "Mensaje Calibrando:", self.entry_calib)

        self.entry_track = ctk.CTkEntry(frame_msg, width=300)
        self.entry_track.insert(0, "TRACKING")
        self.add_labeled_widget(frame_msg, "Mensaje Tracking:", self.entry_track)

        frame_mot = ctk.CTkFrame(self.tab_settings)
        frame_mot.pack(padx=20, pady=10, fill="x")
        ctk.CTkLabel(frame_mot, text="Física de los Motores", font=("Arial", 16, "bold")).pack(pady=5)

        self.slider_sens = ctk.CTkSlider(frame_mot, from_=0.0, to=1.0, width=300)
        self.slider_sens.set(0.5)
        self.add_labeled_widget(frame_mot, "Sensibilidad (1.0 = Máxima, se mueve con 10cm):", self.slider_sens)

        self.slider_smooth = ctk.CTkSlider(frame_mot, from_=0.0, to=1.0, width=300)
        self.slider_smooth.set(0.5)
        self.add_labeled_widget(frame_mot, "Suavizado (1.0 = Máximo efecto gelatina):", self.slider_smooth)

        self.slider_speed = ctk.CTkSlider(frame_mot, from_=0.03, to=0.2, width=300)
        self.slider_speed.set(0.1)
        self.add_labeled_widget(frame_mot, "Delay de I2C (Velocidad de señal):", self.slider_speed)

        self.latest_frame = None
        self.backend = ArabotsCore(self)
        self.backend.start()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_video_resize(self, event):
        w, h = event.width, event.height
        if w > 20 and h > 20:
            target_ratio = 16 / 9
            current_ratio = w / h
            if current_ratio > target_ratio:
                new_h = h
                new_w = int(h * target_ratio)
            else:
                new_w = w
                new_h = int(w / target_ratio)
            self.video_size = (new_w, new_h)

    def change_language(self, lang_code):
        self.current_lang = lang_code

    def add_labeled_widget(self, parent, text, widget):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(container, text=text, width=200, anchor="w").pack(side="left")
        widget.pack(side="left", padx=10)

    def cmd_release(self):
        if hasattr(self, 'backend'): self.backend.force_release = True

    def cmd_reset(self):
        if hasattr(self, 'backend'): self.backend.force_reset = True

    def get_msg_idle(self):
        return self.entry_idle.get()

    def get_msg_ready(self):
        return self.entry_ready.get()

    def get_msg_calib(self):
        return self.entry_calib.get()

    def get_msg_track(self):
        return self.entry_track.get()

    def get_sensibilidad(self):
        return self.slider_sens.get()

    def get_smoothing(self):
        return self.slider_smooth.get()

    def get_update_speed(self):
        return self.slider_speed.get()

    def get_mirror(self):
        return self.switch_mirror.get() == 1

    def get_brightness(self):
        return int(self.slider_bright.get())

    def get_contrast(self):
        return self.slider_contrast.get()

    def push_frame_and_status(self, cv_img, status_text, calib_progress):
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)

        self.latest_frame = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=self.video_size)
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