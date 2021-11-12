# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
from datetime import datetime
from datetime import timedelta
import json
import random
import requests
import time

class ActionQueComprar(Action):

     def name(self) -> Text:
         return "action_que_comprar"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        mayorista = tracker.get_slot("mayorista")
        message = "quiero comprar "
        with open("compras_mayorista.json", 'r') as contenido:
            datos = json.load(contenido)
            stock_maximo = 1000
            with open ("Productos.json", 'r+') as p_minorista:
                minorista = json.load(p_minorista)
                for producto in datos[mayorista]:
                    i = 0
                    while minorista["productos"][i]["nombre"] != producto:
                        i += 1
                    if minorista["productos"][i]["stock"] < stock_maximo:
                        solicitado = stock_maximo - minorista["productos"][i]["stock"]
                        message = message + f"{solicitado} bultos de {producto} "
                        minorista["productos"][i]["stock"] += solicitado
                #Aumento el stock de los productos
                p_minorista.seek(0)
                json.dump(minorista, p_minorista, indent=4)
        dispatcher.utter_message(text=message)
        return[]

class ActionElegirHacer(Action):

     def name(self) -> Text:
         return "action_elegir_que_hacer"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        if tracker.get_slot("usuario") != None:
            loggeado = True
        else:
            loggeado = False
        
        comprado = tracker.get_slot("compra")
        consulta = tracker.get_slot("consulta")
        mayorista = tracker.get_slot("mayorista")

        print("En action elegir_que_hacer")
        if loggeado == False:
            dispatcher.utter_message(text="quiero iniciar sesion en mi cuenta")
            if mayorista == None:
                mayorista = next(tracker.get_latest_entity_values("mayorista"), None)
                return[SlotSet("usuario", "Monarca"), SlotSet("compra", False), SlotSet("consulta", False), SlotSet("mayorista", mayorista)]
            else:
                return[SlotSet("usuario", "Monarca"), SlotSet("compra", False), SlotSet("consulta", False)]
        else:
            if comprado == False:
                dispatcher.utter_message(text="me gustaria realizar un pedido")
                return[SlotSet("compra", True)]
            else:
                if consulta == False:
                    dispatcher.utter_message(text="quiero saber cuales son los horarios de atencion al cliente")
                    return[SlotSet("consulta", True)]
                else:
                    dispatcher.utter_message(text="Eso seria todo, muchas gracias")

        return []
    
class ActionConsultarStock(Action):

    def name(self) -> Text:
        return "action_stock"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open('Productos.json', 'r') as contenido:
            productos = json.load(contenido)
            dispatcher.utter_message(text= "Este es el catalogo actualizado de nuestros productos:\n")
            for producto in productos["productos"]:
                dispatcher.utter_message(text = "| \t Producto: " + producto["nombre"] + "\n")
                dispatcher.utter_message(text = "| \t Precio individual: " + str(producto["individual"]) + " \n")
                dispatcher.utter_message(text = "| \t Precio bulto: " + str(producto["preciobulto"]) + " \n")
                dispatcher.utter_message(text = "| \t Stock: "+ str(producto["stock"]) +" \n")
                dispatcher.utter_message(text = "--------------------------------------\n")
        return []


# -------------------------------------- ACCIONES NO USADAS -------------------------------------

class ActionRealizarPedido(Action):
    def name(self) -> Text:
        return "action_realizar_pedido"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user = tracker.get_slot('usuario')
        usermessage = tracker.latest_message['text']
        produc = tracker.latest_message['entities']
        #Consigue las cantidades de cada uno de los productos que se desea comprar
        unidad = [int(s) for s in usermessage.split() if s.isdigit()]
        print(unidad)
        print(produc)
        carrito = []
        i = 0
        while i < len(produc):
            y = {
                "producto": produc[i]["value"],
                "unidades": unidad[i],
                "precio_unidad": 0
            }
            carrito.append(y)
            i += 1

        compra_aceptada = True
        #Revisa si hay stock de los productos a comprar
        with open("Productos.json", 'r+') as p:
            datos_prod = json.load(p)
            z = 0
            while z < len(carrito):
                j = 0
                while j < len(datos_prod["productos"]) and carrito[z]["producto"] != datos_prod["productos"][j]["nombre"]:
                    j = j+1
                if j < len(datos_prod["productos"]) and carrito[z]["producto"] == datos_prod["productos"][j]["nombre"]:

                    if datos_prod["productos"][j]["stock"] == carrito[z]["unidades"]:
                        print("Problema stock")
                        produc = carrito[z]["producto"]
                        compra_aceptada = False
                        message = f"No hay suficientes unidades de {produc} para efectuar la compra"
                        dispatcher.utter_message(text=message)
                    else:
                        carrito[z]["precio_unidad"] = datos_prod["productos"][j]["individual"]
                else:
                    no_vende = carrito[z]["producto"]
                    message = f"El elemento {no_vende} que desea comprar no se encuentre en nuestro catalogo"
                    dispatcher.utter_message(text=message)
                    compra_aceptada = False

                z += 1
                    
            #Si hay stock de los productos, se guarda la compra en la cuenta y se pasa al metodo de pago 
        if compra_aceptada:
            print(f"compra:{compra_aceptada}")
            npedido = random.randint(1000, 9999)
            date = datetime.today() + timedelta(days = random.randint(1, 20))
            date = date.strftime("%d/%m/%Y")
            total = 0
            for elemento in carrito:
                total += (elemento["precio_unidad"] * elemento["unidades"])

            #Se reduce el stock de los productos
            with open("Productos.json", 'r+') as p:
                datos_prod = json.load(p)
                for elemento in carrito:
                    j = 0
                    while elemento["producto"] != datos_prod["productos"][j]["nombre"]:
                        j = j+1
                    if datos_prod["productos"][j]["stock"] <= elemento["unidades"]:
                        datos_prod["productos"][j]["stock"] = 0
                    elif datos_prod["productos"][j]["stock"] > elemento["unidades"]:
                        datos_prod["productos"][j]["stock"] -= elemento["unidades"]
                p.seek(0)
                json.dump(datos_prod, p, indent=4)

            message = f"El numero de pedido es {npedido}. Su pedido llegara el {date}\nEL total a pagar es {total} + envio.\nPor favor ingrese al siguiente link y coloque sus datos para completar el pago: https://www.completarpedido.com\nGracias por comprar con nosotros!"
            dispatcher.utter_message(text=message)
        return[]

class ActionInteraccionMayorista(Action):
    def name(self) -> Text:
        return "action_mayorista"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


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


        #insatncio 'message' que es el primer mensaje que le voy a enviar al bot
        message = 'Hola'
        print(s1 + ': ' + message)
        last_message_minorista = ""
        while last_message_minorista != "Eso seria todo, muchas gracias": 
            #ciclo infinitamente para que los bots se comuniquen
            #llamo a la funcion send_mesagge y le paso el mensaje, el nombre del bot que envia el mensaje y el puerto del bot al que le voy a enviar el mensaje 
            message = send_mesagge(message, s1, p2)
            print(s2 + ': ' + message)
            #llamo a la funcion send_mesagge y le paso el mensaje, el nombre del bot que envia el mensaje y el puerto del bot al que le voy a enviar el mensaje
            message = send_mesagge(message, s2, p1) 
            last_message_minorista = message
            print(s1 + ': ' + message)
        
        dispatcher.utter_message(text= "Interaccion terminada")
        return[]