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

def send_mesagge(msg, sender, port):

    # direccion del localhost en el que se encuentra el servidor de rasa
    url = 'http://localhost:'+str(port)+'/webhooks/rest/webhook'

    #objeto json que se enviara al servidor de rasa
    data = {"sender": sender, "message": msg} 

    #envio mediante post el objeto json al servidor de rasa
    x = requests.post(url, json=data) 
    #obtengo la respuesta del servidor de rasa
    rta = x.json() 

    
    if x.status_code == 200: 
        #si el status es 200, entonces contesto bien
        #retorno el texto de la respuesta
        return rta.pop(0)['text'] 
    else: 
        #si el status no es 200 hubo un error
        #imprimo el error por pantalla
        print(x.raw) 
        return None 
    
"""
    INSTANCIO EL BOT 1
"""
#puerto del bot 1
p1 = 5006
#nombre que le voy a dar al bot 1
s1 = 'Minorista'


"""
    INSTANCIO EL BOT 2
"""
#puerto del bot 2
p2 = 5005
#nombre que le voy a dar al bot 2
s2 = 'Mayorista' 


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
    if mensaje == "rellena stock":
        #insatncio 'message' que es el primer mensaje que le voy a enviar al bot
        message = 'Hola'
        print(s1 + ': ' + message)
        while message != "Eso seria todo, muchas gracias": 
            time.sleep(1)
            #ciclo infinitamente para que los bots se comuniquen
            #llamo a la funcion send_mesagge y le paso el mensaje, el nombre del bot que envia el mensaje y el puerto del bot al que le voy a enviar el mensaje 
            message = send_mesagge(message, s1, p2)
            print(s2 + ': ' + message)
            time.sleep(1)
            #llamo a la funcion send_mesagge y le paso el mensaje, el nombre del bot que envia el mensaje y el puerto del bot al que le voy a enviar el mensaje
            message = send_mesagge(message, s2, p1) 
            print(s1 + ': ' + message)