from ultralytics import RTDETR


def generar_engine_extremo_batch_13():
    model = RTDETR(r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Arabots_RTDETR_2026\RTDETR_L_Novi_V1\weights\best.pt")
    print("🚀 Compilando Engine Ultra-Rotación (Batch=13)...")

    model.export(
        format="engine",
        imgsz=800,
        batch=13,  # 13 ángulos en un solo disparo
        half=True,  # FP16 para velocidad máxima en la 4060
        device=0,
        simplify=True
    )
    print("✅ Engine Batch=13 completado.")


if __name__ == "__main__":
    generar_engine_extremo_batch_13()