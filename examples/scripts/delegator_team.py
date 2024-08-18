# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 3.0.1
@date 27/07/20
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

from pbesa.mas import Adm
from pbesa.social.worker import Task
from pbesa.social.worker import Worker
from pbesa.social.dispatcher_team import PoolType
from pbesa.social.dispatcher_team import DelegateAction
from pbesa.social.dispatcher_team import DispatcherController

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
        self.to_assign(data[0])
        self.to_assign(data[1])
        
    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

# --------------------------------------------------------
# Define Agent
class TranslateController(DispatcherController):
    """ Through a class the concept of agent is defined """
        
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bind_delegate_action(TranslateDelegate())
        
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
            print('Hola')
        if data == 'World':
            print('Mundo')

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

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
    ag = TranslateController(ctrID, PoolType.NO_BLOCK, bufferSize, poolSize)
    ag.suscribe_agent(w1)
    ag.suscribe_agent(w2)
    ag.start()

    # Call
    data = ['Hello', 'World']
    mas.submit_agent(ctrID, data)
