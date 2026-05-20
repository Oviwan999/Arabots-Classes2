from ultralytics import YOLO

model = YOLO(r"C:\git\Arabots-Classes2\Vision2026\runs\detect\Arabots_RTDETR_2026\RTDETR_L_Novi_V1\weights\best.pt")

model.export(format="engine", device=0, half=True)