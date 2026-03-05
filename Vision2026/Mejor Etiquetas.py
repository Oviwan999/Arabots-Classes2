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
    def __init__(self, engine_path):
        self.frame_ia = None
        self.anotaciones = None
        self.corriendo = True
        # Memoria ahora guarda (Label, Precisión) para comparar cambios significativos
        self.memoria_ultima_toma = set()

        # Cargamos el modelo ENGINE
        self.model = YOLO(engine_path, task='detect')

        # --- DICCIONARIO DE CONFIANZA POR CLASE ---
        self.confidencias = {
            'Stop': 0.10, 'Yield': 0.55, 'Do Not Enter': 0.65,
            'No Left Turn': 0.85, 'No Right Turn': 0.8, 'No U Turn': 0.80,
            'Left Turn Only': 0.85, 'Right Turn Only': 0.80,
            'Straight or Left Turn Only': 0.80, 'Straight or Right Turn Only': 0.80,
            'One Way Left': 0.70, 'One Way Right': 0.7,
            'Left Curve Ahead': 0.70, 'Right Curve Ahead': 0.70,
            'No Parking Left Arrow': 0.9, 'No Parking No Arrow': 0.8,
            'No Parking Double Arrow': 0.9, 'Pedestrian Crossing': 0.60,
            'School Crossing': 0.60, 'Speed Limit 25mph': 0.75,
            'Be Prepared to Stop': 0.65, 'Left Turn Yield on Green': 0.9,
            'No Turn on Red': 0.80, 'When Flashing': 0.80
        }
        self.conf_default = 0.50

    def hilo_ia(self):
        while self.corriendo:
            if self.frame_ia is not None:
                frame_copy = self.frame_ia.copy()

                # EJECUCIÓN CON ENGINE + FP16 (half=True)
                results = self.model(frame_copy, conf=0.35, verbose=False, device=0, half=True)

                nombres_validados = set()
                detalles_voz = []  # Para guardar "Nombre + Porcentaje"
                boxes_validadas = []

                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]
                    conf_detectada = float(box.conf[0])

                    umbral_minimo = self.confidencias.get(label, self.conf_default)

                    if conf_detectada >= umbral_minimo:
                        nombres_validados.add(label)
                        # Guardamos el detalle para la voz (ej: "Stop al 92 por ciento")
                        porcentaje = int(conf_detectada * 100)
                        detalles_voz.append(f"{label} al {porcentaje} por ciento")
                        boxes_validadas.append(box)

                # DIBUJO MANUAL
                annotated_frame = frame_copy.copy()
                for box in boxes_validadas:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = self.model.names[int(box.cls[0])]
                    conf = float(box.conf[0])

                    # Dibujamos Verde Neón para resaltar
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, f"{label} {int(conf * 100)}%", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                self.anotaciones = annotated_frame

                # LÓGICA DE MEMORIA Y VOZ CON PRECISIÓN
                aparecieron = nombres_validados - self.memoria_ultima_toma
                if aparecieron:
                    # Filtramos los detalles de voz para que solo diga los que "Aparecieron"
                    mensajes_nuevos = [d for d in detalles_voz if any(n in d for n in aparecieron)]
                    if mensajes_nuevos:
                        mensaje_final = f"Atención: {', '.join(mensajes_nuevos)}"
                        print(mensaje_final)
                        hablar_nativo(mensaje_final)

                self.memoria_ultima_toma = nombres_validados
                time.sleep(0.1)
            else:
                time.sleep(0.05)


# --- 3. EJECUCIÓN ---
ruta_engine = r'C:\git\Arabots-Classes2\Vision2026\runs\detect\Vision2026_v24\weights\best.engine'

robot = RobotVision(ruta_engine)
threading.Thread(target=robot.hilo_ia, daemon=True).start()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    robot.frame_ia = frame
    display_frame = robot.anotaciones if robot.anotaciones is not None else frame

    cv2.imshow("Arabots 2026 - Novi Engine Precision Mode", display_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        robot.corriendo = False
        break

cap.release()
cv2.destroyAllWindows()