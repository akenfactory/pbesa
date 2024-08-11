# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 09/08/24
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------
 
from abc import abstractmethod
from ..kernel.agent import Agent
from ..kernel.agent import Action

# ----------------------------------------------------------
# Defines system component exceptions
# ----------------------------------------------------------
 
class DelegatorException(Exception):
    """ Base class for exceptions of agent """
    pass

# --------------------------------------------------------
# Define Delegator component
# --------------------------------------------------------

class Delegator(Agent):
    """ Represents the agent that delegates the execution of actions to other agents """
    
    def __init__(self, agent_id:str) -> None:
        """ Constructor
        @param agent_id: Agent ID
        """
        self.__agentList = []
        super().__init__(agent_id)

    def setup(self) -> None:
        """ Set up method """
        self._social = True
        # Defines the agent state
        self.state = {}
        # Defines the delegate behavior        
        self.add_behavior('Delegate')
        # Defines the space for build
        self.build()

    def bindDelegateAction(self, action:Action) -> None:
        """ Binds the delegate action to the agent
        @param action: Delegate action
        """
        self.bind_action('Delegate', 'delegate', action)

    def suscribeAgent(self, agent: Agent) -> None:
        """ Suscribes an agent to the delegate agent
        @param agent: Agent
        """
        if not isinstance(agent, Agent):
            raise DelegatorException('[Warn, suscribeAgent]: The object to subscribe is not an agent')
        self.__agentList.append(agent.id)

    @abstractmethod
    def build(self) -> None:
        """ Build method """
        pass

    def start(self) -> None:
        """ Start method """
        if len(self.__agentList) <= 0:
            raise DelegatorException('[Warn, start]: Delegate agent list is empty. Agents must be subscribed to the Delegate Agent')
        super().start()

    def getAgentList(self) -> list:
        """ Get the agent
        @return: Agent list
        """
        return self.__agentList