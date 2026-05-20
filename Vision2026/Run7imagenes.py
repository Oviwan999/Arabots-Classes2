import cv2
import numpy as np
from ultralytics import RTDETR
import win32com.client
import threading
import time


def hablar_nativo(texto):
    """Voz asíncrona para evitar tirones en el video."""

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

        # CARGA DEL MOTOR (Engine Batch=7)
        print(f"🚀 Iniciando Visión Arabots: Filtro de Persistencia Activo...")
        self.model = RTDETR(model_path)

        # --- MEMORIA DE SEÑALES (CERROJO DE VOZ) ---
        self.labels_anteriores = set()

        # 7 Ángulos para cubrir rotaciones en curvas
        self.angulos = [0, 15, 70, 90, -15, -70, -90]

        self.CONF_GENERAL = 0.80

        # --- TUS 24 CLASES Y UMBRALES ORIGINALES ---
        self.CONF_POR_CLASE = {
            'Stop': 0.93, 'Yield': 0.89, 'Do Not Enter': 0.93, 'No Left Turn': 0.95,
            'No Right Turn': 0.95, 'No U Turn': 0.95, 'Left Turn Only': 0.9,
            'Right Turn Only': 0.9, 'Straight or Left Turn Only': 0.93,
            'Straight or Right Turn Only': 0.93, 'One Way Left': 0.9,
            'One Way Right': 0.9, 'Left Curve Ahead': 0.93, 'Right Curve Ahead': 0.93,
            'No Parking Left Arrow': 0.93, 'No Parking No Arrow': 0.93,
            'No Parking Double Arrow': 0.93, 'Pedestrian Crossing': 0.9,
            'School Crossing': 0.9, 'Speed Limit 25mph': 0.9, 'Be Prepared to Stop': 0.9,
            'Left Turn Yield on Green': 0.85, 'No Turn on Red': 0.85, 'When Flashing': 0.9
        }

    def obtener_umbral(self, label):
        return self.CONF_POR_CLASE.get(label, self.CONF_GENERAL)

    def rotar_imagen(self, image, angle):
        if angle == 0: return image
        h, w = image.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        return cv2.warpAffine(image, M, (w, h))

    def hilo_ia(self):
        while self.corriendo:
            if self.frame_ia is None:
                time.sleep(0.01)
                continue

            frame_copy = self.frame_ia.copy()
            # Creamos las 7 versiones para el Batch
            frames_batch = [self.rotar_imagen(frame_copy, a) for a in self.angulos]

            try:
                # Inferencia Batch=7
                results = self.model(frames_batch, conf=0.01, verbose=False, imgsz=800)
            except Exception as e:
                print(f"❌ Error Engine: {e}")
                continue

            annotated_frame = frame_copy.copy()
            labels_detectados_ahora = set()
            max_conf_encontrada = {}

            # 1. ESCANEO DE RESULTADOS (De los 7 frames)
            for res in results:
                if res.boxes is not None:
                    for box in res.boxes:
                        try:
                            cls_id = int(box.cls[0])
                            conf = float(box.conf[0])
                            label = self.model.names[cls_id]

                            if conf < self.obtener_umbral(label):
                                continue

                            # Lo agregamos al set de lo que se está viendo "en este instante"
                            labels_detectados_ahora.add(label)

                            # Guardamos la mejor confianza para el reporte de voz
                            if label not in max_conf_encontrada or conf > max_conf_encontrada[label]:
                                max_conf_encontrada[label] = conf

                            # --- DIBUJO GIGANTE ---
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 6)
                            cv2.putText(annotated_frame, f"{label} {int(conf * 100)}%", (x1, y1 - 25),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 4)
                        except:
                            continue

            # 2. LÓGICA DE FILTRADO (LA CLAVE)
            # Calculamos qué señales son REALMENTE nuevas comparadas con el frame anterior
            nuevas_apariciones = labels_detectados_ahora - self.labels_anteriores

            if nuevas_apariciones:
                mensajes_voz = []
                for lab in nuevas_apariciones:
                    p = int(max_conf_encontrada[lab] * 100)
                    mensajes_voz.append(f"{lab} al {p} por ciento")

                aviso = "Atención: " + ", ".join(mensajes_voz)
                print(aviso)
                hablar_nativo(aviso)

            # 3. ACTUALIZAR ESTADO PARA EL SIGUIENTE CICLO
            # Si una señal sigue estando presente, se queda en labels_anteriores
            # Si desaparece, se borra de labels_anteriores y podrá ser anunciada de nuevo
            self.labels_anteriores = labels_detectados_ahora

            self.anotaciones = annotated_frame
            time.sleep(0.005)


if __name__ == "__main__":
    # Asegúrate de que este sea tu engine Batch=7
    ruta_engine = r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Arabots_RTDETR_2026\RTDETR_L_Novi_V1\weights\best.engine"

    robot = RobotVisionSeptuple(ruta_engine)
    threading.Thread(target=robot.hilo_ia, daemon=True).start()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break
        robot.frame_ia = frame
        display = robot.anotaciones if robot.anotaciones is not None else frame
        cv2.imshow("ARABOTS 2026 - TENSORRT FILTRADO", display)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            robot.corriendo = False
            break

    cap.release()
    cv2.destroyAllWindows()