import json,os,requests

#estos son los codigos de acceso para que se conecte con la api de azure
subscription_key="16173823f64b4be0a1455fd78686a6dc"
# este es el url de acceso al servicio de azure
face_api_url = "https://facerecognitionmna23rodrigo.cognitiveservices.azure.com/"+"face/v1.0/detect"

#este es el url de la imagen que vamos a analizar
image_url = "https://i0.wp.com/imgs.hipertextual.com/wp-content/uploads/2019/11/hipertextual-100-000-caras-que-realidad-no-existen-2019554542.jpg?w=1500&quality=50&strip=all&ssl=1"

#este es la forma en la que se envia la peticion a la api con el acceso y la imagen
headers = {'Ocp-Apim-Subscription-Key': subscription_key}

params = {
    'returnFaceId': 'false',
    'returnFaceLandmarks': 'false',
    #"returnFaceAttributes":"age,gender,headPose,smile,facialHair,glasses,emotion"
}
#esta es la forma en lq que le pedimso que nos entrege la informacion de la imagen

response = requests.post(face_api_url, params=params, headers=headers, json={"url": image_url})
print(json.dumps(response.json()))