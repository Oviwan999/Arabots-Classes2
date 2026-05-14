import cv2


import numpy as np
import time
from pykinect2 import PyKinectRuntime, PyKinectV2

# --- PARCHES DE COMPATIBILIDAD ---
if not hasattr(time, 'clock'):
    time.clock = time.perf_counter
import numpy

numpy.object = object


class ArabotsPuppetMonitor:
    def __init__(self):
        self._kinect = PyKinectRuntime.PyKinectRuntime(
            PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body
        )
        self._kinect.bodies = numpy.ndarray((6), dtype=object)
        self.view_w, self.view_h = 960, 540
        self._bodies = None
        self.target_body_id = None

    def get_color_joint_points(self, joints):
        joint_points = numpy.ndarray((PyKinectV2.JointType_Count), dtype=object)
        for j in range(0, PyKinectV2.JointType_Count):
            joint_points[j] = self._kinect._mapper.MapCameraPointToColorSpace(joints[j].Position)
        return joint_points

    def is_raising_hands(self, joints):
        """ Gesto de Inicio: Ambas manos sobre la cabeza """
        head_y = joints[PyKinectV2.JointType_Head].Position.y
        return (joints[PyKinectV2.JointType_HandLeft].Position.y > head_y and
                joints[PyKinectV2.JointType_HandRight].Position.y > head_y)

    def is_touching_foot(self, joints):
        """ Gesto de Reset: Mano Derecha toca Pie Izquierdo """
        hand_r = joints[PyKinectV2.JointType_HandRight].Position
        foot_l = joints[PyKinectV2.JointType_FootLeft].Position

        # Distancia euclidiana 3D
        dist = np.sqrt((hand_r.x - foot_l.x) ** 2 + (hand_r.y - foot_l.y) ** 2 + (hand_r.z - foot_l.z) ** 2)

        # Umbral de 20cm para considerar "toque"
        return dist < 0.20

    def draw_skeleton(self, img, joints, joint_points):
        connections = [
            (PyKinectV2.JointType_Head, PyKinectV2.JointType_Neck),
            (PyKinectV2.JointType_Neck, PyKinectV2.JointType_SpineShoulder),
            (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderLeft),
            (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_ShoulderRight),
            (PyKinectV2.JointType_ShoulderLeft, PyKinectV2.JointType_ElbowLeft),
            (PyKinectV2.JointType_ElbowLeft, PyKinectV2.JointType_WristLeft),
            (PyKinectV2.JointType_ShoulderRight, PyKinectV2.JointType_ElbowRight),
            (PyKinectV2.JointType_ElbowRight, PyKinectV2.JointType_WristRight),
            (PyKinectV2.JointType_SpineShoulder, PyKinectV2.JointType_SpineMid),
            (PyKinectV2.JointType_SpineMid, PyKinectV2.JointType_SpineBase),
            (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipLeft),
            (PyKinectV2.JointType_SpineBase, PyKinectV2.JointType_HipRight),
            (PyKinectV2.JointType_HipLeft, PyKinectV2.JointType_KneeLeft),
            (PyKinectV2.JointType_KneeLeft, PyKinectV2.JointType_AnkleLeft),
            (PyKinectV2.JointType_HipRight, PyKinectV2.JointType_KneeRight),
            (PyKinectV2.JointType_KneeRight, PyKinectV2.JointType_AnkleRight)
        ]

        for j1, j2 in connections:
            if joints[j1].TrackingState == PyKinectV2.TrackingState_Tracked and \
                    joints[j2].TrackingState == PyKinectV2.TrackingState_Tracked:
                start = (int(joint_points[j1].x * self.view_w / 1920), int(joint_points[j1].y * self.view_h / 1080))
                end = (int(joint_points[j2].x * self.view_w / 1920), int(joint_points[j2].y * self.view_h / 1080))
                if not np.isinf(start).any() and not np.isinf(end).any():
                    cv2.line(img, start, end, (255, 255, 0), 2)

    def run(self):
        print("SISTEMA ARABOTS: MANO DER a PIE IZQ para soltar objetivo.")

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
                selected_body = None

                # 1. Selección de Body
                for i in range(0, self._kinect.max_body_count):
                    body = self._bodies.bodies[i]
                    if not body.is_tracked: continue

                    if self.target_body_id == body.tracking_id:
                        # Si es el actual, checar si quiere soltar (Mano Der -> Pie Izq)
                        if self.is_touching_foot(body.joints):
                            print(f"\nOBJETIVO {self.target_body_id} LIBERADO")
                            self.target_body_id = None
                            break
                        selected_body = body
                        break

                    elif self.target_body_id is None:
                        if self.is_raising_hands(body.joints):
                            self.target_body_id = body.tracking_id
                            print(f"\nNUEVO OBJETIVO: {self.target_body_id}")
                            selected_body = body
                            break

                # 2. Procesamiento Visual (Solo si hay alguien seleccionado)
                if selected_body:
                    joints = selected_body.joints
                    joint_points = self.get_color_joint_points(joints)
                    self.draw_skeleton(img, joints, joint_points)

                    # Recuperamos la lógica de colores por estado de mano
                    # Abierta (2) = Verde, Cerrada (3) = Rojo, Lasso (4) = Amarillo
                    color_R = (0, 255, 0) if selected_body.hand_right_state == 2 else \
                        (0, 0, 255) if selected_body.hand_right_state == 3 else (0, 255, 255)

                    color_L = (0, 255, 0) if selected_body.hand_left_state == 2 else \
                        (0, 0, 255) if selected_body.hand_left_state == 3 else (0, 255, 255)

                    puntos = {
                        "CABEZA": PyKinectV2.JointType_Head,
                        "MANO D": PyKinectV2.JointType_HandRight,
                        "MANO I": PyKinectV2.JointType_HandLeft,
                        "PIE D": PyKinectV2.JointType_FootRight,
                        "PIE I": PyKinectV2.JointType_FootLeft
                    }

                    for nombre, jt_id in puntos.items():
                        jp = joint_points[jt_id]
                        if not np.isinf(jp.x):
                            px = int(jp.x * self.view_w / 1920)
                            py = int(jp.y * self.view_h / 1080)

                            # Aplicar color dinámico a las manos
                            dot_color = color_R if "MANO D" in nombre else \
                                color_L if "MANO I" in nombre else (255, 255, 255)

                            cv2.circle(img, (px, py), 15, dot_color, -1)
                            cv2.circle(img, (px, py), 18, (255, 255, 255), 2)

                            etiqueta = f"{nombre}: {joints[jt_id].Position.x:.2f}"
                            cv2.putText(img, etiqueta, (px + 20, py), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            cv2.imshow('Arabots Puppet Master', img)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        self._kinect.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    ArabotsPuppetMonitor().run()