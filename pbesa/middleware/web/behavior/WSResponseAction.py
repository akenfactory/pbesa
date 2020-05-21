from TokenForce.KernelTK.Util.Log import Log
from TokenForce.KernelTK.AgentTK.ActionTK import ActionTK

class WSResponseAction(ActionTK):
    
    def execute(self, data):    	
        queue = self.agent.requestTable[data['requestID']]
        dto = data['data']
        queue.put(dto)
        Log().info('[WS-RESPONSE]: Request-ID: ' + data['requestID'] + '.')