from abc import abstractmethod
from ...kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class Task(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        self.goHead(data)

    def sendResponse(self, data):
        response = {
            'source': self.agent.id,
            'result': data
        }
        self.adm.sendEvent(self.agent.state['controller'], 'response', response)

    @abstractmethod
    def goHead(self, data):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
