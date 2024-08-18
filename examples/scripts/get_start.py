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

import time
import traceback
from pbesa.mas import Adm
from pbesa.kernel.agent import Agent
from pbesa.kernel.agent import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------

class SumAction(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data:any) -> any:
        """ 
        Response.
        @param data Event data 
        """
        print(f'Received event: {data}')
        print('Agent will sum the data, and the result will be:')
        print(self.agent.state['acum'] + data)

# --------------------------------------------------------
# Define Agent
# --------------------------------------------------------

class SumAgent(Agent):
    """ Through a class the concept of agent is defined """
    
    def setup(self) -> None:
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
        self.add_behavior('calculate')
        # Assign an action to the behavior
        self.bind_action('calculate', 'sum', SumAction())

    def shutdown(self) -> None:
        """ Method to free up the resources taken by the agent """
        pass

# --------------------------------------------------------
# Main
# --------------------------------------------------------

# The main function is the entry point of the program
if __name__ == "__main__":
    try:
        # Initialize the container
        mas = Adm()
        mas.start()

        # Create the agent
        agent_id = 'Jarvis'
        ag = SumAgent(agent_id)
        ag.start()

        # Send the event to the agent
        print('Sending event to agent')
        data = 8
        mas.send_event(agent_id, 'sum', data)
        print('Event sent')

        # Wait for the agent to process the event
        time.sleep(1)

        # Remove the agent from the system
        mas.kill_agent(ag)

        # Destroy the Agent Container
        mas.destroy()
    except:
        traceback.print_exc()