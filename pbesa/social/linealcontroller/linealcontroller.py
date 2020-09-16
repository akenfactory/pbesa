from abc import abstractmethod
from ...kernel.util.Queue import Queue
from .exceptions import LinealException
from ...kernel.agent.Agent import Agent
from .timeoutaction import TimeoutAction
from .delegateaction import DelegateAction
from .responseaction import ResponseAction

class LinealController(Agent):
    
    def __init__(self, agentID):
        self.__agentList = []
        self.__checkDict = {}
        self.__gateway = None
        self.__freeList = None
        self.__timeout = False
        self.__poolSize = None
        self.__requestDict = {}    
        super().__init__(agentID)

    def setUp(self):
        self._social = True
        self.addBehavior('Timeout')
        self.bindAction('Timeout', 'timeout', TimeoutAction())
        self.addBehavior('Delegate')
        self.addBehavior('Response')
        self.build()

    def bindDelegateAction(self, action):
        self.bindAction('Delegate', 'delegate', action)

    def bindResponseAction(self, action):
        self.bindAction('Response', 'response', action)

    def suscribeAgent(self, agent):
        if not isinstance(agent, Agent):
            raise LinealException('[Warn, suscribeAgent]: The object to subscribe is not an agent')
        agent.setController(self.id)
        agent.setControllerType('LINEAL')
        self.__checkDict[agent.id] = None
        self.__agentList.append(agent.id)
        actions = agent.getActions()
        for action in actions:
            action.setIsPool(False)
            action.setEnableResponse(True)
    
    def suscribeRemoteAgent(self, agentID):
        if not isinstance(agentID, str):
            raise LinealException('[Warn, suscribeRemoteAgent]: The object to subscribe is not an agent ID')
        self.__checkDict[agentID] = None
        self.__agentList.append(agentID)
        
    def reset(self):
        self.__freeList = []
        for ag in self.__agentList:
            self.__checkDict[ag] = None
            self.__freeList.append(ag)

    @abstractmethod
    def build(self):
        pass

    def start(self):
        if len(self.__agentList) <= 0:
            raise LinealException('[Warn, toAssign]: Controller agent list is empty. Agents must be subscribed to the controller')
        super().start()

    def getFreeList(self):
        return self.__freeList

    def getRequestDict(self):
        return self.__requestDict

    def getGateway(self):
        return self.__gateway

    def setGateway(self, gateway):
        self.__gateway = gateway

    def getCheckDict(self):
        return self.__checkDict
    
    def isTimeout(self):
        return self.__timeout

    def setTimeout(self, timeout):
        self.__timeout = timeout

    def isBlock(self):
        return True
