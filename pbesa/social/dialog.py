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
import traceback
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

class Node:
    def __init__(self, actor, performative, text=None, is_terminal=False):
        self.actor = actor
        self.performative = performative  # Se asigna el ID del objeto (en str)
        self.text = text
        self.is_terminal = is_terminal
        self.children = []

class ActionNode(Node):
    def __init__(self, actor, performative, text, action=None, team=None, tool=None, is_terminal=False):
        super().__init__(actor, performative=performative, text=text, is_terminal=is_terminal)
        self.action = action
        self.team = team
        self.tool = tool

class DeclarativeNode(Node):
    def __init__(self, actor, performative, text, is_terminal=False):
        super().__init__(actor, performative, text, is_terminal)

class ResponseNode(Node):
    def __init__(self, actor, performative, text, is_terminal=False):
        super().__init__(actor, performative=performative, text=text, is_terminal=is_terminal)

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

def recorrer_interacciones(obj):
    try:
        # Si el objeto es una lista, procesamos cada elemento y devolvemos la lista de nodos resultantes
        if isinstance(obj, list):
            nodos = []
            for item in obj:
                resultado = recorrer_interacciones(item)
                if resultado is not None:
                    # Si el resultado es una lista, lo extendemos; si es un solo nodo, lo agregamos
                    if isinstance(resultado, list):
                        nodos.extend(resultado)
                    else:
                        nodos.append(resultado)
            return nodos

        # Si es un diccionario
        elif isinstance(obj, dict):
            # Si tiene la clave "tipo", creamos un nodo (según su valor) y procesamos sus hijos
            if "tipo" in obj:
                # Se usa el id del diccionario convertido a cadena para 'performative'
                current_id = str(id(obj))
                texto = obj.get("texto")
                
                # Procesamos los nodos hijos buscando en las claves "interacciones" y "Interacciones"
                children = []
                for key in ["interacciones", "Interacciones"]:
                    if key in obj and isinstance(obj[key], (list, dict)):
                        hijos = recorrer_interacciones(obj[key])
                        if hijos is not None:
                            if isinstance(hijos, list):
                                children.extend(hijos)
                            else:
                                children.append(hijos)
                
                # Es terminal si no tiene hijos
                is_terminal = (len(children) == 0)
                
                # Normalizamos el valor de "tipo" (se pasa a minúsculas y se reemplaza "í" por "i")
                tipo = obj["tipo"].lower().replace("í", "i").strip()
                if tipo == "dialogo":
                    nuevo_nodo = DeclarativeNode(actor=obj["actor"], performative=current_id, text=texto, is_terminal=is_terminal)
                elif tipo == "llamada a equipo":
                    nuevo_nodo = ActionNode(actor=obj["actor"], performative=current_id, text=texto, action=tipo, team=obj["equipo"], tool=obj["herramienta"], is_terminal=is_terminal)
                elif tipo == "respuesta de equipo":
                    nuevo_nodo = ResponseNode(actor=obj["actor"], performative=current_id, text=texto, is_terminal=is_terminal)
                else:
                    nuevo_nodo = Node(actor=obj["actor"], performative=current_id, text=texto, is_terminal=is_terminal)
                
                # Se asignan los nodos hijos construidos
                nuevo_nodo.children = children
                return nuevo_nodo
            
            else:
                # Si el diccionario no tiene "tipo", es un contenedor (por ejemplo, el nodo raíz que contiene "Interacciones")
                nodos = []
                for key in ["interacciones", "Interacciones"]:
                    if key in obj:
                        resultado = recorrer_interacciones(obj[key])
                        if resultado is not None:
                            if isinstance(resultado, list):
                                nodos.extend(resultado)
                            else:
                                nodos.append(resultado)
                return nodos if nodos else None
        else:
            return None
    except Exception as e:
        print(f"Error al recorrer interacciones: {e}")
        traceback.print_exc()
        return None
    
def extraer_diccionario_nodos(grafo):
    diccionario_nodos = {}
    
    def recorrer(nodo):
        # Obtener el contenido: se utiliza 'text' si existe, de lo contrario se toma 'action'
        diccionario_nodos[nodo.performative] = nodo
        # Recorrer los hijos del nodo
        for hijo in nodo.children:
            recorrer(hijo)
    
    # El grafo puede ser una lista de nodos o un único nodo
    if isinstance(grafo, list):
        for nodo in grafo:
            recorrer(nodo)
    else:
        recorrer(grafo)
        
    return diccionario_nodos

# Ejemplo: función para imprimir el grafo (para visualizar la estructura)
def imprimir_grafo(nodo, nivel=0):
    indent = "  " * nivel
    # Se muestra la clase del nodo y algunos atributos
    clase = nodo.__class__.__name__
    print(f"{indent}{clase} (performative: {nodo.performative}, text/action: {nodo.text if hasattr(nodo, 'text') and nodo.text is not None else getattr(nodo, 'action', None)}, terminal: {nodo.is_terminal})")
    for child in nodo.children:
        imprimir_grafo(child, nivel + 1)