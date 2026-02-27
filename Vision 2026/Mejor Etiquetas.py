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
        self.memoria_ultima_toma = set()

        # Cargamos el modelo ENGINE (TensorRT)
        # Especificamos task='detect' para asegurar la compatibilidad
        self.model = YOLO(engine_path, task='detect')

        # --- DICCIONARIO DE CONFIANZA POR CLASE ---
        self.confidencias = {
            'Stop': 0.50,
            'Yield': 0.55,
            'Do Not Enter': 0.65,
            'No Left Turn': 0.85,
            'No Right Turn': 0.85,
            'No U Turn': 0.80,
            'Left Turn Only': 0.80,
            'Right Turn Only': 0.80,
            'Straight or Left Turn Only': 0.80,
            'Straight or Right Turn Only': 0.80,
            'One Way Left': 0.75,
            'One Way Right': 0.75,
            'Left Curve Ahead': 0.70,
            'Right Curve Ahead': 0.70,
            'No Parking Left Arrow': 0.85,
            'No Parking No Arrow': 0.85,
            'No Parking Double Arrow': 0.85,
            'Pedestrian Crossing': 0.60,
            'School Crossing': 0.60,
            'Speed Limit': 0.75,
            'Be Prepared to Stop': 0.65,
            'Left Turn Yield on Green': 0.70,
            'No Turn on Red': 0.80,
            'When Flashing': 0.70
        }
        self.conf_default = 0.70

    def hilo_ia(self):
        while self.corriendo:
            if self.frame_ia is not None:
                frame_copy = self.frame_ia.copy()

                # EJECUCIÓN CON ENGINE
                # Usamos half=True porque las RTX 40 series vuelan en precisión media (FP16)
                results = self.model(frame_copy, conf=0.35, verbose=False, device=0, half=True)

                nombres_validados = set()
                detalles_voz = []
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

                # DIBUJO MANUAL (Optimizado para evitar parpadeo)
                annotated_frame = frame_copy.copy()
                for box in boxes_validadas:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = self.model.names[int(box.cls[0])]
                    conf = float(box.conf[0])
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                self.anotaciones = annotated_frame

                # LÓGICA DE MEMORIA
                aparecieron = nombres_validados - self.memoria_ultima_toma
                if aparecieron:
                    mensaje = f"Atencion: {', '.join(aparecieron)}"
                    print(mensaje)
                    hablar_nativo(mensaje)

                self.memoria_ultima_toma = nombres_validados
                time.sleep(0.1)  # Con .engine podemos bajar este tiempo porque es más rápido
            else:
                time.sleep(0.05)


# --- 3. EJECUCIÓN ---
# Asegúrate de haber exportado antes tu .pt a .engine
ruta_engine = r'D:\pythonProject\Arabots-Classes2\Vision 2026\runs\detect\Vision20263\weights\best.engine'

robot = RobotVision(ruta_engine)
threading.Thread(target=robot.hilo_ia, daemon=True).start()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    robot.frame_ia = frame
    display_frame = robot.anotaciones if robot.anotaciones is not None else frame

    cv2.imshow("Arabots 2026 - TENSORRT ENGINE MODE", display_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        robot.corriendo = False
        break

cap.release()
cv2.destroyAllWindows()