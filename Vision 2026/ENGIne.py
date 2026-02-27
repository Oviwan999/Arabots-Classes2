from ultralytics import YOLO

# Cargas tu modelo entrenado
model = YOLO(r'runs/detect/Vision2026_v24/weights/best.pt')

# Exportas a TensorRT (Engine)
# 'half=True' usa precisión de 16-bits, que es perfecta para la serie 40
model.export(format='engine', device=0, half=True)