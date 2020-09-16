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

    def __init__(self):
        self.__timer = None
        super().__init__()

    def handler(self):
        """ Timeout handler """
        if self.agent.isTimeout():
            self.agent.setTimeout(False)
            self.adm.sendEvent(self.agent.id, 'response', 'timeout')

    def execute(self, data):
        """
        @param data
        """
        if data['command'] == 'start':
            if not self.agent.isTimeout():
                self.agent.setTimeout(True)
                self.__timer = Timer(data['time'], self.handler)
                self.__timer.start()
        else:
            if self.__timer:
                self.__timer.cancel()
                self.__timer = None

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
