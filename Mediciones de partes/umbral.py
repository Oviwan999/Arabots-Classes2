import cv2
import random

# Variables globales
frame_actual = None  # Variable para almacenar el frame actual
umbral_inicial = 180  # Umbral inicial
color_piezas = {}  # Diccionario para asignar un color único a cada pieza
area_minima = 100  # Área mínima para contar una figura


# Función para generar un color aleatorio
def generar_color_aleatorio():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


# Función para procesar un frame de video con un umbral específico
def procesar_frame(frame):
    global frame_actual, umbral_inicial

    # Almacenar el frame actual en la variable global
    frame_actual = frame

    # Convertir el frame a escala de grises
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplicar el umbral para segmentar el objeto blanco
    _, binary_mask = cv2.threshold(gris, umbral_inicial, 255, cv2.THRESH_BINARY)

    # Encontrar contornos en la máscara binaria
    contornos, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Crear una copia del frame para mostrar la máscara binaria
    frame_con_mask = frame.copy()

    # Inicializar un índice para etiquetar las partes
    indice_parte = 1

    # Procesar cada contorno individual
    for contorno in contornos:
        # Calcular el área del contorno
        area = cv2.contourArea(contorno)

        # Si el área es menor que el umbral definido, omitir esta figura
        if area < area_minima:
            continue

        # Calcular el perímetro del contorno
        perimetro = cv2.arcLength(contorno, True)

        # Obtener las coordenadas del centroide
        M = cv2.moments(contorno)
        if M["m00"] != 0:
            centroide_x = int(M["m10"] / M["m00"])
            centroide_y = int(M["m01"] / M["m00"])
        else:
            centroide_x, centroide_y = 0, 0

        # Generar un color aleatorio para la pieza (si aún no se ha asignado)
        if indice_parte not in color_piezas:
            color_piezas[indice_parte] = generar_color_aleatorio()

        # Dibujar el contorno en el frame original con el color asignado
        cv2.drawContours(frame, [contorno], -1, color_piezas[indice_parte], 2)

        # Etiquetar la figura con un número y mostrar el área, el perímetro y las coordenadas del centroide
        etiqueta = f"Parte {indice_parte}: Area={area:.2f}, Perimetro={perimetro:.2f}, Centroide=({centroide_x},{centroide_y})"
        cv2.putText(frame, etiqueta, (10, 30 * indice_parte), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_piezas[indice_parte],
                    2)

        # Dibujar la máscara binaria en la copia del frame
        cv2.drawContours(frame_con_mask, [contorno], -1, color_piezas[indice_parte], -1)  # Rellenar el contorno

        # Incrementar el índice de parte
        indice_parte += 1

    # Mostrar la máscara binaria junto al frame original
    cv2.imshow("Máscara Binaria", frame_con_mask)

    # Mostrar el frame resultante con las etiquetas
    cv2.imshow("Detección de Contorno en Tiempo Real", frame)


# Función de callback para la trackbar de umbral
def on_trackbar_umbral_change(val):
    global umbral_inicial
    umbral_inicial = val
    # Llamar a la función de procesamiento con el umbral actual
    procesar_frame(frame_actual)


# Función de callback para la trackbar de área mínima
def on_trackbar_area_minima_change(val):
    global area_minima
    area_minima = val
    # Llamar a la función de procesamiento con el umbral actual
    procesar_frame(frame_actual)


# Iniciar la captura de video desde la cámara (cambiar 0 a otro número si tienes múltiples cámaras)
cap = cv2.VideoCapture(0)

# Crear una ventana para mostrar la imagen
cv2.namedWindow("Detección de Contorno en Tiempo Real")

# Crear trackbars para ajustar el umbral y el área mínima en tiempo real
cv2.createTrackbar("Umbral", "Detección de Contorno en Tiempo Real", umbral_inicial, 255, on_trackbar_umbral_change)
cv2.createTrackbar("Área Mínima", "Detección de Contorno en Tiempo Real", area_minima, 2000,
                   on_trackbar_area_minima_change)

while True:
    # Capturar un frame de la cámara
    ret, frame_actual = cap.read()

    # Llamar a la función para procesar el frame
    procesar_frame(frame_actual)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
