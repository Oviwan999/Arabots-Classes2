import cv2
import numpy as np
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
    dx = np.gradient(points[:, 0])
    dy = np.gradient(points[:, 1])
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)
    curvature = (dx * ddy - dy * ddx) / np.power(dx ** 2 + dy ** 2, 1.5)
    return curvature


def detect_high_curvature_points(contour, threshold=0.1):
    curvature = compute_curvature(contour[:, 0, :])
    high_curvature_points = np.where(np.abs(curvature) > threshold)[0]
    return contour[high_curvature_points, 0, :]


def angle_between(v1, v2):
    dot_product = np.dot(v1, v2)
    det = v1[0] * v2[1] - v1[1] * v2[0]
    angle = np.arctan2(det, dot_product)
    return np.degrees(angle)


def merge_segments(segments, angle_threshold=10):
    merged = []
    current_segment = segments[0]

    for next_segment in segments[1:]:
        vec1 = np.array(current_segment[1]) - np.array(current_segment[0])
        vec2 = np.array(next_segment[1]) - np.array(next_segment[0])

        angle_diff = abs(angle_between(vec1, vec2))

        if angle_diff < angle_threshold or abs(angle_diff - 180) < angle_threshold:
            current_segment = [current_segment[0], next_segment[1]]
        else:
            merged.append(current_segment)
            current_segment = next_segment

    merged.append(current_segment)
    return merged


def on_trackbar(val):
    pass


def metrology_report_realtime_with_sliders(min_contour_area=5000, angle_threshold=10):
    global puntos_calibracion, conversion_mm_pixel

    cap = cv2.VideoCapture(0)
    ret, imagen = cap.read()
    cv2.imshow("Imagen en tiempo real", imagen)
    cv2.setMouseCallback("Imagen en tiempo real", click_event, imagen)

    cv2.createTrackbar('Canny Lower', 'Imagen en tiempo real', 50, 255, on_trackbar)
    cv2.createTrackbar('Canny Upper', 'Imagen en tiempo real', 150, 255, on_trackbar)
    cv2.createTrackbar('Min Arc Length', 'Imagen en tiempo real', 10, 100, on_trackbar)
    cv2.createTrackbar('Min Line Length', 'Imagen en tiempo real', 10, 100, on_trackbar)

    while True:
        key = cv2.waitKey(1)
        if key == ord('c') and len(puntos_calibracion) == 2:
            distancia = float(input("Ingrese la distancia en milímetros entre los dos puntos: "))
            pixels = np.linalg.norm(np.array(puntos_calibracion[0]) - np.array(puntos_calibracion[1]))
            conversion_mm_pixel = distancia / pixels
            puntos_calibracion = []
            break

    segment_data = []

    while True:
        ret, imagen = cap.read()
        gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

        canny_lower = cv2.getTrackbarPos('Canny Lower', 'Imagen en tiempo real')
        canny_upper = cv2.getTrackbarPos('Canny Upper', 'Imagen en tiempo real')
        min_arc_length = cv2.getTrackbarPos('Min Arc Length', 'Imagen en tiempo real')
        min_line_length = cv2.getTrackbarPos('Min Line Length', 'Imagen en tiempo real')

        bordes = cv2.Canny(gris, canny_lower, canny_upper)
        contornos, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contornos:
            contorno_pieza = max(contornos, key=cv2.contourArea)

            if cv2.contourArea(contorno_pieza) > min_contour_area:
                high_curvature_pts = detect_high_curvature_points(contorno_pieza)

                for pt in high_curvature_pts:
                    cv2.circle(imagen, tuple(pt), 5, (255, 0, 0), -1)

                epsilon = 0.02 * cv2.arcLength(contorno_pieza, True)
                aproximado = cv2.approxPolyDP(contorno_pieza, epsilon, True)

                segments = []
                for i in range(len(aproximado)):
                    p1 = tuple(aproximado[i][0])
                    p2 = tuple(aproximado[(i + 1) % len(aproximado)][0])
                    segments.append([p1, p2])

                merged_segments = merge_segments(segments, angle_threshold)
                for segment in merged_segments:
                    p1, p2 = segment
                    distance = np.linalg.norm(np.array(p1) - np.array(p2)) * conversion_mm_pixel

                    if distance >= min_line_length:
                        segment_data.append({
                            'Type': 'Line',
                            'Start': p1,
                            'End': p2,
                            'Length (mm)': distance
                        })
                        cv2.line(imagen, p1, p2, (0, 255, 0), 2)
                    elif distance >= min_arc_length:
                        segment_data.append({
                            'Type': 'Arc',
                            'Start': p1,
                            'End': p2,
                            'Length (mm)': distance
                        })

        cv2.imshow("Imagen en tiempo real", imagen)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            df = pd.DataFrame(segment_data)
            df.to_csv('metrology_report.csv', index=False)

        elif cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
metrology_report_realtime_with_sliders()