
import io
import os
##subimos la credencial para acceder

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= "credencial.json"
#importamos la libreria que instalamos

from google.cloud import vision

# iniciamos el cliente
client = vision.ImageAnnotatorClient()

#le damos el nombre del file que vamos a mandar analizar
file_name = os.path.abspath('Space Invaiders/catapillar-damage-to-leaves.jpg')

# cargamos la imagen a memoria
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# buscamos los labels en la imagen
response = client.label_detection(image=image)
labels = response.label_annotations

#imprimimos los labels de la imagen
print('Labels:')
for label in labels:
    print(label.description)