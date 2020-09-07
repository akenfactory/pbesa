from abc import abstractmethod
from .exceptions import LinealException
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
        self.agent.setGateway(data['gateway'])
        self.agent.reset()
        self.delegate(data['dto'])
        
    def activeTimeout(self, time):
        self.adm.sendEvent(self.agent.id, 'timeout', {'time': time, 'command': 'start'})

    def toAssign(self, data):
        if len(self.agent.getFreeList()) > 0:
            ag = self.agent.getFreeList().pop(0)
            self.adm.sendEvent(ag, 'task', data)
        else:
            raise LinealException('[Warn, toAssign]: The number of data packets exceeds the number of agents')

    @abstractmethod
    def delegate(self, data):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

