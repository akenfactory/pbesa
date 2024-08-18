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
from pbesa.social.dispatcher_team import build_dispatcher_controller

# --------------------------------------------------------
# Define the task of agent
# --------------------------------------------------------

class TranslateTask(Task):
    """ Define the task of the worker agent """

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
# Main
# --------------------------------------------------------
if __name__ == "__main__":
    """ Main """
    # Initialize the container
    mas = Adm()
    mas.start()
    # Create the team
    agent_count = 2
    ctr_id = "translation-team"
    agent_ctr = build_dispatcher_controller(ctr_id, agent_count, TranslateTask)
    # Make a calls
    response_1 = mas.call_agent(ctr_id, 'Hello')
    print(response_1)
    response_2 = mas.call_agent(ctr_id, 'World')
    print(response_2)