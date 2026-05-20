import cv2
import threading
import time
import os
import win32com.client
from ultralytics import RTDETR


def hablar_nativo(texto):
    def proceso():
        try:
            import pythoncom
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(texto)
        except Exception as e:
            print("Error en voz:", e)

    threading.Thread(target=proceso, daemon=True).start()


class RobotVision:
    def __init__(self, model_path):
        self.frame_ia = None
        self.anotaciones = None
        self.corriendo = True
        self.labels_anteriores = set()

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"No se encontró el modelo: {model_path}")

        print("Cargando RT-DETR TensorRT Engine...")
        print(model_path)

        # IMPORTANTE: para RT-DETR usamos RTDETR, no YOLO
        self.model = RTDETR(model_path)

        print("Modelo cargado correctamente.")
        print("Clases del modelo:")
        print(self.model.names)

        self.CONF_GENERAL = 0.80

        self.CONF_POR_CLASE = {
            'Stop': 0.70,
            'Yield': 0.87,
            'Do Not Enter': 0.70,
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

    def obtener_nombre_clase(self, cls_id):
        """
        Evita el error:
        Error procesando box: 54
        Error procesando box: 131
        Error procesando box: 295

        Si el modelo devuelve un ID de clase que no existe,
        simplemente lo ignora.
        """

        names = self.model.names

        if isinstance(names, dict):
            if cls_id in names:
                return names[cls_id]
            return None

        if isinstance(names, list):
            if 0 <= cls_id < len(names):
                return names[cls_id]
            return None

        return None

    def obtener_umbral(self, label):
        return self.CONF_POR_CLASE.get(label, self.CONF_GENERAL)

    def hilo_ia(self):
        while self.corriendo:
            if self.frame_ia is None:
                time.sleep(0.03)
                continue

            frame_copy = self.frame_ia.copy()

            try:
                results = self.model.predict(
                    source=frame_copy,
                    conf=0.01,
                    verbose=False
                )
            except Exception as e:
                print("Error en inferencia:", e)
                time.sleep(0.1)
                continue

            annotated_frame = frame_copy.copy()
            labels_actuales = set()
            mensajes_nuevos = []

            if not results or len(results) == 0:
                self.anotaciones = annotated_frame
                continue

            r = results[0]

            if r.boxes is not None and len(r.boxes) > 0:
                for box in r.boxes:
                    try:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])

                        label = self.obtener_nombre_clase(cls_id)

                        # Si el ID de clase no existe, lo ignoramos
                        if label is None:
                            continue

                        umbral = self.obtener_umbral(label)

                        if conf < umbral:
                            continue

                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        cv2.rectangle(
                            annotated_frame,
                            (x1, y1),
                            (x2, y2),
                            (0, 255, 0),
                            2
                        )

                        cv2.putText(
                            annotated_frame,
                            f"{label} {int(conf * 100)}%",
                            (x1, max(y1 - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (0, 255, 0),
                            2
                        )

                        labels_actuales.add(label)

                    except Exception as e:
                        print("Error procesando box:", e)

            labels_recien_aparecidas = labels_actuales - self.labels_anteriores

            if labels_recien_aparecidas:
                for label in labels_recien_aparecidas:
                    mensajes_nuevos.append(label)

            self.anotaciones = annotated_frame

            if mensajes_nuevos:
                mensaje_final = "Atención: " + ", ".join(mensajes_nuevos)
                print(mensaje_final)
                hablar_nativo(mensaje_final)

            self.labels_anteriores = labels_actuales

            time.sleep(0.03)


if __name__ == "__main__":
    ruta_modelo = r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Arabots_RTDETR_2026\RTDETR_L_Novi_V1\weights\best.engine"

    try:
        robot = RobotVision(ruta_modelo)
    except Exception as e:
        print("No se pudo cargar el modelo:")
        print(e)
        input("Presiona ENTER para salir...")
        exit()

    threading.Thread(target=robot.hilo_ia, daemon=True).start()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        robot.corriendo = False
        input("Presiona ENTER para salir...")
        exit()

    print("Cámara iniciada.")
    print("Presiona Q para salir.")

    while True:
        success, frame = cap.read()

        if not success:
            print("No se pudo leer la cámara.")
            break

        robot.frame_ia = frame

        if robot.anotaciones is not None:
            display_frame = robot.anotaciones
        else:
            display_frame = frame

        cv2.imshow("Arabots 2026 - RTDETR Engine", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            robot.corriendo = False
            break

    robot.corriendo = False
    cap.release()
    cv2.destroyAllWindows()