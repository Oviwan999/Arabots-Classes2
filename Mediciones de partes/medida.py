import cv2
import numpy as np
import csv
import pandas as pd
import matplotlib.pyplot as plt

# Variables globales
puntos_calibracion = []
conversion_mm_pixel = 1.0

def click_event(event, x, y, flags, param):
    global puntos_calibracion
    imagen = param
    if event == cv2.EVENT_LBUTTONDOWN:
        puntos_calibracion.append((x, y))
        cv2.circle(imagen, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Imagen en tiempo real", imagen)

def compute_curvature(points):
    """Compute curvature for a set of points using finite differences."""
    dx = np.gradient(points[:, 0])
    dy = np.gradient(points[:, 1])
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)
    curvature = (dx * ddy - dy * ddx) / np.power(dx**2 + dy**2, 1.5)
    return curvature

def detect_high_curvature_points(contour, threshold=0.1):
    """Detect high curvature points in a contour."""
    curvature = compute_curvature(contour[:, 0, :])
    high_curvature_points = np.where(np.abs(curvature) > threshold)[0]
    return contour[high_curvature_points, 0, :]

def metrology_report_realtime(min_contour_area=5000):
    global puntos_calibracion, conversion_mm_pixel

    cap = cv2.VideoCapture(0)
    ret, imagen = cap.read()
    cv2.imshow("Imagen en tiempo real", imagen)
    cv2.setMouseCallback("Imagen en tiempo real", click_event, imagen)

    while True:
        key = cv2.waitKey(1)
        if key == ord('c') and len(puntos_calibracion) == 2:
            distancia = float(input("Ingrese la distancia en milímetros entre los dos puntos: "))
            pixels = np.linalg.norm(np.array(puntos_calibracion[0]) - np.array(puntos_calibracion[1]))
            conversion_mm_pixel = distancia / pixels
            puntos_calibracion = []  # Clear calibration points for next use
            break

    medidas = []
    segmentos = []

    while True:
        ret, imagen = cap.read()
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        bordes = cv2.Canny(gris, 50, 150)
        contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contornos:
            contorno_pieza = max(contornos, key=cv2.contourArea)

            if cv2.contourArea(contorno_pieza) > min_contour_area:
                high_curvature_pts = detect_high_curvature_points(contorno_pieza)

                for pt in high_curvature_pts:
                    cv2.circle(imagen, tuple(pt), 5, (255, 0, 0), -1)

                epsilon = 0.02 * cv2.arcLength(contorno_pieza, True)
                aproximado = cv2.approxPolyDP(contorno_pieza, epsilon, True)

                perimetro = 0
                for i in range(len(aproximado)):
                    p1 = aproximado[i][0]
                    p2 = aproximado[(i + 1) % len(aproximado)][0]
                    distancia = np.linalg.norm(p1 - p2) * conversion_mm_pixel
                    segmentos.append({
                        'Segmento': f"Segmento {i+1}",
                        'Medida (mm)': distancia
                    })
                    perimetro += distancia
                    cv2.line(imagen, tuple(p1), tuple(p2), (0, 255, 0), 2)

                medidas.append(perimetro)

        cv2.imshow("Imagen en tiempo real", imagen)

        # Save report with 's'
        if cv2.waitKey(1) & 0xFF == ord('s'):
            # Generate metrology report using pandas and matplotlib
            df = pd.DataFrame(segmentos)

            # Plotting
            fig, ax = plt.subplots(figsize=(10, 6))
            df.plot(kind='bar', x='Segmento', y='Medida (mm)', ax=ax)
            plt.title('Informe de Metrología')
            plt.ylabel('Longitud (mm)')
            plt.tight_layout()
            plt.savefig('metrology_report.png')
            plt.show()

            # Saving to CSV
            df.to_csv('metrology_report.csv', index=False)

        # Exit with 'q'
        elif cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# To run the realtime metrology report:
metrology_report_realtime()