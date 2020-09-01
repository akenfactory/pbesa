from abc import abstractmethod
from ...kernel.agent.Agent import Agent
from .timeoutaction import TimeoutAction
from .delegateaction import DelegateAction
from .responseaction import ResponseAction

class LinealController(Agent):
    
    def setUp(self):
        self.state = {
            'social': True,
            'freeList': [],
            'checkDict': {},
            'gateway': None,
            'timeout': False
        }
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
        agent.state['controller'] = self.id
        self.state['checkDict'][agent.id] = None
        self.state['freeList'].append(agent.id) 
    
    @abstractmethod
    def build(self):
        pass
