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
import time
import traceback
from pbesa.kernel.system.Adm import Adm
from pbesa.kernel.agent.Agent import Agent
from pbesa.kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class SumAction(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        print(self.agent.state['acum'] + data)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

# --------------------------------------------------------
# Define Agent
# --------------------------------------------------------
class SumAgent(Agent):
    """ Through a class the concept of agent is defined """
    
    def setUp(self):
        """
        Method that allows defining the status, structure 
        and resources of the agent
        """
        # Defines the agent state
        self.state = {
            'acum': 7
        }
        # Defines the behavior of the agent. An agent can 
        # have one or many behaviors
        self.addBehavior('calculate')
        # Assign an action to the behavior
        self.bindAction('calculate', 'sum', SumAction())

    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass

# --------------------------------------------------------
# Main
# --------------------------------------------------------
if __name__ == "__main__":
    """ Main """
    try:
        # Initialize the container
        mas = Adm()
        mas.start()

        # Create the agent
        agentID = 'Jarvis'
        ag = SumAgent(agentID)
        ag.start()

        # Send the event
        data = 8
        mas.sendEvent('Jarvis', 'sum', data)

        # Remove the agent from the system
        time.sleep(1)
        mas.killAgent(ag)

        # Destroy the Agent Container
        mas.destroy()
    except:
        traceback.print_exc()
