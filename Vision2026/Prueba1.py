import cv2
from ultralytics import YOLO
import win32com.client
import threading
import time


# --- 1. FUNCIÓN DE VOZ NATIVA ---
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


# --- 2. CLASE DE CONTROL DE ESTADOS ---
class RobotVision:
    def __init__(self):
        self.frame_ia = None
        self.anotaciones = None
        self.corriendo = True
        # Aquí guardamos lo que había en la toma anterior
        self.memoria_ultima_toma = set()

    def hilo_ia(self):
        # Cargamos el modelo una sola vez
        model = YOLO(r'C:\git\Arabots-Classes2\Vision2026\runs\detect\Vision2026_v210\weights\best.pt') #modelo creado por ustedes

        while self.corriendo:
            if self.frame_ia is not None:
                # Copiamos el frame para que la cámara siga fluyendo
                frame_copy = self.frame_ia.copy()
                results = model(frame_copy, conf=0.7, verbose=False)

                # Actualizar visualización
                frame_dibujo = frame_copy.copy()

                mapa_nombres = {
                    "Speed Limit 25mph": "Speed Limit"
                }

                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    nombre_original = model.names[cls_id]

                    # Aplicamos el cambio de nombre
                    nombre_final = mapa_nombres.get(nombre_original, nombre_original)

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Dibujar rectángulo
                    cv2.rectangle(frame_dibujo, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Dibujar texto con nombre modificado
                    cv2.putText(frame_dibujo, nombre_final,
                                (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7,
                                (0, 255, 0),
                                2)

                self.anotaciones = frame_dibujo

                # Objetos detectados en ESTA toma
                objetos_actuales = set([
                    "Speed Limit" if model.names[int(box.cls[0])] == "Speed Limit 25mph"
                    else model.names[int(box.cls[0])]
                    for box in results[0].boxes
                ])

                # COMPARACIÓN DE TOMAS:
                # Buscamos qué hay en la toma actual que NO estaba en la anterior
                aparecieron = objetos_actuales - self.memoria_ultima_toma

                if aparecieron:
                    mensaje = f"Apareció: {', '.join(aparecieron)}"
                    print(mensaje)
                    hablar_nativo(mensaje)

                # ACTUALIZAMOS LA MEMORIA:
                # Ahora la toma actual se convierte en la "anterior" para el siguiente ciclo.
                # Esto permite que si algo desaparece, el set se limpie y pueda volver a anunciarse.
                self.memoria_ultima_toma = objetos_actuales

                time.sleep(0.5)  # Pausa para procesar la siguiente toma
            else:
                time.sleep(0.1)


# --- 3. EJECUCIÓN ---
robot = RobotVision()
threading.Thread(target=robot.hilo_ia, daemon=True).start()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    robot.frame_ia = frame

    if robot.anotaciones is not None:
        cv2.imshow("Robot Arabots 2026 - Comparador", robot.anotaciones)
    else:
        cv2.imshow("Robot Arabots 2026 - Comparador", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        robot.corriendo = False
        break

cap.release()
cv2.destroyAllWindows()