from abc import abstractmethod
from ...kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class ResponseAction(Action):
    """ An action is a response to the occurrence of an event """
    
    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        request = self.agent.state['requestDict'][data['source']]
        if 'timeout' in data:
            request['gateway'].put(request['dtoList'])
        else:
            request['dtoList'].append(data['result'])
            if len(request['dtoList']) >= self.agent.state['bufferSize']:
                request['gateway'].put(request['dtoList'])
        
    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
