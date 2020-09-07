# ----------------------------------------------------------
# Define resources
# ----------------------------------------------------------
import logging
from threading import Timer
from datetime import datetime
from ...kernel.agent.Action import Action

# ----------------------------------------------------------
# Define the action
# ----------------------------------------------------------
class TimeoutAction(Action):
    """
    @See Action
    """

    def handler(self):
        """ Timeout handler """
        if self.agent.isTimeout():
            self.agent.setTimeout(False)
            self.adm.sendEvent(self.agent.id, 'response', 'timeout')

    def execute(self, data):
        """
        @param data
        """
        if not self.agent.isTimeout():
            self.agent.setTimeout(True)
            r = Timer(data['time'], self.handler)
            r.start()

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
