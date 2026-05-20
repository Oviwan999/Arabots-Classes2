import os
os.environ["YOLO_OFFLINE"] = "True"
os.environ["ULTRALYTICS_HUB"] = "0"

import cv2
import time
import traceback
from ultralytics import YOLO

try:
    from ultralytics.utils import SETTINGS
    SETTINGS["sync"] = False
    SETTINGS["hub"] = False
except Exception:
    pass

MODELO = r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Vision2026_v24\weights\best.pt"
# También puedes probar:
# MODELO = "yolov8n.pt"

print("Cargando modelo...")
model = YOLO(MODELO, task="detect")
print("Modelo cargado.")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("No se pudo abrir la cámara")
    raise SystemExit

print("Prueba CÁMARA + YOLO SIN VOZ. Presiona q para salir.")

while True:
    ok, frame = cap.read()
    if not ok or frame is None:
        print("No se pudo leer frame")
        time.sleep(0.1)
        continue

    try:
        results = model.predict(
            source=frame,
            conf=0.25,
            imgsz=640,
            verbose=False,
            device=0
        )

        annotated = frame.copy()

        if results and len(results) > 0 and results[0].boxes is not None:
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                label = model.names[cls_id]
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    annotated,
                    f"{label} {int(conf * 100)}%",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        cv2.imshow("TEST YOLO SIN VOZ", annotated)

    except Exception as e:
        print("Error en inferencia:", repr(e))
        traceback.print_exc()
        cv2.imshow("TEST YOLO SIN VOZ", frame)
        time.sleep(0.2)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()