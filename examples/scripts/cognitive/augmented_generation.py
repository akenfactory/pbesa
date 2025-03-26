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
import re
import openai
from pbesa.mas import Adm
from dotenv import load_dotenv
from pbesa.social.worker import Task
from pbesa.social.worker import Worker
from pbesa.cognitive import AugmentedGeneration
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

class AugmentedController(DispatcherController):
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

class AugmentedTask(Task):
    """ An action is a response to the occurrence of an event """

    def run(self, data):
        """
        Execute.
        @param data Event data
        """
        response = self.agent.derive(data["query"])
        self.send_response(response)

# --------------------------------------------------------
# Define Agent

class WorkerAgent(Worker, AugmentedGeneration):
    """ Through a class the concept of agent is defined """
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bind_task(AugmentedTask())
        
    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass

    def define_role(self) -> str:
        """ Set role set method """
        return """
        eres una asistente virtual llamado G-Berry y estas para asistir al usario para obtener información de un documento
        """

    def retrieval(self, query) -> str:
        """ Set retrieval method
        :param query: query
        :return: str
        """
        # Load bib.txt file
        data = None
        with open('bib.txt', 'r') as file:
            data = file.read()
        # Get chunk to retrival from text by query
        pattern = r"([^.]*?interpretación de Copenhague.*?\n\n)"
        chunk = re.search(pattern, data).group(0)
        print("Chunk:\n", chunk)
        return chunk

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
    ag = AugmentedController(ctrID, bufferSize, poolSize)
    ag.suscribe_agent(w1)
    ag.start()

    # Run the demo
    response = mas.call_agent(ctrID, {'query': '¿Qué es la interpretación de Copenhague?'})
    print("Response:\n", response)