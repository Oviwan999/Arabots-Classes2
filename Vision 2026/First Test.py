import cv2
from ultralytics import YOLO
import win32com.client  # Librería nativa de Windows
import threading
import time


# --- 1. CONFIGURACIÓN DE VOZ NATIVA (SAPI5) ---
def hablar_nativo(texto):
    def proceso():
        try:
            # Inicializa el objeto de voz de Windows dentro del hilo
            # Esto evita conflictos de memoria entre hilos
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(texto)
        except Exception as e:
            print(f"Error de voz: {e}")

    # Lanzamos la voz en un hilo para que no detenga el video
    threading.Thread(target=proceso, daemon=True).start()


# --- 2. CONFIGURACIÓN DE IA EN HILO ---
frame_actual = None
anotaciones_global = None
corriendo = True


def hilo_ia():
    global frame_actual, anotaciones_global, corriendo
    model = YOLO('yolov8n.pt')

    while corriendo:
        if frame_actual is not None:
            # La IA analiza una copia para no trabar la cámara
            img_ia = frame_actual.copy()
            results = model(img_ia, conf=0.5, verbose=False)

            # Guardamos los dibujos para el hilo principal
            anotaciones_global = results[0].plot()

            # Detectar nombres únicos
            objetos = set([model.names[int(box.cls[0])] for box in results[0].boxes])

            if objetos:
                frase = f"Detectado: {', '.join(objetos)}"
                print(f"Robot dice: {frase}")
                hablar_nativo(frase)

            # Espera 2 segundos antes de la siguiente detección
            time.sleep(2)
        else:
            time.sleep(0.1)


# Iniciar el hilo de la IA
threading.Thread(target=hilo_ia, daemon=True).start()

# --- 3. BUCLE DE CÁMARA (HILO PRINCIPAL) ---
cap = cv2.VideoCapture(0)

# Opcional: Ajustar resolución para mayor velocidad
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame_actual = frame  # Actualizamos el frame para que el hilo IA lo vea

    # Mostramos las anotaciones si existen, si no, el video real
    if anotaciones_global is not None:
        cv2.imshow("Vision Arabots 2026 - Nativo", anotaciones_global)
    else:
        cv2.imshow("Vision Arabots 2026 - Nativo", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        corriendo = False
        break

cap.release()
cv2.destroyAllWindows()