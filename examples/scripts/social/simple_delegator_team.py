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
from pbesa.social.delegator_team import DelegateAction, build_delegator

# --------------------------------------------------------
# Define Delegate Action
# --------------------------------------------------------

class TranslateDelegate(DelegateAction):
    """ An action is a response to the occurrence of an event """

    def delegate(self, data):
        """
        Catch the exception.
        @param exception Response exception
        """
        self.to_assign(data[0])
        self.to_assign(data[1])

# --------------------------------------------------------
# Define the agen tasks 
# --------------------------------------------------------

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
    agent_ctr = build_delegator(ctr_id, agent_count, TranslateTask, TranslateDelegate)
    # Make a calls
    data = ['Hello', 'World']
    mas.submit_agent(ctr_id, data)