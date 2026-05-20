import cv2
import numpy as np
from ultralytics import RTDETR
import win32com.client
import threading
import time


def hablar_nativo(texto):
    def proceso():
        try:
            import pythoncom
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(texto)
        except:
            pass

    threading.Thread(target=proceso, daemon=True).start()


class RobotVisionSeptuple:
    def __init__(self, model_path):
        self.frame_ia = None
        self.anotaciones = None
        self.corriendo = True
        self.model = RTDETR(model_path)
        self.ultimo_ganador_anunciado = None

        # ÁNGULOS Y PERSPECTIVA
        self.angulos = [0, 10, -10, 20, -20, 45, -45]
        self.clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

        # --- OPCIÓN DE CALIBRACIÓN RESTAURADA ---
        # Cambia el valor de cada una según necesites en la pista
        self.UMBRAL_GENERAL = 0.91
        self.CONF_POR_CLASE = {
            'Stop': 0.8,
            'Yield': 0.7,
            'Do Not Enter': 0.91,
            'No Left Turn': 0.91,
            'No Right Turn': 0.93,
            'No U Turn': 0.91,
            'Left Turn Only': 0.75,
            'Right Turn Only': 0.75,
            'Straight or Left Turn Only': 0.91,
            'Straight or Right Turn Only': 0.91,
            'One Way Left': 0.6,
            'One Way Right': 0.6,
            'Left Curve Ahead': 0.91,
            'Right Curve Ahead': 0.91,
            'No Parking Left Arrow': 0.91,
            'No Parking No Arrow': 0.91,
            'No Parking Double Arrow': 0.91,
            'Pedestrian Crossing': 0.85,
            'School Crossing': 0.91,
            'Speed Limit 25mph': 0.7,
            'Be Prepared to Stop': 0.91,
            'Left Turn Yield on Green': 0.89,
            'No Turn on Red': 0.85,
            'When Flashing': 0.7
        }

    def obtener_umbral(self, label):
        return self.CONF_POR_CLASE.get(label, self.UMBRAL_GENERAL)

    def preprocesar_frame(self, img, target_size=(800, 800)):
        h, w = img.shape[:2]
        r = min(target_size[0] / w, target_size[1] / h)
        new_w, new_h = int(w * r), int(h * r)
        resized = cv2.resize(img, (new_w, new_h))
        canvas = np.full((target_size[1], target_size[0], 3), 114, dtype=np.uint8)
        canvas[(target_size[1] - new_h) // 2:(target_size[1] - new_h) // 2 + new_h,
        (target_size[0] - new_w) // 2:(target_size[0] - new_w) // 2 + new_w] = resized
        return canvas

    def correccion_perspectiva_agresiva(self, image, fov_deg):
        h, w = image.shape[:2]
        offset = int(w * (fov_deg / 100))
        pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        pts2 = np.float32([[offset, 0], [w - offset, 0], [-offset, h], [w + offset, h]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(image, M, (w, h), borderValue=(114, 114, 114))

    def rotar_imagen(self, image, angle):
        if angle == 0: return image
        h, w = image.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        return cv2.warpAffine(image, M, (w, h), borderValue=(114, 114, 114))

    def hilo_ia(self):
        while self.corriendo:
            if self.frame_ia is None:
                time.sleep(0.01)
                continue

            lab = cv2.cvtColor(self.frame_ia, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l = self.clahe.apply(l)
            frame_limpio = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

            frame_prep = self.preprocesar_frame(frame_limpio)

            frames_batch = []
            for a in self.angulos:
                frames_batch.append(self.rotar_imagen(frame_prep, a))
            for p in [15, -15, 30, -30, 45, -45]:
                frames_batch.append(self.correccion_perspectiva_agresiva(frame_prep, p))

            try:
                results = self.model(frames_batch, conf=0.01, verbose=False, imgsz=800)
            except:
                continue

            annotated_frame = self.frame_ia.copy()
            max_conf_frame = -1.0
            ganador_nombre = None

            for res in results:
                if res.boxes is not None:
                    for box in res.boxes:
                        label = self.model.names[int(box.cls[0])]
                        conf = float(box.conf[0])

                        # USAR EL UMBRAL ESPECÍFICO CALIBRADO
                        if conf < self.obtener_umbral(label): continue

                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        # Mapeo a resolución 720p
                        x1, x2 = int(x1 * 1280 / 800), int(x2 * 1280 / 800)
                        y1, y2 = int(y1 * 720 / 800), int(y2 * 720 / 800)

                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 6)
                        cv2.putText(annotated_frame, f"{label} {int(conf * 100)}%", (x1, y1 - 25),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 4)

                        if conf > max_conf_frame:
                            max_conf_frame = conf
                            ganador_nombre = label

            if ganador_nombre is None:
                self.ultimo_ganador_anunciado = None
            elif ganador_nombre != self.ultimo_ganador_anunciado:
                p = int(max_conf_frame * 100)
                print(f"🏆 GANADOR CALIBRADO: {ganador_nombre} ({p}%)")
                hablar_nativo(f"Atención: {ganador_nombre}")
                self.ultimo_ganador_anunciado = ganador_nombre

            self.anotaciones = annotated_frame
            time.sleep(0.005)


if __name__ == "__main__":
    ruta_engine = r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Arabots_RTDETR_2026\RTDETR_L_Novi_V1\weights\best.engine"
    robot = RobotVisionSeptuple(ruta_engine)
    threading.Thread(target=robot.hilo_ia, daemon=True).start()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_EXPOSURE, -7)

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break
        robot.frame_ia = frame
        display = robot.anotaciones if robot.anotaciones is not None else frame
        cv2.imshow("ARABOTS 2026 - CALIBRACION ACTIVA", display)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            robot.corriendo = False
            break
    cap.release()
    cv2.destroyAllWindows()