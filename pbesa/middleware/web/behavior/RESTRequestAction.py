from TokenForce.KernelTK.Util.Log import Log
from TokenForce.KernelTK.SystemTK.Adm import Adm
from TokenForce.KernelTK.AgentTK.ActionTK import ActionTK

class RESTRequestAction(ActionTK):
	
    def execute(self, data):
        Log().info(data)
        url = data['url']
        dto = data['data']

        self.agent.requestID = self.agent.requestID + 1
        rqstID = str(self.agent.requestID)
        self.agent.requestTable[rqstID] = data['queue'] 

        dto['requestID'] = rqstID
        urlSplit = url.split('/')
        Adm().sendEvent(urlSplit[0], urlSplit[1], dto)

