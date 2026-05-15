from ultralytics import RTDETR

# 1. Carga tu modelo de RT-DETR (asegúrate de que la extensión sea .pt)
model = RTDETR(r'bestrgen.pt')

# 2. Exportación Maestra a Engine
# Agregamos imgsz=640 porque TensorRT necesita dimensiones fijas para máxima velocidad
model.export(
    format='engine',
    device=0,
    half=True,
    imgsz=800,    # Debe coincidir con el tamaño usado en el entrenamiento
    simplify=True # Esto limpia el grafo de la red para que sea aún más rápido
)