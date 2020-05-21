from pbesa.kernel.util.Log import Log
from pbesa.kernel.agent.Action import Action

class RESTResponseAction(Action):
    
    def execute(self, data):
        queue = self.agent.requestTable[data['requestID']]
        queue.put(data)
