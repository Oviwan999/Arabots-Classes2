import os
import shutil

base = r"C:\git\Arabots-Classes2\Vision2026\Test"
images_train = os.path.join(base, "images", "train")
images_val   = os.path.join(base, "images", "val")

labels_root  = os.path.join(base, "labels")          # donde están sueltos
labels_train = os.path.join(base, "labels", "train") # destino
labels_val   = os.path.join(base, "labels", "val")   # destino

os.makedirs(labels_train, exist_ok=True)
os.makedirs(labels_val, exist_ok=True)

moved_train = 0
moved_val = 0
skipped = 0

for fname in os.listdir(labels_root):
    if not fname.lower().endswith(".txt"):
        continue

    src = os.path.join(labels_root, fname)
    stem = os.path.splitext(fname)[0]

    # Busca la imagen correspondiente (jpg/png/jpeg)
    found_train = any(os.path.exists(os.path.join(images_train, stem + ext)) for ext in [".jpg", ".jpeg", ".png"])
    found_val   = any(os.path.exists(os.path.join(images_val,   stem + ext)) for ext in [".jpg", ".jpeg", ".png"])

    if found_train and not found_val:
        shutil.move(src, os.path.join(labels_train, fname))
        moved_train += 1
    elif found_val and not found_train:
        shutil.move(src, os.path.join(labels_val, fname))
        moved_val += 1
    elif found_train and found_val:
        # raro: mismo nombre en train y val
        skipped += 1
    else:
        # no hay imagen con ese nombre en train ni val
        skipped += 1

print("Movidos a train:", moved_train)
print("Movidos a val:", moved_val)
print("Saltados (sin match o duplicados):", skipped)
