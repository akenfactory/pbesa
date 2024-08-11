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

from enum import Enum
from abc import abstractmethod
from ..kernel.agent import Queue
from ..kernel.agent import Agent
from ..kernel.agent import Action


# --------------------------------------------------------
# Define PoolType
# --------------------------------------------------------

class PoolType(Enum):
    """ Represents the pool type """

    # Block
    BLOCK = 1
    # No block
    NO_BLOCK = 2

# ----------------------------------------------------------
# Defines system component exceptions
# ----------------------------------------------------------
 
class SimultaneousException(Exception):
    """ Base class for exceptions of agent """
    pass

# --------------------------------------------------------
# Define Delegate Action
# --------------------------------------------------------

class Delegate(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data: any) -> None:
        """ 
        Response.
        @param data Event data 
        """
        ag = self.agent.getFreeQueue().get()
        self.agent.getRequestDict()[ag] = {
            'gateway': data['gateway'],
            'dtoList': []
        }
        self.adm.send_event(ag, 'task', data['dto'])

# --------------------------------------------------------
# Define DelegateAction
# --------------------------------------------------------

class DelegateAction(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data: any) -> None:
        """ 
        Response.
        @param data Event data 
        """
        self.delegate(data)
    
    def active_timeout(self, time: int) -> None:
        """ Active timeout
        @param time: Time
        """
        self.adm.send_event(self.agent.id, 'timeout', {'time': time, 'dto': None})

    def to_assign(self, data: any) -> None:
        """ Assign
        @param data: Data
        """
        ag = self.agent.getFreeQueue().get()
        self.agent.getRequestDict()[ag] = {
            'dtoList': []
        }
        self.adm.send_event(ag, 'task', data)

    @abstractmethod
    def delegate(self, data: any) -> None:
        """ Delegate
        @param data: Data
        """
        pass

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------

class NotifyFreeAction(Action):
    """ An action is a response to the occurrence of an event """
    
    def execute(self, data: any) -> None:
        """ 
        Response.
        @param data Event data 
        """
        self.agent.getFreeQueue().put(data)

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------

class ResponseAction(Action):
    """ An action is a response to the occurrence of an event """
    
    def send_response(self, request: dict) -> None:
        """ Send response
        @param request: Request
        """
        if len(request['dtoList']) == 1:
            request['gateway'].put(request['dtoList'][0])
        else:
            request['gateway'].put(request['dtoList'])

    def execute(self, data: any) -> None:
        """ Execute
        @param data: Data
        """
        request = self.agent.getRequestDict()[data['source']]
        if 'timeout' in data:
            self.send_response(request)
        else:
            request['dtoList'].append(data['result'])
            if len(request['dtoList']) >= self.agent.getBufferSize():
                self.send_response(request)

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class SimultaneousController(Agent):
    """ Represents the agent that delegates the execution of actions to other agents """
    
    def __init__(self, agent_id:str, type:str, buffer_size:int, pool_size:int) -> None:
        """ Constructor
        @param agent_id: Agent ID
        @param type: Pool type
        @param buffer_size: Buffer size
        @param pool_size: Pool size
        """
        self.__type = type
        self.__pool_size = pool_size
        self.__buffer_size = buffer_size
        self.__requestDict = {}
        self.__free_queue = Queue(pool_size)
        self.__agentList = []
        super().__init__(agent_id)

    def setup(self) -> None:
        """ Set up method """
        self._social = True
        self.add_behavior('Delegate')
        if self.__type == PoolType.BLOCK:
            self.bind_action('Delegate', 'delegate', Delegate())
        self.add_behavior('Notify')
        self.bind_action('Notify', 'notify', NotifyFreeAction())
        # TODO Para el bloquenate debe ser por defecto
        # Para el no bloquenate ?
        self.add_behavior('Response')
        self.bind_action('Response', 'response', ResponseAction())
        self.build()

    def bind_delegate_action(self, action:Delegate) -> None:
        """ Binds the delegate action to the agent
        @param action: Delegate action
        @raise PoolException: If the controller is a blocking type
        """
        if self.__type == PoolType.NO_BLOCK:
            self.bind_action('Delegate', 'delegate', action)
        else:
            raise SimultaneousException('[Warn, bindDelegateAction]: The controller is a blocking type. No need to define delegator')

    def suscribe_agent(self, agent:Agent) -> None:
        """ Suscribes an agent to the controller
        @param agent: Agent
        """
        self.__agentList.append(agent.id)
        agent.setController(self.id)
        agent.setControllerType('POOL')
        self.__free_queue.put(agent.id)
        actions = agent.getActions()
        for action in actions:
            action.setIsPool(True)
            action.setEnableResponse(self.__type == PoolType.BLOCK)

    def suscribe_remote_agent(self, agent_id:str) -> None:
        """ Suscribes an agent to the controller
        @param agent_id: Agent ID
        """
        if not isinstance(agent_id, str):
            raise SimultaneousException('[Warn, suscribeRemoteAgent]: The object to subscribe is not an agent ID')
        self.__agentList.append(agent_id)
        self.__free_queue.put(agent_id)
    
    def broadcast_event(self, event:any, data:any) -> None:
        """ Broadcasts an event to the agents
        @param event: Event
        @param data: Data
        """
        from pbesa.kernel.system.adm import Adm
        for agent_id in self.__agentList:
            Adm().send_event(agent_id, event, data)
    
    @abstractmethod
    def build(self) -> None:
        """ Builds the agent """
        pass

    def get_free_queue(self) -> Queue:
        """ Gets the free queue
        @return: Free queue
        """
        return self.__free_queue

    def get_request_dict(self) -> dict:
        """ Gets the request dictionary
        @return: Request dictionary
        """
        return self.__requestDict

    def get_buffer_size(self) -> int:
        """ Gets the buffer size
        @return: Buffer size
        """
        return self.__buffer_size

    def is_block(self) -> bool:
        """ Checks if the pool is blocking
        @return: True if the pool is blocking, False otherwise
        """
        return self.__type == PoolType.BLOCK