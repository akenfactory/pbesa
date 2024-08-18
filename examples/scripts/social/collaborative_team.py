# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 3.0.1
@date 27/07/20

The Collaborative Team consists of a controller and a 
group of agents who work together to complete tasks 
synchronously with the client. When a client submits a 
request, the controller breaks down the task into smaller 
parts, assigning each part to a specific agent. The 
agents perform their portion of the work and then send 
their results back to the controller. The controller 
then consolidates all the partial responses into a single 
comprehensive response, which is delivered to the client. 
This structure allows the team to efficiently tackle 
complex tasks by leveraging the agents' ability to work 
in parallel. By maintaining a synchronous interaction 
with the client, the Collaborative Team ensures 
that requests are managed in an organized and structured 
manner, providing a unified and cohesive response. 
This approach is ideal for situations where precision 
and consistency are essential, as it allows for close 
coordination among all team members and the delivery of 
clear and unified results.
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------
from pbesa.mas import Adm
from pbesa.social.worker import Task
from pbesa.social.worker import Worker
from pbesa.social.collaborative_team import DelegateAction
from pbesa.social.collaborative_team import ResponseAction
from pbesa.social.collaborative_team import CollaborativeController

# --------------------------------------------------------
# Define controller agent
# --------------------------------------------------------

# --------------------------------------------------------
# Define Action
class TranslateDelegate(DelegateAction):
    """ An action is a response to the occurrence of an event """

    def delegate(self, data):
        """
        Catch the exception.
        @param exception Response exception
        """
        tokens = data.split('_')
        self.toAssign(tokens[0])
        self.toAssign(tokens[1])
        self.activeTimeout(3)

# --------------------------------------------------------
# Define Action
class TranslateResponse(ResponseAction):
    """ An action is a response to the occurrence of an event """

    def end_of_process(self, resultDict, timeout):
        """
        Catch the exception.
        @param exception Response exception
        """
        result = "%s %s" % (resultDict['w1'], resultDict['w2'])
        self.send_response(result)

# --------------------------------------------------------
# Define Agent
class TranslateController(CollaborativeController):
    """ Through a class the concept of agent is defined """
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bind_delegate_action(TranslateDelegate())
        # Assign an action to the behavior
        self.bind_response_action(TranslateResponse())

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
        if data == 'Hello':
            self.send_response('Hola')
        if data == 'World':
            self.send_response('Mundo')

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
    ag = TranslateController(ctrID)
    ag.suscribe_agent(w1)
    ag.suscribe_agent(w2)
    ag.start()

    # Call
    result = mas.call_agent(ctrID, "Hello_World")

    # Log
    print(result)
