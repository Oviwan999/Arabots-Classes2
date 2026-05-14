import os
from ultralytics import RTDETR

# --- CONFIGURACIÓN DE ÉXITO ARABOTS ---
DATA_YAML = "data.yaml"  # Asegúrate de que este archivo esté en la misma carpeta
MODELO_BASE = "rtdetr-l.pt"  # Versión Large: Máxima precisión para las 24 clases


def entrenar_maestro_antireflejos():
    """
    Entrenamiento optimizado para RT-DETR con enfoque en:
    1. Resiliencia a reflejos (HSV Augmentation)
    2. Estabilidad de clases direccionales (No Flips)
    3. Rendimiento en GPU 4060 (Batch 16 + AMP)
    """

    # 1. Cargar el modelo del estado del arte
    model = RTDETR(MODELO_BASE)

    # 2. Ejecutar entrenamiento con hiperparámetros de élite
    model.train(
        # --- ARCHIVOS Y RECURSOS ---
        data=DATA_YAML,
        epochs=200,  # Suficiente para que el Transformer converja
        imgsz=640,  # Vital para detectar texto pequeño en las señales
        batch=8,  # Optimizado para los 8GB de VRAM de tu 4060
        device=0,  # GPU NVIDIA obligatoria
        workers=8,  # Aprovechamos los núcleos de tu CPU para carga de datos
        amp=True,  # Mixed Precision para velocidad y ahorro de memoria

        # --- OPTIMIZACIÓN DE PÉRDIDA (Loss) ---
        cls=4.0,  # Peso en clasificación para no ignorar señales críticas
        box=12.0,  # Precisión milimétrica en el dibujo del cuadro (IoU)
        label_smoothing=0.1,  # Evita el overfitting y mejora la generalización
        warmup_epochs=10.0,  # Calentamiento de pesos para estabilidad inicial
        patience=50,  # Early stopping si el aprendizaje se estanca
        optimizer="AdamW",  # El estándar de oro para arquitecturas Transformer
        lr0=0.0005,  # Tasa de aprendizaje estable para RT-DETR

        # --- AUMENTACIÓN ANTI-REFLEJOS (LA CLAVE) ---
        augment=True,
        hsv_h=0.015,  # Cambios leves de tono
        hsv_s=0.7,  # Simula colores lavados por luz intensa (reflejos)
        hsv_v=0.4,  # Variación de brillo extrema para ignorar destellos
        degrees=10.0,  # Rotación leve para señales en curvas de la pista
        perspective=0.0001,  # Efecto 3D de profundidad

        # --- REGLA DE ORO PARA SEÑALES DIRECCIONALES ---
        flipud=0.0,  # PROHIBIDO: Evita que el robot confunda flechas arriba/abajo
        fliplr=0.0,  # PROHIBIDO: Evita que confunda flechas izquierda/derecha

        # --- MEZCLA DE DATOS (DATA MIXING) ---
        mosaic=0.5,  # Mezcla imágenes para que no dependa de un solo fondo
        mixup=0.2,  # Ayuda a ver señales a través de "ruido" visual
        copy_paste=0.5,  # Pega señales en fondos aleatorios para eliminar error de background
        #blur=0.1,  # Simula vibración o desenfoque de la cámara del robot

        # --- LOGÍSTICA DE PROYECTO ---
        project="Arabots_Vision_Project",
        name="RTDETR_L_AntiReflex_Final",
        exist_ok=True,
        plots=True,  # Genera gráficas y matriz de confusión para análisis
        save=True,  # Guarda los mejores pesos (.pt) automáticamente
        val=True  # Validación en cada época para monitorear el éxito
    )

    print("\n✅ ENTRENAMIENTO COMPLETO: Modelo optimizado para el Vision Centric Challenge.")


if __name__ == "__main__":
    # Verificación de seguridad antes de iniciar
    if os.path.exists(DATA_YAML):
        print(f"🚀 Iniciando entrenamiento maestro en Novi, MI...")
        entrenar_maestro_antireflejos()
    else:
        print(f"❌ Error crítico: No se encontró el archivo {DATA_YAML}")
        print("Asegúrate de que la ruta del dataset sea correcta para evitar el Background Error.")