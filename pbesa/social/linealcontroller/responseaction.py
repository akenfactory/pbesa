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
        if 'timeout' == data:
            results = {}
            for key, res in self.agent.getCheckDict().items():
                results[key] = res
            self.endOfProcess(results, True)
        else:
            result = 'None'
            agentID = data['source']
            if data['result']:
                result =  data['result']
            self.agent.getCheckDict()[agentID] = result
            if self.check():
                results = {}
                for key, res in self.agent.getCheckDict().items():
                    results[key] = res
                self.endOfProcess(results, False)

    def check(self):
        for res in self.agent.getCheckDict().values():
            if not res:
                return False
        return True

    def sendResponse(self, response):
        self.agent.setTimeout(False)
        self.adm.sendEvent(self.agent.id, 'timeout', {'command': 'cancel'})
        self.agent.getGateway().put(response) 
    
    @abstractmethod
    def endOfProcess(self, results, timeout):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
