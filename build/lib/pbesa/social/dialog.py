# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 05/02/25
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import datetime
from .templates import AFIRMATIVE_RESPONSE, GET_DATE

#------------------------------------------
# Define enumeration with states of the 
# dialog
#------------------------------------------

class DialogState:
    """ Define the dialog states """
    START = "start"
    ASK_CONFIRMATION_NEGATIVE = "ask confirmation negative"
    ASK_CONFIRMATION_POSITIVE = "ask confirmation_positive"
    END = "end"

#------------------------------------------
# Define Node class
#------------------------------------------

class ActionNode:
    """ Node class """

    def __init__(self, owner, performative, action, is_terminal=False):
        self.owner = owner
        self.children = {}
        self.action = action
        self.is_terminal = is_terminal
        self.performative = performative

    def add_child(self, tag, node):
        self.children[tag] = node
    
class DeclarativeNode:
    """ Node class """

    def __init__(self, owner, performative, text, is_terminal=False):
        self.text = text
        self.owner = owner
        self.children = {}
        self.is_terminal = is_terminal
        self.performative = performative

    def add_child(self, tag, node):
        self.children[tag] = node
    
class TerminalNode:
    """ Node class """

    def __init__(self, owner, performative):
        self.owner = owner
        self.performative = performative

class Node:
    """ Node class """

    def __init__(self, owner, performative, text=None, action=None, is_terminal=False, is_expert=False, value={}):
        self.text = text
        self.owner = owner
        self.value = value
        self.children = {}
        self.action = action
        self.is_expert = is_expert
        self.is_terminal = is_terminal
        self.performative = performative

    def add_child(self, tag, node):
        self.children[tag] = node

    def set_value(self, key, value):
        self.value[key] = value

    def run(self, dto):
        if self.text and not self.action:
            return self
        elif self.action:
            window = self.action(self, dto)
            if window.is_terminal:
                return window.action(window, dto) if window.action else window
            elif self.is_expert:
                return self
            return window.run(dto)
        raise Exception("Se ha estructurado mal el dialogo.")
    
    def generate_response(self):
        response = get_response_message()
        response['text'] = self.text
        if self.value:
            for key, value in self.value.items():
                response[key] = value
        return response

#------------------------------------------
# Define functions
#------------------------------------------

def get_response_message():
    """ Define the response message """
    return {
        "text": None,
        "share": False
    }

def check_yes(self, dto):
    """ Check if text is yes """
    user_response = dto['query']
    user_response = user_response.lower()
    if user_response == "si" or user_response == "sí" or user_response == "yes" or user_response == "s ":
        return self.children['yes']
    model_handler = self.owner.model_handler
    prompt = AFIRMATIVE_RESPONSE % user_response
    response = model_handler.make_request(prompt)
    if response:
        if "SI_ES" in response:
            return self.children['yes']
    return self.children['no']

def check_date(self, dto):
    """ Check if date is valid """
    date = dto['query']
    session = dto['session']
    model_handler = self.owner.model_handler
    # Get current date in %d-%m-%Y format.
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    date_prompt = GET_DATE
    prompt = date_prompt.format(
        fecha_actual= current_date,
        texto= date
    )
    response = model_handler.make_request(prompt, engine="gpt-4")
    # Check if response is valid date.
    if response:
        try:
            reminder_date = datetime.datetime.strptime(response, '%Y-%m-%d %H:%M:%S')
            dto['reminder_date'] = reminder_date
            return self.children['yes']
        except:
            pass
    return self.children['no']