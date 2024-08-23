# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 12/08/24

Example of a simple agent that receives an event and
responds to it. The agent is created, started, an event
is sent to it, and the agent responds to the event.
"""
# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import os
import openai
from pbesa.mas import Adm
from dotenv import load_dotenv
from pbesa.social.worker import Task
from pbesa.social.worker import Worker
from pbesa.cognitive import Production
from pbesa.social.dispatcher_team import DispatcherController

# --------------------------------------------------------
# Define variables and constants
# --------------------------------------------------------

# Load the environment variables
load_dotenv()

# Define API_KEY.
API_KEY = os.getenv("OPENAI_KEY_API")

# Define OpenAI engine.
OPENAI_ENGINE = os.getenv("OPENAI_ENGINE")

# --------------------------------------------------------
# Define controller agent
# --------------------------------------------------------

# --------------------------------------------------------
# Define Agent

class ProcessController(DispatcherController):
    """ Through a class the concept of agent is defined """
        
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        pass

    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass
        
# --------------------------------------------------------
# Define worker agent
# --------------------------------------------------------

# --------------------------------------------------------
# Define Action

class ProcessTask(Task):
    """ An action is a response to the occurrence of an event """

    def run(self, data):
        """
        Execute.
        @param data Event data
        """
        self.agent.update_world_model(data["fact"])
        response = self.agent.derive()
        self.send_response(response)

# --------------------------------------------------------
# Define Agent

class WorkerAgent(Worker, Production):
    """ Through a class the concept of agent is defined """
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bind_task(ProcessTask())
        
    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass

    def define_role(self) -> str:
        """ Set role set method """
        return """
        eres una asistente virtual llamado G-Berry y estas para asistir al usario en el proceso de conversion de una moneda
        """

    def define_rule_set(self) -> tuple:
        """ Set rule set method """
        return (
            ('Si es PRESENTARSE entonces solo describe brevemente tu rol, luego pregunta ¿Qué moneda deseas convertir? y luego PRIMERO'),
            ('Si es PRIMERO entonces pregunta por la moneda a la que se desea convertir y luego SEGUNDO'),
            ('Si es SEGUNDO entonces pregunta por la cantidad a convertir y luego TERMINAR'),
            ('Si es TERMINAR entonces finaliza la conversación'),
        )
    
    def define_example(self) -> str:
        """ Set example set method """
        return """
        user: es PRESENTARSE
        assistant: Hola, soy G-Berry, tu asistente virtual para asistirte en la conversión de una moneda. ¿Qué moneda deseas convertir?
        user: es PRIMERO
        assistant: ¿A qué moneda deseas convertir?
        user: es SEGUNDO
        assistant: ¿Cuánto deseas convertir?
        user: es TERMINAR
        assistant: Hemos finalizado el proceso de conversión de moneda. ¿Hay algo más en lo que pueda ayudarte?
        """

# --------------------------------------------------------
# Main
# --------------------------------------------------------

if __name__ == "__main__":
    """ Main """
    # Initialize the container
    mas = Adm()
    mas.start()

    #-----------------------------------------------------
    # Create the worker agents
    w1ID = 'w1'
    w1 = WorkerAgent(w1ID)
    w1.load_model(openai, {"OPENAI_ENGINE": OPENAI_ENGINE, "API_KEY": API_KEY})
    w1.start()
    
    #-----------------------------------------------------
    # Create the controller agent
    ctrID = 'Jarvis'
    bufferSize = 1
    poolSize = 2
    ag = ProcessController(ctrID, bufferSize, poolSize)
    ag.suscribe_agent(w1)
    ag.start()

    # Run the demo
    response = mas.call_agent(ctrID, {'fact': 'es PRESENTARSE'})
    print("=> ", response)
    response = mas.call_agent(ctrID, {'fact': 'es PRIMERO'})
    print("=> ", response)
    response = mas.call_agent(ctrID, {'fact': 'es SEGUNDO'})
    print("=> ", response)
    response = mas.call_agent(ctrID, {'fact': 'es TERMINAR'})
    print("=> ", response)