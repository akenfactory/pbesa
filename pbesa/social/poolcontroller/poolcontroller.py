from .pooltype import PoolType
from abc import abstractmethod
from .delegate import Delegate
from .exceptions import PoolException
from ...kernel.agent.Agent import Agent
from .responseaction import ResponseAction
from .notifyfreeaction import NotifyFreeAction

class PoolController(Agent):

    __type = None
    __bufferSize = None
    
    def __init__(self, agentID, type, bufferSize):
        self.__type = type
        self.__bufferSize = bufferSize
        super().__init__(agentID)

    def setUp(self):
        self.state = {
            'social': True,
            'freeList': [],
            'requestDict': {},
            'type': self.__type,
            'bufferSize': self.__bufferSize
        }
        self.addBehavior('Delegate')
        if self.__type == PoolType.BLOCK:
            self.bindAction('Delegate', 'delegate', Delegate())
        self.addBehavior('Notify')
        self.bindAction('Notify', 'notify', NotifyFreeAction())
        self.addBehavior('Response')
        self.bindAction('Response', 'response', ResponseAction())
        self.build()

    def bindDelegateAction(self, action):
        if self.__type == PoolType.NO_BLOCK:
            self.bindAction('Delegate', 'delegate', action)
        else:
            raise PoolException('[Warn, bindDelegateAction]: The controller is a blocking type. No need to define delegator')

    def suscribeAgent(self, agent):
        agent.state['controller'] = self.id
        agent.state['controllerType'] = 'POOL'
        self.state['freeList'].append(agent.id)
        actions = agent.getActions()
        for action in actions:
            action.isPool = True
            action.enableResponse = (self.__type == PoolType.BLOCK)
    
    @abstractmethod
    def build(self):
        pass
