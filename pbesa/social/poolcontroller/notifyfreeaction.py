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
        if not data in self.agent.state['freeList']: 
            self.agent.state['freeList'].append(data)
        
    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
