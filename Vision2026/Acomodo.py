import os
import random
import shutil

# Configuración
carpeta_original = 'Test/images' # Pon aquí el nombre de tu carpeta
destino = 'Test'
train_percent = 0.8  # 80% para entrenamiento

# Crear estructura de carpetas YOLO
for folder in ['images/train', 'images/val', 'labels/train', 'labels/val']:
    os.makedirs(os.path.join(destino, folder), exist_ok=True)

# Listar todas las imágenes (asumiendo que imagen y .txt tienen mismo nombre)
imagenes = [f for f in os.listdir(carpeta_original) if f.endswith(('.jpg', '.png', '.jpeg'))]
random.shuffle(imagenes)

limit = int(len(imagenes) * train_percent)
train_files = imagenes[:limit]
val_files = imagenes[limit:]

def mover_archivos(lista, subfijo):
    for f in lista:
        # Mover Imagen
        shutil.copy(os.path.join(carpeta_original, f), os.path.join(destino, f'images/{subfijo}', f))
        # Mover Etiqueta (.txt)
        txt_name = os.path.splitext(f)[0] + '.txt'
        if os.path.exists(os.path.join(carpeta_original, txt_name)):
            shutil.copy(os.path.join(carpeta_original, txt_name), os.path.join(destino, f'labels/{subfijo}', txt_name))

mover_archivos(train_files, 'train')
mover_archivos(val_files, 'val')

print(f"¡Listo! {len(train_files)} fotos a train y {len(val_files)} a val.")