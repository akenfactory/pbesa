from TokenForce.KernelTK.Util.Log import Log
from TokenForce.KernelTK.AgentTK.ActionTK import ActionTK

class RESTResponseAction(ActionTK):
    
    def execute(self, data):
        queue = self.agent.requestTable[data['requestID']]
        queue.put(data)
