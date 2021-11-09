from abc import abstractmethod
from ...kernel.agent.Agent import Agent
from .exceptions import DelegatorException

class Delegator(Agent):
    
    def __init__(self, agentID):
        self.__agentList = []
        super().__init__(agentID)

    def setUp(self):
        self._social = True
        # Defines the agent state
        self.state = {}
        # Defines the delegate behavior        
        self.addBehavior('Delegate')
        # Defines the space for build
        self.build()

    def bindDelegateAction(self, action):
        self.bindAction('Delegate', 'delegate', action)

    def suscribeAgent(self, agent):
        if not isinstance(agent, Agent):
            raise DelegatorException('[Warn, suscribeAgent]: The object to subscribe is not an agent')
        self.__agentList.append(agent.id)

    @abstractmethod
    def build(self):
        pass

    def start(self):
        if len(self.__agentList) <= 0:
            raise DelegatorException('[Warn, start]: Delegate agent list is empty. Agents must be subscribed to the Delegate Agent')
        super().start()

    def getAgentList(self):
        return self.__agentList