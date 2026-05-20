import cv2
import numpy as np
from ultralytics import RTDETR
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


class RobotVisionFinal:
    def __init__(self, model_path):
        self.frame_ia = None
        self.anotaciones = None
        self.corriendo = True

        print(f"🚀 Cargando Engine Final - Triple Escaneo y Texto Gigante...")
        self.model = RTDETR(model_path)

        self.labels_anteriores = set()
        self.CONF_GENERAL = 0.80

        # Umbrales personalizados
        self.CONF_POR_CLASE = {
            'Stop': 0.7,
            'Yield': 0.87,
            'Do Not Enter': 0.7,
            'Pedestrian Crossing': 0.87
            # Agrega más aquí si es necesario
        }

    def obtener_umbral(self, label):
        return self.CONF_POR_CLASE.get(label, self.CONF_GENERAL)

    def rotar_imagen(self, image, angle):
        """Rota la imagen para compensar inclinaciones en curvas."""
        h, w = image.shape[:2]
        centro = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(centro, angle, 1.0)
        return cv2.warpAffine(image, M, (w, h))

    def hilo_ia(self):
        while self.corriendo:
            if self.frame_ia is None:
                time.sleep(0.01)
                continue

            frame_copy = self.frame_ia.copy()

            # BATCH DE ESCANEO: Original, +15° y -15° (Sin espejos/flips)
            frames_batch = [
                frame_copy,
                self.rotar_imagen(frame_copy, 15),
                self.rotar_imagen(frame_copy, -15)
            ]

            try:
                # Inferencia en batch para maximizar la 2060/4060
                results = self.model(frames_batch, conf=0.01, verbose=False, imgsz=800)
            except Exception as e:
                print(f"Error en Batch Engine: {e}")
                continue

            annotated_frame = frame_copy.copy()
            labels_actuales = set()
            mensajes_nuevos = []

            # Procesar los resultados de los 3 ángulos
            for res in results:
                if res.boxes is not None:
                    for box in res.boxes:
                        try:
                            cls_id = int(box.cls[0])
                            conf = float(box.conf[0])
                            label = self.model.names[cls_id]

                            if conf < self.obtener_umbral(label):
                                continue

                            x1, y1, x2, y2 = map(int, box.xyxy[0])

                            # Evitar duplicados en el set de voz
                            labels_actuales.add(label)

                            # --- DIBUJO CON TEXTO TRIPLE (GIGANTE) ---
                            # Cuadro más grueso (Grosor 6)
                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 6)

                            # Texto gigante (Escala 1.8, Grosor 4)
                            texto_pantalla = f"{label} {int(conf * 100)}%"
                            cv2.putText(
                                annotated_frame,
                                texto_pantalla,
                                (x1, y1 - 20),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1.8,  # Texto casi al triple
                                (0, 255, 0),
                                4  # Grosor de letra aumentado
                            )
                        except:
                            continue

            # LÓGICA DE VOZ CON PORCENTAJE
            labels_recien_aparecidas = labels_actuales - self.labels_anteriores
            if labels_recien_aparecidas:
                # Buscamos la mejor confianza en el batch para la voz
                for label in list(labels_recien_aparecidas):
                    best_conf = 0
                    for res_v in results:
                        for b_v in res_v.boxes:
                            if self.model.names[int(b_v.cls[0])] == label:
                                best_conf = max(best_conf, float(b_v.conf[0]))

                    if best_conf >= self.obtener_umbral(label):
                        mensajes_nuevos.append(f"{label} al {int(best_conf * 100)} por ciento")

            self.anotaciones = annotated_frame

            if mensajes_nuevos:
                mensaje_final = "Atención: " + ", ".join(mensajes_nuevos)
                print(mensaje_final)
                hablar_nativo(mensaje_final)

            self.labels_anteriores = labels_actuales
            time.sleep(0.01)


if __name__ == "__main__":
    # RUTA AL ENGINE COMPILADO
    ruta_engine = r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Arabots_RTDETR_2026\RTDETR_L_Novi_V1\weights\best.engine"

    robot = RobotVisionFinal(ruta_engine)
    threading.Thread(target=robot.hilo_ia, daemon=True).start()

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    # Resolución HD para que el texto grande tenga espacio
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("🏁 Iniciando Arabots Engine Final - Modo Texto Gigante y Anti-Rotación")

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        robot.frame_ia = frame
        display = robot.anotaciones if robot.anotaciones is not None else frame

        cv2.imshow("ARABOTS 2026 - TENSORRT GIGANTE", display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            robot.corriendo = False
            break

    cap.release()
    cv2.destroyAllWindows()