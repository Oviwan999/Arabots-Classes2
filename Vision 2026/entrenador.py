from multiprocessing.pool import worker

from sympy import false
from ultralytics import YOLO
import os
##print("Existe data.yaml?", os.path.exists(r"C:\git\Arabots-Classes2\Vision2026\data.yaml"))

model = YOLO("yolo11s.pt")

if __name__ == "__main__":
    model.train(
        data="data.yaml",
        epochs=100,
        imgsz=800,
        batch=8,
        augment=True,
        degrees=20,
        perspective=0.0005,
        flipud=0.0,
        fliplr=0.0,
        mosaic=1.0,
        mixup=0.1,
        copy_paste=0.1,
        dropout=0.15,
        patience=30,
        auto_augment=None,
        cache=False,
        warmup_epochs=3.0,
        box=10.0,
        cls=2.5,
        label_smoothing=0.1,
        optimizer="auto",
        lr0=0.001,
        close_mosaic=20,
        name="Vision2026_v2",
        device=0,
        workers=0,

    )