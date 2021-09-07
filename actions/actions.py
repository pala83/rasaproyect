# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_consultar"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        consulta = next(tracker.get_latest_entity_values("consulta"), None)
        if str(consulta)=="precio":
            message="Estos son los precios de nuestros productos: Sopas: $40, Fideos $30, Papel HIgienico $1500"

        dispatcher.utter_message(text=str(message))

        return []
