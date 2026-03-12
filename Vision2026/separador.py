import os
import shutil

# ========= CONFIG =========
base_path = r"C:\git\Arabots-Classes2\Vision2026\Test"
output_path = r"C:\git\Arabots-Classes2\Vision2026\Train_SoloClase"

class_id_to_keep = 2  # <-- CAMBIA ESTE NÚMERO

image_exts = [".jpg", ".jpeg", ".png", ".webp"]

# ========= RUTAS =========
labels_dir = os.path.join(base_path, "labels", "train")
images_dir = os.path.join(base_path, "images", "train")

out_labels_dir = os.path.join(output_path, "labels")
out_images_dir = os.path.join(output_path, "images")

os.makedirs(out_labels_dir, exist_ok=True)
os.makedirs(out_images_dir, exist_ok=True)

# ========= FUNCION =========
def find_image(stem):
    for ext in image_exts:
        img_path = os.path.join(images_dir, stem + ext)
        if os.path.exists(img_path):
            return img_path
    return None

# ========= PROCESO =========
copiadas = 0

for label_file in os.listdir(labels_dir):
    if not label_file.endswith(".txt"):
        continue

    label_path = os.path.join(labels_dir, label_file)

    with open(label_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Filtrar solo la clase deseada
    new_lines = [l for l in lines if l.startswith(str(class_id_to_keep) + " ")]

    if new_lines:
        # Guardar label filtrado
        out_label_path = os.path.join(out_labels_dir, label_file)
        with open(out_label_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        # Copiar imagen correspondiente
        stem = os.path.splitext(label_file)[0]
        img_path = find_image(stem)

        if img_path:
            shutil.copy2(img_path, os.path.join(out_images_dir, os.path.basename(img_path)))
            copiadas += 1

print(f"\n✅ LISTO. Se copiaron {copiadas} imágenes a:")
print(output_path)