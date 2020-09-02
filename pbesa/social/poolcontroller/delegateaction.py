from abc import abstractmethod
from ...kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class DelegateAction(Action):
    """ An action is a response to the occurrence of an event """

    __gateway = None

    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        self.__gateway = data['gateway']
        self.delegate(data['dto'])
    
    def activeTimeout(self, time):
        self.adm.sendEvent(self.agent.id, 'timeout', {'time': time, 'dto': None})

    def toAssign(self, data):
        ag = self.agent.state['freeList'].pop(0)
        self.agent.state['requestDict'][ag] = {
            'gateway': self.__gateway,
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
