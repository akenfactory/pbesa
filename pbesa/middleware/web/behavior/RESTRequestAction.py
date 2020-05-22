from ...kernel.system.Adm import Adm
from ...kernel.agent.Action import Action

class RESTRequestAction(Action):
	
    def execute(self, data):
        url = data['url']
        dto = data['data']

        self.agent.requestID = self.agent.requestID + 1
        rqstID = str(self.agent.requestID)
        self.agent.requestTable[rqstID] = data['queue'] 

        dto['requestID'] = rqstID
        urlSplit = url.split('/')
        Adm().sendEvent(urlSplit[0], urlSplit[1], dto)

