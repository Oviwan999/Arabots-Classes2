import cv2
import numpy as np
import time
import ctypes
from pykinect2 import PyKinectRuntime, PyKinectV2

# --- CONFIGURACIÓN DE ENTORNO ---
if not hasattr(time, 'clock'):
    time.clock = time.perf_counter

import numpy

numpy.object = object


class ArabotsKinectExtremities:
    def __init__(self):
        self._kinect = PyKinectRuntime.PyKinectRuntime(
            PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body
        )
        self._kinect.bodies = numpy.ndarray((6), dtype=object)
        self.view_w, self.view_h = 960, 540
        self._bodies = None

    def get_color_joint_points(self, joints):
        joint_points = numpy.ndarray((PyKinectV2.JointType_Count), dtype=object)
        for j in range(0, PyKinectV2.JointType_Count):
            joint_points[j] = self._kinect._mapper.MapCameraPointToColorSpace(joints[j].Position)
        return joint_points

    def safe_draw_point(self, img, point, color, label):
        """Dibuja un punto solo si las coordenadas son números válidos (no infinito)."""
        try:
            # Validar que no sean NaN o Infinito
            if not (np.isinf(point.x) or np.isinf(point.y) or np.isnan(point.x) or np.isnan(point.y)):
                px = int(point.x * self.view_w / 1920)
                py = int(point.y * self.view_h / 1080)

                if 0 <= px < self.view_w and 0 <= py < self.view_h:
                    cv2.circle(img, (px, py), 10, color, -1)
                    cv2.putText(img, label, (px + 10, py), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                    return (px, py)
        except OverflowError:
            pass
        return None

    def run(self):
        print("Analizando: Manos y Pies. Presiona 'q' para salir.")

        while True:
            if self._kinect.has_new_color_frame():
                frame = self._kinect.get_last_color_frame()
                img = frame.reshape((1080, 1920, 4))
                img = cv2.resize(img, (self.view_w, self.view_h))
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            else:
                img = np.zeros((self.view_h, self.view_w, 3), np.uint8)

            if self._kinect.has_new_body_frame():
                self._bodies = self._kinect.get_last_body_frame()

            if self._bodies is not None:
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if body.is_tracked:
                        joints = body.joints
                        joint_points = self.get_color_joint_points(joints)

                        # --- EXTRACCIÓN DE LAS 4 EXTREMIDADES ---
                        extremidades = [
                            (PyKinectV2.JointType_HandRight, (0, 255, 0), "Mano D"),
                            (PyKinectV2.JointType_HandLeft, (0, 255, 255), "Mano I"),
                            (PyKinectV2.JointType_FootRight, (255, 0, 0), "Pie D"),
                            (PyKinectV2.JointType_FootLeft, (255, 0, 255), "Pie I")
                        ]

                        for joint_type, color, label in extremidades:
                            pos_3d = joints[joint_type].Position
                            # Imprimir coordenadas en metros en la consola
                            if i == 0:  # Solo del primer usuario para no saturar
                                print(f"{label}: x={pos_3d.x:.2f} y={pos_3d.y:.2f} z={pos_3d.z:.2f}", end=" | ")

                            # Dibujar en pantalla con filtro de seguridad
                            self.safe_draw_point(img, joint_points[joint_type], color, label)

                        print("", end="\r")  # Limpiar línea de consola

            cv2.imshow('Arabots - Extremidades', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self._kinect.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    ArabotsKinectExtremities().run()