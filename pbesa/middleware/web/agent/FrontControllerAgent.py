from pbesa.kernel.agent.Agent import Agent
from pbesa.kernel.util.HashTable import HashTable
from pbesa.middleware.web.behavior.WSRequestAction import WSRequestAction
from pbesa.middleware.web.behavior.WSResponseAction import WSResponseAction
from pbesa.middleware.web.behavior.RESTRequestAction import RESTRequestAction
from pbesa.middleware.web.behavior.RESTResponseAction import RESTResponseAction
from pbesa.middleware.web.behavior.WSSNJDelegateAction import WSSNJDelegateAction

class FrontControllerAgent(AgtTK):

    poolList = None
    requestID = None
    agentTable = None
    requestTable = None

    def __init__(self):
        self.poolList = []
        self.requestID = 0
        self.agentTable = HashTable()
        self.requestTable = HashTable() 
        super().__init__()

    def setUp(self):
        settings = {
            'id': 'front_controller',
            'state': {}, 
            'behaviors': [
                {'name': 'Delegate', 'events':[
                    {'performative': 'rest_request', 'action' : RESTRequestAction()},
                    {'performative': 'rest_response', 'action' : RESTResponseAction()},
                    {'performative': 'ws_request', 'action' : WSRequestAction()},
                    {'performative': 'ws_response', 'action' : WSResponseAction()},
                    {'performative': 'wsnj_delegate', 'action' : WSSNJDelegateAction()}
                ]}
            ]
        }
        return settings

    def getFreePool(self):
        if self.poolList:
            return self.poolList.pop()
        else:
            return None

    def addPool(self, ag):
        self.poolList.append(ag)

    def getAgentID(self, userID):
        if self.agentTable:
            return self.agentTable[str(userID)]
        return None

    def suscribeAgent(self, userID, agID):
        self.agentTable[userID] = agID

    def toPool(self, userID, agID):
        self.agentTable.slots.remove(userID)
        self.addPool(agID)
                        
                        
