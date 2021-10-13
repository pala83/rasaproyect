import requests
import time

#puerto del bot que se va a comunicar con un humano
port = 5006

#url del server rasa
url = 'http://localhost:'+str(port)+'/webhooks/rest/webhook' 


def response(mensaje):
    #creo el objeto json para enviarle al server rasa
    myobj = {
    "message": str(mensaje),
    "sender": "cliente"
    }
    #envio el mensaje al server rasa
    request_response = requests.post(url, json = myobj)
    #retorno la respuesta completa del server rasa
    return request_response 


while True:
    mensaje= input('¿Mensaje?: ')
    if mensaje == "/stop": #si el menasje es '/stop' se sale del programa. Como en 'rasa shell'
        break
    chat_recibidos=response(mensaje).json() #envio el mesnaje al bot y recibo la respuesta
    for chat in chat_recibidos: #esto es por si se recibe mas de un mensaje
        if 'text' in chat: #verifica si existe el campo text, ya que podemos recibir una imagen
            textReceive=chat['text'] #obtiene la respuesat del bot si es un mensaje
            print(textReceive) #imprime la respuesta del bot
        if 'image' in chat: #verifica si existe el campo text, ya que podemos recibir una imagen
            imageReceive=chat['image'] #obtiene la respuesat del bot si es una imagen
            print(imageReceive) #imprime la imagen que envio del bot