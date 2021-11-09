from ...kernel.Agent.Action import Action

class WSResponseAction(Action):
    
    def execute(self, data):    	
        queue = self.agent.requestTable[data['requestID']]
        dto = data['data']
        queue.put(dto)
        