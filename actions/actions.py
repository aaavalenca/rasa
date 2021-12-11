# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
import json
import random
import datetime as dt

from rasa_sdk.events import AllSlotsReset
from rasa_sdk import Action , Tracker
from rasa_sdk.executor import CollectingDispatcher

with open ('restaurant_db.json', 'r') as read_file:
    restaurants_in_db = json.load(read_file)

entities = {}

def select_restaurants(restaurant):
    # seleciona todos os restaurantes que têm as características dadas pelo usuário
    return restaurant["area"] == entities['area'] and restaurant["food"] == entities['food'] and restaurant["pricerange"] == entities['pricerange']

def get_restaurants(): 
    # filtra os que não têm as características do usuário
    options = [x for x in filter(select_restaurants, restaurants_in_db)] 

    # Dar, no máximo, 5 sugestões
    random.shuffle(options) 
    options = options[:min(5, len(options))] 

    return options

class ActionFindRestaurant(Action):

    def name(self) -> Text:
        return "action_find_restaurant"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        global entities
        entities = {}

        entities['area'] = tracker.get_slot('restaurant-area')
        entities['food'] = tracker.get_slot('restaurant-food')
        entities['pricerange'] = tracker.get_slot('restaurant-pricerange')

        restaurant_results = get_restaurants()

        buttons = [{"title":'Restaurant name: ' + x["name"], "payload": '/book_restaurant{"restaurant-name":"' + x["name"] + '"}'} for x in restaurant_results] + [{"title": "Finished", "payload": "/finish_query"}]
        dispatcher.utter_message(text="here's what I found for " + entities['area'] + ", " + entities['food'] + ", and" + entities['pricerange'] + ":", buttons=buttons)

        return []

class ActionResetAllSlots(Action):

    def name(self) -> Text:
        return "action_reset_all_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [AllSlotsReset()]
