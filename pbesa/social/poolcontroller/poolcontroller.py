from .pooltype import PoolType
from abc import abstractmethod
from .delegate import Delegate
from .exceptions import PoolException
from ...kernel.util.Queue import Queue
from ...kernel.agent.Agent import Agent
from .responseaction import ResponseAction
from .notifyfreeaction import NotifyFreeAction

class PoolController(Agent):
    
    def __init__(self, agentID, type, bufferSize, poolSize):
        self.__type = type
        self.__poolSize = poolSize
        self.__bufferSize = bufferSize
        self.__requestDict = {}
        self.__freeQueue = Queue(poolSize)
        self.__agentList = []
        super().__init__(agentID)

    def setUp(self):
        self._social = True
        self.addBehavior('Delegate')
        if self.__type == PoolType.BLOCK:
            self.bindAction('Delegate', 'delegate', Delegate())
        self.addBehavior('Notify')
        self.bindAction('Notify', 'notify', NotifyFreeAction())
        # TODO Para el bloquenate debe ser por defecto
        # Para el no bloquenate ?
        self.addBehavior('Response')
        self.bindAction('Response', 'response', ResponseAction())
        self.build()

    def bindDelegateAction(self, action):
        if self.__type == PoolType.NO_BLOCK:
            self.bindAction('Delegate', 'delegate', action)
        else:
            raise PoolException('[Warn, bindDelegateAction]: The controller is a blocking type. No need to define delegator')

    def suscribeAgent(self, agent):
        self.__agentList.append(agent.id)
        agent.setController(self.id)
        agent.setControllerType('POOL')
        self.__freeQueue.put(agent.id)
        actions = agent.getActions()
        for action in actions:
            action.setIsPool(True)
            action.setEnableResponse(self.__type == PoolType.BLOCK)

    def suscribeRemoteAgent(self, agentID):
        if not isinstance(agentID, str):
            raise PoolException('[Warn, suscribeRemoteAgent]: The object to subscribe is not an agent ID')
        self.__agentList.append(agentID)
        self.__freeQueue.put(agentID)
    
    def broadcastEvent(self, event, data):
        from pbesa.kernel.system.Adm import Adm
        for agentID in self.__agentList:
            Adm().sendEvent(agentID, event, data)
    
    @abstractmethod
    def build(self):
        pass

    def getFreeQueue(self):
        return self.__freeQueue

    def getRequestDict(self):
        return self.__requestDict

    def getBufferSize(self):
        return self.__bufferSize

    def isBlock(self):
        return self.__type == PoolType.BLOCK
