from abc import abstractmethod
from ...kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class NotifyFreeAction(Action):
    """ An action is a response to the occurrence of an event """
    
    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        self.agent.getFreeQueue().put(data)
        
    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
