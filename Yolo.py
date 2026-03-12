import cv2
from ultralytics import YOLO
import pyttsx3


engine = pyttsx3.init()
def hablar(texto):
    engine.say(texto)
    engine.runAndWait()

model = YOLO('yolov8n.pt')

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model(frame, conf=.5)

        anotaciones = results[0].plot
        cv2.imshow('vision de robot',frame)

        for box in results[0].boxes:
            clase_id = int(box.cls[0])
            nombre_objeto = model.names[clase_id]
            hablar(f"veo un {nombre_objeto}")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()