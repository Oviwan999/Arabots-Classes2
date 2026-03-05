from rq.cli import worker
from sympy import false
from ultralytics import YOLO
import os
##print("Existe data.yaml?", os.path.exists(r"C:\git\Arabots-Classes2\Vision2026\data.yaml"))

model = YOLO("yolo11s.pt")
if __name__ == "__main__":
    model.train(
        data=r"C:\git\Arabots-Classes2\Vision2026\data.yaml",
        epochs=150,
        imgsz=1024,
        batch=16,
        augment=True,
        degrees=15,
        perspective=0.0001,
        flipud=0.0,
        fliplr=0.0,
        mosaic=1.0,
        mixup=0.1,
        copy_paste=0.3,
        dropout=0.15,
        patience=0,
        auto_augment=None,
        cache=False,
        warmup_epochs=3.0,
        box=12.0,
        cls=4.0,
        label_smoothing=0.0,
        optimizer="auto",
        lr0=0.001,
        close_mosaic=20,
        name="Vision2026_v2",
        device=0,
        workers=4,
        amp=True,
        plots=True

)

