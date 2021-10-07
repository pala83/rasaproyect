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

class ActionConsulta(Action):

    def name(self) -> Text:
        return "action_consultar"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        consulta = next(tracker.get_latest_entity_values("consulta"), None)
        if str(consulta)=="precio":
            message="Estos son los precios de nuestros productos:\n Sopa Knorr: $27,80 (IVA incluido)\n  Sopa Knorr (Bulto x24):$624,22\n Fideos Matarazzo $39\n  Fideos Matarazzo (Bulto x50): $1821\n Papel Higienico Scott (50m) $80\n  Papel Higiennico Scott (Bulto x24): $1761\n Mayonesa Hellmann's: $140\n  Mayonesa Hellmann's (Bulto x24): $3160"
        elif str(consulta)=="disponibilidad":
            message="Aqui tienes un listado de la disponibilidad de nuestros productos:\n Sopas Knorr: En Stock\n Fideos Matarazzo: En Stock\n Papel Higienico Scott: En Stock\n Mayonesa Hellmann's: En stock"
        elif str(consulta)=="horarios":
            message="Los horarios de atencion al cliente son de 8:00 a 17:00\nSi quieres contactarte con nosotros, nuestro numero de telefono es: 0-800-rasahelp"
        dispatcher.utter_message(text=str(message))

        return []

class ActionMetodoPago(Action):

    def name(self) -> Text:
        return "action_metodo_pago"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("usuario") == None:
            dispatcher.utter_message(text="No parece que hayas iniciado sesion. Podemos seguir con la compra pero no podremos registrarla en un perfil.")
        else:
            user = tracker.get_slot('usuario')
            with open('Cuentas.json', 'r') as acc:
                datos = json.load(acc)
                i = 0
                while i <= (len(datos["cuentas"])-1) and datos["cuentas"][i]["user"] != user:
                    i = i+1
                if i <= (len(datos["cuentas"])-1) and datos["cuentas"][i]["user"] == user:
                    metodo = datos["cuentas"][i]["metodo_pago_fav"]
                    message = f"Parece que ya has comprado usando {metodo}, te gustaria volver a comprar de la misma forma?"
                    dispatcher.utter_message(text=message)
                else:
                    print("ERROR: Este error no deberia suceder")

        return []

class ActionPago(Action):

    def name(self) -> Text:
        return "action_efectuar_pago"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        mpago = next(tracker.get_latest_entity_values("mpago"), None)
        user = tracker.get_slot('usuario')
        i = 0
        with open('Cuentas.json', 'r+') as acc:
            datos = json.load(acc)
            date = datetime.today() + timedelta(days = random.randint(1, 14))
            date = date.strftime("%d/%m/%Y")
            while datos["cuentas"][i]["user"] != user:
                i = i+1
            datos["cuentas"][i]["n_compras"] = datos["cuentas"][i]["n_compras"]+1
            datos["cuentas"][i]["metodo_pago_fav"] = mpago
            npedido = random.randint(1000, 9999)

            if npedido % 5 == 0: #No se cobra el envio cada 5 compras en el mayorista
                message = f"FELICIDADES! Esta es tu compra numero {npedido}, por lo tanto no te cobraremos el envio de este pedido.\nPor favor, ingrese al siguiente link y complete el formulario con sus datos para completar la compra.\n\nEl numero de pedido es {npedido}.\nSu pedido llegara el {date}\nMuchas gracias por su compra."
                dispatcher.utter_message(text=message)
            else:
                message = f"Por favor, ingrese al siguiente link y complete el formulario con sus datos para completar la compra.\n\nEl numero de pedido es {npedido}.\nSu pedido llegara el {date}\nMuchas gracias por su compra." 
                dispatcher.utter_message(text=message)
            
            #Guardo los datos en el json
            y = {
                "npedido": npedido,
                "entrega": str(date)    
            }
            datos["envios"].append(y)
            acc.seek(0)
            json.dump(datos, acc, indent=4)

        return [SlotSet("nuevo", "false")]

#Lo mismo que la accion de pago 1 pero obteniendo el metodo del json en vez de por las entidades
#y no cambiar el slot de "nuevo"

class ActionPago2(Action):

    def name(self) -> Text:
        return "action_efectuar_pago2"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user = tracker.get_slot('usuario')
        i = 0
        with open('Cuentas.json', 'r+') as acc:
            datos = json.load(acc)
            date = datetime.today() + timedelta(days = random.randint(1, 14))
            date = date.strftime("%d/%m/%Y")
            while datos["cuentas"][i]["user"] != user:
                i = i+1
            datos["cuentas"][i]["n_compras"] = datos["cuentas"][i]["n_compras"]+1
            mpago = datos["cuentas"][i]["metodo_pago_fav"]
            npedido = random.randint(1000, 9999)

            if npedido % 5 == 0: #No se cobra el envio cada 5 compras en el mayorista
                message = f"FELICIDADES! Esta es tu compra numero {npedido}, por lo tanto no te cobraremos el envio de este pedido.\nPor favor, ingrese al siguiente link y complete el formulario con sus datos para completar la compra.\n\nEl numero de pedido es {npedido}.\nSu pedido llegara el {date}\nMuchas gracias por su compra."
                dispatcher.utter_message(text=message)
            else:
                message = f"Por favor, ingrese al siguiente link y complete el formulario con sus datos para completar la compra.\n\nEl numero de pedido es {npedido}.\nSu pedido llegara el {date}\nMuchas gracias por su compra."
                dispatcher.utter_message(text=message)
            
            #Guardo los datos en el json
            y = {
                "npedido": npedido,
                "entrega": str(date)    
            }
            datos["envios"].append(y)
            acc.seek(0)
            json.dump(datos, acc, indent=4)

        return []

class ActionSetNuevoBool(Action):

    def name(self) -> Text:
        return "action_set_nuevo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        with open('Cuentas.json', 'r') as acc:
            user = tracker.get_slot('usuario')
            datos = json.load(acc)
            i = 0
            while datos["cuentas"][i]["user"] != user:
                i = i+1
            message = f"Bienvenido/a, {user}, espero poder ayudarte."
            dispatcher.utter_message(text=message)
            if datos["cuentas"][i]["n_compras"] == 0:
                print("nuevo: true")
                return [SlotSet("nuevo", "true")]
            else:
                print("nuevo: false")
                return [SlotSet("nuevo", "false")]

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
            while i <= (len(datos["cuentas"])-1) and datos["cuentas"][i]["user"] != str(slot_value):
                i = i+1
            if i <= (len(datos["cuentas"])-1) and slot_value == datos["cuentas"][i]["user"]:
                return {"usuario": slot_value}
            else:
                dispatcher.utter_message(text=f"Usuario no registrado")
                return {"usuario": None}

    def validate_contr(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """validate 'contr' value"""

        #Revisa si el usuario ingresado ya tiene una cuenta a su nombre
        print(f"Contrasena ingresada: {slot_value}")
        with open('Cuentas.json', 'r') as acc:
            user = tracker.get_slot('usuario')
            datos = json.load(acc)
            i = 0
            while datos["cuentas"][i]["user"] != user:
                i = i+1
            if slot_value == str(datos["cuentas"][i]["password"]):
                return {"contr": slot_value}
            else:
                dispatcher.utter_message(text=f"Contrasena incorrecta")
                return {"contr": None}
        
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
        with open('RegAcc.txt', 'r') as acc:
            line = acc.readlines()
            i = 0
            while i <= (len(line)-1) and line[i].rstrip('\n') != str(slot_value):
                i = i+2 #Los usuarios se encuentran
                        #en las lineas par del archivo
            if i <= (len(line)-1) and slot_value == line[i].rstrip('\n'):
                dispatcher.utter_message(text=f"Usuario ya registrado")
                return {"usuario": None}
        with open('RegAcc.txt', 'a') as acc:
            acc.write(slot_value+"\n")
            return {"usuario": slot_value}

    def validate_contr(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """validate 'contr' value"""

        #Revisa si el usuario ingresado ya tiene una cuenta a su nombre
        print(f"Contrasena ingresada: {slot_value}")
        with open('RegAcc.txt', 'a') as acc:
            if slot_value != '':
                acc.write(slot_value+"\n")
                return {"contr": slot_value}
            else:
                dispatcher.utter_message(text=f"Contrasena no valida")
                return {"contr": None}