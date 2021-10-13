# This files contains your custom actions which can be used to run
# custom Python code.
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

class ActionConsulta(Action):

    def name(self) -> Text:
        return "action_consultar"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        consulta = next(tracker.get_latest_entity_values("consulta"), None)
        if str(consulta)=="precio" or str(consulta)=="disponibilidad":
            with open('Productos.json', 'r') as contenido:
                productos = json.load(contenido)
                dispatcher.utter_message(text= "Este es el catalogo actualizado de nuestros productos:\n")
                for producto in productos["productos"]:
                    dispatcher.utter_message(text = "| \t Producto: " + producto["nombre"] + "\n")
                    dispatcher.utter_message(text = "| \t Precio individual: " + str(producto["Individual"]) + " \n")
                    dispatcher.utter_message(text = "| \t Precio bulto: " + str(producto["preciobulto"]) + " \n")
                    dispatcher.utter_message(text = "| \t Stock: "+ str(producto["stock"]) +" \n")
                    dispatcher.utter_message(text = "--------------------------------------\n")
        elif str(consulta)=="horarios":
            message="Los horarios de atencion al cliente son de 8:00 a 17:00\nSi quieres contactarte con nosotros, nuestro numero de telefono es: 0-800-rasahelp"
            dispatcher.utter_message(text=message)
        elif str(consulta)=="historial":
            if tracker.get_slot("usuario") != None:
                user = tracker.get_slot("usuario")
                with open('Cuentas.json', 'r') as acc:
                    datos = json.load(acc)
                    i = 0
                    while i < len(datos["cuentas"]) and datos["cuentas"][i]["user"] != user:
                        i = i+1
                    dispatcher.utter_message(text="Estas son tus compras con sus respectivas fechas de entrega:\n ")
                    for codigo in datos["cuentas"][i]["compras"]:
                        j = 0
                        while j < len(datos["envios"]) and datos["envios"][j]["npedido"] != codigo:
                            j = j+1
                        fentrega = datos["envios"][j]["entrega"]
                        message = f" \nNumero de pedido: {codigo}.\nFecha de entrega: {fentrega}\nProductos:\n"
                        for elemento in datos["envios"][j]["carrito"]:
                            producto = elemento["producto"]
                            cantidad = elemento["unidades"]
                            precio_unidad = elemento["Individual"]
                            message = message + f" -{producto} x{cantidad} unidades (${precio_unidad} por unidad)\n"
                        if datos["envios"][j]["cobro_envio"] == True:
                            valor_envio = datos["valor_envio"]
                            message = message + f"Se cobro el costo de envio: ${valor_envio}\n"
                        else:
                            message = message + "No se cobro el envio\n"
                        total = datos["envios"][j]["valor_total"]
                        message = message + f" \nPrecio total: ${total}\n"
                        dispatcher.utter_message(text=message)
            else:
               dispatcher.utter_message(text="Debes iniciar sesion si quieres ver el historial de compras de tu cuenta.")
        return []

#------------------------------------------------------------------

class ActionRenovarStock(Action):
    def name(self) -> Text:
        return "action_comprar" #Nueva action en el Domain
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open("Productos.json", 'r') as contenido:
            productos = json.load(contenido)
            stock_maximo = 1000
            message = "quiero comprar "
            for producto in productos["productos"]:
                if producto["stock"] < stock_maximo:
                    solicitado = stock_maximo - producto["stock"]
                    message += str(solicitado) + " " + producto["nombre"] + ", "
            message = message[0:(len(message)-2)]
            dispatcher.utter_message(text=message)
        return[SlotSet("compras", message)] #Crear el slot "compras"

class ActionRealizarPedido(Action):
    def name(self) -> Text:
        return "action_renovar_stock"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        modificador = tracker.get_slot('compras')
        produc = tracker.latest_message['entities']
        unidad = [int(numero) for numero in modificador.split() if numero.isdigit()]
        with open("Productos.json", 'r+') as contenido:
            productos = json.load(contenido)
            i=0
            for producto in produc["value"]:
                for elemento in productos["productos"]:
                    if elemento["nombre"] == producto:
                        elemento["stock"] += unidad[i]
        dispatcher.uttter_message(text = "muchas gracias")
        return[]
        
#-------------------------------------------------------------------

# - Si se le da un numero de pedido, devolvera la fecha en la que sera entregado
class ActionConsultarEnvio(Action):

    def name(self) -> Text:
        return "action_consultar_envio"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        npedido = next(tracker.get_latest_entity_values("numero_pedido"), None)
        cont_ansioso = tracker.get_slot("ansioso")
        with open("Cuentas.json", 'r+') as acc:
            datos = json.load(acc)
            i = 0
            while i < len(datos["envios"]) and npedido != str(datos["envios"][i]["npedido"]):
                i += 1
            if i < len(datos["envios"]) and npedido == str(datos["envios"][i]["npedido"]):
                fecha = datos["envios"][i]["entrega"]
                message = f"El pedido con numero {npedido}, esta programado para llegar el dia {fecha}"
                dispatcher.utter_message(text=message)
                if cont_ansioso == None:
                    print("Contador ans: 1")
                    return[SlotSet("ansioso", 1)]
                else:
                    if cont_ansioso < 4:
                        cont_ansioso += 1
                        print(f"Contador ans: {cont_ansioso}")
                        return[SlotSet("ansioso", cont_ansioso)]
                    elif cont_ansioso == 4:
                        cont_ansioso += 1
                        print("Contador ans: 5")
                        dispatcher.utter_message(text="Parece que estas consultando mucho por este envio, vere si puedo apresurar un poco el tramite")
                        fecha = datetime.strptime(fecha, "%d/%m/%Y")
                        fecha = fecha - timedelta(days = 2)
                        fecha = fecha.strftime("%d/%m/%Y")
                        datos["envios"][i]["entrega"] = fecha
                        acc.seek(0)
                        json.dump(datos, acc, indent=4)
                        return[SlotSet("ansioso", cont_ansioso)]
            else:
                message = f"El numero {npedido}, no pertenece a ningun envio de productos que se haya realizado recientemente \nQuiza no escribiste bien el numero, vuelve a intentarlo"
                dispatcher.utter_message(text=message)

        return []

# - Realiza el pedido del usuario, revisa si hay stock de los productos en el carrito
#   Y si los hay prepara el pedido, guardando la compra en su cuenta
# - Si para AL MENOS uno de los productos del carrito no hay stock, se cancela el pedido
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
                "Individual": 0
            }
            carrito.append(y)
            i += 1
        with open('Cuentas.json', 'r+') as acc:
            datos = json.load(acc)
            i = 0
            while datos["cuentas"][i]["user"] != user:
                i = i+1
            if datos["cuentas"][i]["user"] == user:
                    compra_aceptada = True

                    #Revisa si hay stock de los productos a comprar
                    with open("Productos.json", 'r') as p:
                        datos_prod = json.load(p)
                        z = 0
                        while z < len(carrito):
                            j = 0
                            while j < len(datos_prod["productos"]) and carrito[z]["producto"] != datos_prod["productos"][j]["nombre"]:
                                j = j+1
                            if j < len(datos_prod["productos"]) and carrito[z]["producto"] == datos_prod["productos"][j]["nombre"]:

                                if datos_prod["productos"][j]["stock"] == 0:
                                    print("Problema stock")
                                    produc = carrito[z]["producto"]
                                    message = f"No hay suficientes unidades de {produc} para efectuar la compra"
                                    compra_aceptada = False
                                    dispatcher.utter_message(text=message)
                                else:
                                    carrito[z]["Individual"] = datos_prod["productos"][j]["preciobulto"]
                            else:
                                no_vende = carrito[z]["producto"]
                                message = f"El elemento {no_vende} que desea comprar no se encuentre en nuestro catalogo"
                                dispatcher.utter_message(text=message)
                                compra_aceptada = False

                            z += 1
                    
                    #Si hay stock de los productos, se guarda la compra en la cuenta y se pasa al metodo de pago 
                    if compra_aceptada:
                        print(f"compra:{compra_aceptada}")
                        datos["cuentas"][i]["n_compras"] = datos["cuentas"][i]["n_compras"]+1
                        npedido = random.randint(1000, 9999)
                        datos["cuentas"][i]["compras"].append(npedido)
                        date = datetime.today() + timedelta(days = random.randint(1, 20))
                        date = date.strftime("%d/%m/%Y")
                        total = 0
                        for elemento in carrito:
                            total += (elemento["Individual"] * elemento["unidades"])

                        y = {
                        "npedido": npedido,
                        "carrito": carrito,
                        "valor_total": total,
                        "entrega": str(date),
                        "cobro_envio": False
                        }
                        datos["envios"].append(y)
                        acc.seek(0)
                        json.dump(datos, acc, indent=4)

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
                        
                        return[SlotSet("compra_aceptada", "true")]
                    else:
                        print(f"compra:{compra_aceptada}")
                        return[SlotSet("compra_aceptada", "false")]

# - Si se detecta que ya se ha pagado con algun metodo de pago previamente
#   el bot consulta si se desea utilizar los mismos datos
class ActionMetodoPago(Action):
    def name(self) -> Text:
        return "action_metodo_pago"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("usuario") == None:
            dispatcher.utter_message(text="Error de stories")
        else:
            user = tracker.get_slot('usuario')
            with open('Cuentas.json', 'r') as acc:
                datos = json.load(acc)
                i = 0
                while i < len(datos["cuentas"]) and datos["cuentas"][i]["user"] != user:
                    i = i+1
                if i < len(datos["cuentas"]) and datos["cuentas"][i]["user"] == user:
                    metodo = datos["cuentas"][i]["metodo_pago_fav"]
                    message = f"En tu ultima compra pagaste con {metodo}, te gustaria volver a comprar de la misma forma?"
                    dispatcher.utter_message(text=message)
                else:
                    print("ERROR: Este error no deberia suceder")

        return []

# - Realiza el pago de los productos consiguiendo el metodo de pago
#   desde las entidades, luego lo guarda como metodo de pago favorito en la cuenta del usuario
class ActionPagar(Action):

    def name(self) -> Text:
        return "action_efectuar_pago"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user = tracker.get_slot('usuario')
        i = 0
        with open('Cuentas.json', 'r+') as acc:
            datos = json.load(acc)
            while datos["cuentas"][i]["user"] != user:
                i = i+1

            mpago = next(tracker.get_latest_entity_values("mpago"), None)
            n = len(datos["cuentas"][i]["compras"])-1
            npedido = datos["cuentas"][i]["compras"][n]
            ncompras = datos["cuentas"][i]["n_compras"]
            m = len(datos["envios"])-1
            date = datos["envios"][m]["entrega"]
            datos["cuentas"][i]["metodo_pago_fav"] = mpago

            #Si no se cobra envio entonces el valor total se queda igual
            if datos["cuentas"][i]["n_compras"] % 5 == 0: #No se cobra el envio cada 5 compras en el mayorista
                total = datos["envios"][m]["valor_total"]
                message = f"FELICIDADES! Esta es tu compra numero {ncompras}, por lo tanto no te cobraremos el envio de este pedido.\nPor favor, ingrese al siguiente link y complete el formulario con sus datos para completar la compra.\n \nEl numero de pedido es {npedido}.\nSu pedido llegara el {date}\nValor total: {total}\nMuchas gracias por su compra."
                dispatcher.utter_message(text=message)   
            else:
            #Si se cobra envio, se suma el costo del envio al valor total de la compra
                datos["envios"][m]["cobro_envio"] = True
                envio = datos["valor_envio"]
                datos["envios"][m]["valor_total"] += envio
                total = datos["envios"][m]["valor_total"]
                message = f"Por favor, ingrese al siguiente link y complete el formulario con sus datos para completar la compra.\n \nEl numero de pedido es {npedido}.\nSu pedido llegara el {date}\nValor total (incluye envio): {total}\nMuchas gracias por su compra." 
                dispatcher.utter_message(text=message)

            
            acc.seek(0)
            json.dump(datos, acc, indent=4)
            acc.truncate()

        return [SlotSet("nuevo", "false")]

# - Lo mismo que la accion de pago 1 pero obteniendo el metodo de pago del json en vez de por las entidades
#   y no cambia el slot de "nuevo"
class ActionPagar2(Action):

    def name(self) -> Text:
        return "action_efectuar_pago2"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user = tracker.get_slot('usuario')
        i = 0
        with open('Cuentas.json', 'r+') as acc:
            datos = json.load(acc)
            while datos["cuentas"][i]["user"] != user:
                i = i+1

            n = len(datos["cuentas"][i]["compras"])-1
            npedido = datos["cuentas"][i]["compras"][n]
            ncompras = datos["cuentas"][i]["n_compras"]
            m = len(datos["envios"])-1
            date = datos["envios"][m]["entrega"]
            mpago = datos["cuentas"][i]["metodo_pago_fav"]

            #Si no se cobra envio entonces el valor total se queda igual
            if datos["cuentas"][i]["n_compras"] % 5 == 0: #No se cobra el envio cada 5 compras en el mayorista
                total = datos["envios"][m]["valor_total"]
                message = f"FELICIDADES! Esta es tu compra numero {ncompras}, por lo tanto no te cobraremos el envio de este pedido.\nPor favor, ingrese al siguiente link y complete el formulario con sus datos para completar la compra.\n \nEl numero de pedido es {npedido}.\nSu pedido llegara el {date}\nValor total: {total}\nMuchas gracias por su compra."
                dispatcher.utter_message(text=message)   
            else:
            #Si se cobra envio, se suma el costo del envio al valor total de la compra
                datos["envios"][m]["cobro_envio"] = True
                envio = datos["valor_envio"]
                datos["envios"][m]["valor_total"] += envio
                total = datos["envios"][m]["valor_total"]
                message = f"Por favor, ingrese al siguiente link y complete el formulario con sus datos para completar la compra.\n \nEl numero de pedido es {npedido}.\nSu pedido llegara el {date}\nValor total (incluye envio): {total}\nMuchas gracias por su compra." 
                dispatcher.utter_message(text=message)

            acc.seek(0)
            json.dump(datos, acc, indent=4)
            acc.truncate()

        return []

#--------------------->> Formularios de inicio de sesion y registro <<---------------------

# - Valida el formulario de inicio de sesion y no sale del loop hasta que los datos ingresados por el usuario sean correctos.
class ValidateLoginForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_login_form"

    def validate_usuario(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """validate 'usuario' value"""

        #Revisa si el usuario ingresado ya tiene una cuenta a su nombre
        print(f"Usuario ingresado: {slot_value}")
        with open('Cuentas.json', 'r') as acc:
            datos = json.load(acc)
            i = 0
            while i < len(datos["cuentas"]) and datos["cuentas"][i]["user"] != str(slot_value):
                i = i+1
            if i < len(datos["cuentas"]) and slot_value == datos["cuentas"][i]["user"]:
                return {"usuario": slot_value}
            else:
                dispatcher.utter_message(text=f"Usuario no registrado")
                return {"usuario": None}

    def validate_nuevo(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """validate 'nuevo' value"""

        #Revisa si el usuario ingresado ya tiene una cuenta a su nombre
        print(f"Contrasena ingresada: {slot_value}")
        with open('Cuentas.json', 'r') as acc:
            user = tracker.get_slot('usuario')
            datos = json.load(acc)
            i = 0
            while datos["cuentas"][i]["user"] != user:
                i = i+1
            if slot_value == str(datos["cuentas"][i]["password"]):
                message = f"Bienvenido/a, {user}, espero poder ayudarte."
                dispatcher.utter_message(text=message)
                if datos["cuentas"][i]["n_compras"] == 0:
                    print("nuevo: true")
                    return {"nuevo": "true"}
                else:
                    print("nuevo: false")
                    return {"nuevo": "false"}
            else:
                dispatcher.utter_message(text=f"Contrasena incorrecta")
                return {"nuevo": None}



# - Valida el formulario de registro, si el usuario ingresado ya tiene una cuenta registrada, vuelve a preguntar
class ValidateRegForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_reg_form"

    def validate_usuario(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """validate 'usuario' value"""

        #Revisa si el usuario ingresado ya tiene una cuenta a su nombre
        print(f"Usuario ingresado: {slot_value}")
        with open('Cuentas.json', 'r+') as acc:
            datos = json.load(acc)
            i = 0
            while i < len(datos["cuentas"]) and datos["cuentas"][i]["user"] != str(slot_value):
                i = i+1
            if i >= len(datos["cuentas"]):
                y = {
                    "user": slot_value,
                    "password": None,
                    "metodo_pago_fav": None,
                    "n_compras": 0,
                    "compras": []
                }
                datos["cuentas"].append(y)
                acc.seek(0)
                json.dump(datos, acc, indent=4)
                return {"usuario": slot_value}
            else:
                dispatcher.utter_message(text=f"Usuario ya registrado")
                return {"usuario": None}

    def validate_nuevo(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """validate 'contr' value"""

        #Si la password es un string vacio, la reconoce como no valida
        print(f"Contrasena ingresada: {slot_value}")
        with open('Cuentas.json', 'r+') as acc:
            user = tracker.get_slot('usuario')
            datos = json.load(acc)
            i = 0
            while datos["cuentas"][i]["user"] != user:
                i = i+1
            if slot_value != "":
                datos["cuentas"][i]["password"] = slot_value
                acc.seek(0)
                json.dump(datos, acc, indent=4)
                return {"nuevo": "true"}
            else:
                dispatcher.utter_message(text=f"Contrasena no valida")
                return {"nuevo": None}

# ------------------------------------------------------------------------------------