import cv2
from ultralytics import YOLO
import win32com.client
import threading
import time


# --- 1. VOZ NATIVA ---
def hablar_nativo(texto):
    def proceso():
        try:
            # CoInitialize permite que el hilo use objetos COM de Windows sin trabarse
            import pythoncom
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(texto)
        except:
            pass

    threading.Thread(target=proceso, daemon=True).start()


# --- 2. IA EN HILO ULTRA-FLUIDO ---
# Usamos un objeto para pasar los datos y evitar bloqueos de memoria
class VisionState:
    def __init__(self):
        self.frame_para_ia = None
        self.anotaciones = None
        self.corriendo = True


state = VisionState()


def hilo_ia():
    model = YOLO('yolov8n.pt')
    while state.corriendo:
        if state.frame_para_ia is not None:
            # 1. Hacemos la inferencia sobre una copia
            results = model(state.frame_para_ia, conf=0.5, verbose=False)

            # 2. Guardamos el resultado de los cuadros (ROI)
            state.anotaciones = results[0].plot()

            # 3. Voz cada 2 segundos
            objetos = set([model.names[int(box.cls[0])] for box in results[0].boxes])
            if objetos:
                hablar_nativo(f"Veo {', '.join(objetos)}")

            # 4. Descanso total para dejar que la CPU respire
            time.sleep(2)
        else:
            time.sleep(0.01)


# Iniciar IA
threading.Thread(target=hilo_ia, daemon=True).start()

# --- 3. BUCLE PRINCIPAL (Prioridad de Video) ---
cap = cv2.VideoCapture(0)

# Ajustes de velocidad para la cámara
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Evita que se acumulen frames viejos

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    # Pasamos el frame a la IA sin detenernos
    state.frame_para_ia = frame.copy()

    # DIBUJO INTELIGENTE:
    # En lugar de mostrar 'state.anotaciones' directamente (que es una imagen completa),
    # vamos a dibujar la info de la IA sobre el frame EN VIVO si existe.
    if state.anotaciones is not None:
        # Fusionamos un poco del frame viejo con el nuevo para suavizar
        display_frame = cv2.addWeighted(frame, 0.7, state.anotaciones, 0.3, 0)
        cv2.imshow("Vision Arabots 2026 - 60 FPS", display_frame)
    else:
        cv2.imshow("Vision Arabots 2026 - 60 FPS", frame)

    # El waitKey(1) es vital, si es muy alto da tirones
    if cv2.waitKey(1) & 0xFF == ord("q"):
        state.corriendo = False
        break

cap.release()
cv2.destroyAllWindows()