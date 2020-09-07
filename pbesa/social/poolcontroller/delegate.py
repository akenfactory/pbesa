from abc import abstractmethod
from ...kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class Delegate(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        ag = self.agent.getFreeQueue().get()
        self.agent.getRequestDict()[ag] = {
            'gateway': data['gateway'],
            'dtoList': []
        }
        self.adm.sendEvent(ag, 'task', data['dto'])

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
