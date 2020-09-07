from abc import abstractmethod
from ...kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class ResponseAction(Action):
    """ An action is a response to the occurrence of an event """
    
    def sendResponse(self, request):
        if len(request['dtoList']) == 1:
            request['gateway'].put(request['dtoList'][0])
        else:
            request['gateway'].put(request['dtoList'])

    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        request = self.agent.getRequestDict()[data['source']]
        if 'timeout' in data:
            self.sendResponse(request)
        else:
            request['dtoList'].append(data['result'])
            if len(request['dtoList']) >= self.agent.getBufferSize():
                self.sendResponse(request)
        
    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
