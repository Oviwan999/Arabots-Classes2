import cv2
from ultralytics import YOLO
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


class RobotVision:
    def __init__(self, model_path):
        self.frame_ia = None
        self.anotaciones = None
        self.corriendo = True

        self.model = YOLO(model_path)

        # Clases que se detectaron en el frame anterior
        self.labels_anteriores = set()

        # Umbral general para clases no personalizadas
        self.CONF_GENERAL = 0.80

        # Umbral por clase
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
                time.sleep(0.03)
                continue

            frame_copy = self.frame_ia.copy()

            try:
                # Lo dejamos bajo y nosotros filtramos manualmente
                results = self.model(frame_copy, conf=0.01, verbose=False)
            except Exception as e:
                print("Error en inferencia:", e)
                time.sleep(0.1)
                continue

            annotated_frame = frame_copy.copy()
            labels_actuales = set()
            mensajes_nuevos = []

            if results and len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    try:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        label = self.model.names[cls_id]

                        umbral = self.obtener_umbral(label)
                        if conf < umbral:
                            continue

                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        # Dibujar
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

                        labels_actuales.add(label)

                    except Exception as e:
                        print("Error procesando box:", e)

            # Solo hablar de las etiquetas que NO estaban en el frame anterior
            labels_recién_aparecidas = labels_actuales - self.labels_anteriores

            if labels_recién_aparecidas:
                # Buscar una confianza representativa para cada label nueva
                for box in results[0].boxes:
                    try:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        label = self.model.names[cls_id]

                        umbral = self.obtener_umbral(label)
                        if conf < umbral:
                            continue

                        if label in labels_recién_aparecidas:
                            mensajes_nuevos.append(f"{label} al {int(conf * 100)} por ciento")
                            labels_recién_aparecidas.remove(label)

                        if not labels_recién_aparecidas:
                            break

                    except:
                        pass

            self.anotaciones = annotated_frame

            if mensajes_nuevos:
                mensaje_final = "Atención: " + ", ".join(mensajes_nuevos)
                print(mensaje_final)
                hablar_nativo(mensaje_final)

            # Guardar lo que sí se detectó en este frame
            self.labels_anteriores = labels_actuales

            time.sleep(0.05)


if __name__ == "__main__":
    ruta_modelo = r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Arabots_RTDETR_2026\RTDETR_L_Novi_V1\weights\best.pt"

    robot = RobotVision(ruta_modelo)
    threading.Thread(target=robot.hilo_ia, daemon=True).start()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        robot.frame_ia = frame
        display_frame = robot.anotaciones if robot.anotaciones is not None else frame

        cv2.imshow("Arabots 2026 - PT con voz", display_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            robot.corriendo = False
            break

    cap.release()
    cv2.destroyAllWindows()