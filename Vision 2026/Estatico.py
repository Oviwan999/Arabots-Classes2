import cv2
import os
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
class RobotVisionCarpeta:
    def __init__(self, ruta_carpeta):
        self.ruta_carpeta = ruta_carpeta
        # Obtener lista de imágenes soportadas
        self.imagenes = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        self.indice = 0
        self.frame_actual = None
        self.anotaciones = None
        self.corriendo = True

        if not self.imagenes:
            print("❌ No se encontraron imágenes en la carpeta.")
            self.corriendo = False

        # Cargar modelo (Aprovechando tu RTX 4060)
        self.model = YOLO(r'D:\pythonProject\Arabots-Classes2\Vision 2026\runs\detect\Vision20263\weights\best.pt')

    def procesar_imagen_actual(self):
        """Carga la imagen actual y ejecuta la IA una sola vez."""
        img_path = os.path.join(self.ruta_carpeta, self.imagenes[self.indice])
        frame = cv2.imread(img_path)

        if frame is not None:
            # Redimensionar si la imagen es muy grande para tu pantalla
            h, w = frame.shape[:2]
            if w > 1280: frame = cv2.resize(frame, (1280, int(h * 1280 / w)))

            # Ejecutar IA (confianza 0.7 como tenías)
            results = self.model(frame, conf=0.45, verbose=False)
            self.anotaciones = results[0].plot()

            # Extraer nombres de lo detectado
            objetos = [self.model.names[int(box.cls[0])] for box in results[0].boxes]

            if objetos:
                mensaje = f"En esta imagen hay: {', '.join(set(objetos))}"
                print(f"[{self.imagenes[self.indice]}] -> {mensaje}")
                hablar_nativo(mensaje)
            else:
                print(f"[{self.imagenes[self.indice]}] -> No se detectaron señales.")
        else:
            print(f"Error cargando: {img_path}")

    def siguiente(self):
        if self.indice < len(self.imagenes) - 1:
            self.indice += 1
            self.procesar_imagen_actual()
        else:
            print("🏁 ¡Llegaste al final de la carpeta!")
            hablar_nativo("Fin de la carpeta")

    def anterior(self):
        if self.indice > 0:
            self.indice -= 1
            self.procesar_imagen_actual()


# --- 3. EJECUCIÓN ---
ruta_fotos = r'C:\Users\oviwa\Downloads\vcc2026-newlabels-dv-v3\images'  # <-- CAMBIA ESTO A TU CARPETA DE PRUEBAS
robot = RobotVisionCarpeta(ruta_fotos)

# Procesar la primera imagen al abrir
if robot.corriendo:
    robot.procesar_imagen_actual()

    print("\n--- CONTROLES ---")
    print("N: Siguiente imagen")
    print("B: Imagen anterior")
    print("Q: Salir\n")

    while robot.corriendo:
        if robot.anotaciones is not None:
            # Mostrar nombre de archivo en la ventana
            titulo = f"Robot Arabots - {robot.imagenes[robot.indice]}"
            cv2.imshow("Visor de Senales", robot.anotaciones)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("n"):  # NEXT
            robot.siguiente()
        elif key == ord("b"):  # BACK (Anterior)
            robot.anterior()

cv2.destroyAllWindows()