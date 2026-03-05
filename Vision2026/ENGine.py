from ultralytics import YOLO

model = YOLO(r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Vision2026_v24\weights\best.pt")

model.export(format="engine", device=0, half=True)