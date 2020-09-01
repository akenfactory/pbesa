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
            for key, res in self.agent.state['checkDict'].items():
                results[key] = res
            self.endOfProcess(results, True)
        else:
            agentID = data['source']
            result = 'None'
            if data['result']:
                result =  data['result']
            self.agent.state['checkDict'][agentID] = result
            if self.check():
                results = {}
                for key, res in self.agent.state['checkDict'].items():
                    results[key] = res
                self.endOfProcess(results, False)
        
    def check(self):
        for res in self.agent.state['checkDict'].values():
            if not res:
                return False
        return True

    def sendResponse(self, response):
        self.agent.state['timeout'] = False
        self.agent.state['gateway'].put(response) 
    
    @abstractmethod
    def endOfProcess(self, results, timeout):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
