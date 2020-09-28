from abc import abstractmethod
from ...kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class DelegateAction(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        self.delegate(data)
    
    def activeTimeout(self, time):
        self.adm.sendEvent(self.agent.id, 'timeout', {'time': time, 'dto': None})

    def toAssign(self, data):
        ag = self.agent.getFreeQueue().get()
        self.agent.getRequestDict()[ag] = {
            'dtoList': []
        }
        self.adm.sendEvent(ag, 'task', data)

    @abstractmethod
    def delegate(self, data):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
