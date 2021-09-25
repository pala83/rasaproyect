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
        with open('RegAcc.txt', 'r') as acc:
            line = acc.readlines()
            i = 0
            while i != len(line) and line[i].rstrip('\n') != str(slot_value):
                i = i+2 #Los usuarios se encuentran
                        #en las lineas par del archivo
            if i != len(line) and slot_value == line[i].rstrip('\n'):
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
        with open('RegAcc.txt', 'r') as acc:
            user = tracker.get_slot('usuario')
            line = acc.readlines()
            i = 0
            while i != len(line) and line[i].rstrip('\n') != user:
                i = i+2
            i = i+1 #Las contrasenas estan en las lineas inpares del archivo
            if i != len(line) and slot_value == line[i].rstrip('\n'):
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
            while i != len(line) and line[i].rstrip('\n') != str(slot_value):
                i = i+2 #Los usuarios se encuentran
                        #en las lineas par del archivo
            if i != len(line) and slot_value == line[i].rstrip('\n'):
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