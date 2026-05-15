import cv2
from ultralytics import RTDETR  # Clase específica para RT-DETR
import win32com.client
import threading
import time


def hablar_nativo(texto):
    """Función asíncrona para que el habla no bloquee el hilo de la IA."""

    def proceso():
        try:
            import pythoncom
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(texto)
        except:
            pass

    threading.Thread(target=proceso, daemon=True).start()


class RobotVision:
    def __init__(self, model_path):
        self.frame_ia = None
        self.anotaciones = None
        self.corriendo = True

        # CARGA DEL MOTOR TENSORRT (imgsz=800)
        print(f"🚀 Cargando Motor TensorRT: {model_path}...")
        self.model = RTDETR(model_path)

        # Memoria de detecciones para evitar repeticiones
        self.labels_anteriores = set()

        # Umbral por defecto
        self.CONF_GENERAL = 0.80

        # Diccionario de confianza personalizado (Arabots 2026)
        self.CONF_POR_CLASE = {
            'Stop': 0.7,
            'Yield': 0.87,
            'Do Not Enter': 0.7,
            'No Left Turn': 0.87,
            'No Right Turn': 0.87,
            'No U Turn': 0.87,
            'Left Turn Only': 0.87,
            'Right Turn Only': 0.87,
            'Straight or Left Turn Only': 0.87,
            'Straight or Right Turn Only': 0.87,
            'One Way Left': 0.87,
            'One Way Right': 0.87,
            'Left Curve Ahead': 0.87,
            'Right Curve Ahead': 0.87,
            'No Parking Left Arrow': 0.87,
            'No Parking No Arrow': 0.87,
            'No Parking Double Arrow': 0.87,
            'Pedestrian Crossing': 0.87,
            'School Crossing': 0.87,
            'Speed Limit 25mph': 0.87,
            'Be Prepared to Stop': 0.87,
            'Left Turn Yield on Green': 0.87,
            'No Turn on Red': 0.87,
            'When Flashing': 0.87
        }

    def obtener_umbral(self, label):
        return self.CONF_POR_CLASE.get(label, self.CONF_GENERAL)

    def hilo_ia(self):
        while self.corriendo:
            if self.frame_ia is None:
                time.sleep(0.01)
                continue

            frame_copy = self.frame_ia.copy()

            try:
                # INFERENCIA: imgsz debe ser 800 para coincidir con tu exportación
                results = self.model(frame_copy, conf=0.01, verbose=False, imgsz=800)
            except Exception as e:
                print(f"⚠️ Error en Engine: {e}")
                continue

            annotated_frame = frame_copy.copy()
            labels_actuales = set()
            mensajes_nuevos = []

            if results and len(results) > 0 and results[0].boxes is not None:
                for box in results[0].boxes:
                    try:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        label = self.model.names[cls_id]

                        umbral = self.obtener_umbral(label)
                        if conf < umbral:
                            continue

                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        labels_actuales.add(label)

                        # Dibujo en pantalla
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            annotated_frame,
                            f"{label} {int(conf * 100)}%",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2
                        )
                    except:
                        continue

            # LÓGICA DE VOZ CON PORCENTAJE
            labels_recien_aparecidas = labels_actuales - self.labels_anteriores

            if labels_recien_aparecidas:
                for box in results[0].boxes:
                    try:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        label = self.model.names[cls_id]

                        if label in labels_recien_aparecidas and conf >= self.obtener_umbral(label):
                            porcentaje = int(conf * 100)
                            mensajes_nuevos.append(f"{label} al {porcentaje} por ciento")
                            labels_recien_aparecidas.remove(label)

                        if not labels_recien_aparecidas:
                            break
                    except:
                        pass

            self.anotaciones = annotated_frame

            if mensajes_nuevos:
                mensaje_final = "Atención: " + ", ".join(mensajes_nuevos)
                print(mensaje_final)
                hablar_nativo(mensaje_final)

            self.labels_anteriores = labels_actuales
            time.sleep(0.01)  # Latencia mínima para aprovechar TensorRT


if __name__ == "__main__":
    # RUTA AL ARCHIVO .ENGINE GENERADO EN TU 2060
    ruta_engine = r"D:\pythonProject\Arabots-Classes2\Vision 2026\bestrgen.engine"

    robot = RobotVision(ruta_engine)
    threading.Thread(target=robot.hilo_ia, daemon=True).start()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    # Ajustamos resolución de cámara a la que prefieras (ej. 720p)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("🏁 Sistema Arabots activo. Presiona 'q' para cerrar.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        robot.frame_ia = frame

        # Mostrar anotaciones de la IA o el frame limpio
        display_frame = robot.anotaciones if robot.anotaciones is not None else frame

        cv2.imshow("Arabots 2026 - TensorRT Engine", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            robot.corriendo = False
            break

    cap.release()
    cv2.destroyAllWindows()