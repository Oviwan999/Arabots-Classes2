from ultralytics import RTDETR

def generar_engine_batch_7():
    # Cargar pesos originales
    model = RTDETR(r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Arabots_RTDETR_2026\RTDETR_L_Novi_V1\weights\best.pt")

    print("🚀 Compilando Engine para 7 ángulos (Batch=7)...")

    # Exportación optimizada
    model.export(
        format="engine",
        imgsz=800,
        batch=7,         # <--- CLAVE: Ahora acepta tus 7 variantes de rotación
        half=True,        # FP16 para velocidad máxima
        device=0,
        simplify=True
    )
    print("✅ Engine Batch=7 listo.")

if __name__ == "__main__":
    generar_engine_batch_7()