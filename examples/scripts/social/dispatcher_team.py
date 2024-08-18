# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 3.0.1
@date 27/07/20

The Dispatcher Team is a group of artificial intelligence 
agents coordinated by a controller that acts as a task 
dispatcher. Unlike teams that consolidate responses, 
in this system, the controller simply assigns the task to 
the first available agent. Each agent operates 
independently and responds through Controller to the 
client once they have processed the assigned task.

When the client sends a request, the controller directs 
it to the agent who is free at that moment. If all agents 
are busy, the request is put on hold until one of them 
becomes available to handle it. This approach ensures 
quick and efficient responses, optimizing the use of 
available resources.

The Dispatcher Team is ideal for scenarios where fast and 
direct responses are crucial, as it minimizes wait times 
and simplifies task management, allowing the team to 
operate in an agile and effective manner.
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

from pbesa.mas import Adm
from pbesa.social.worker import Task
from pbesa.social.worker import Worker
from pbesa.social.dispatcher_team import DispatcherController

# --------------------------------------------------------
# Define controller agent
# --------------------------------------------------------

# --------------------------------------------------------
# Define Agent
class TranslateController(DispatcherController):
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
class TranslateTask(Task):
    """ An action is a response to the occurrence of an event """

    def run(self, data):
        """
        Execute.
        @param data Event data
        """
        response = None
        if data == 'Hello':
            response ='Hola'
        if data == 'World':
            response = 'Mundo'
        self.send_response(response)

# --------------------------------------------------------
# Define Agent
class WorkerAgent(Worker):
    """ Through a class the concept of agent is defined """
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bind_task(TranslateTask())
        
    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass

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
    w1.start()
    w2ID = 'w2'
    w2 = WorkerAgent(w2ID)
    w2.start()
    
    #-----------------------------------------------------
    # Create the controller agent
    ctrID = 'Jarvis'
    bufferSize = 1
    poolSize = 2
    ag = TranslateController(ctrID, bufferSize, poolSize)
    ag.suscribe_agent(w1)
    ag.suscribe_agent(w2)
    ag.start()

    # Call
    response1 = mas.call_agent(ctrID, 'Hello')
    print(response1)
    response2 = mas.call_agent(ctrID, 'World')
    print(response2)