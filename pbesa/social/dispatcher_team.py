# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 09/08/24

The Dispatcher Team is a group of artificial intelligence 
agents coordinated by a controller that acts as a task 
dispatcher. Unlike teams that consolidate responses, 
in this system, the controller simply assigns the task to 
the first available agent. Each agent operates 
independently and responds through Controller to the 
client once they have processed the assigned task.

When the client sends a request, the controller directs 
it to the agent who is free at that moment. If all agents 
are busy, the request is put on hold until one of them 
becomes available to handle it. This approach ensures 
quick and efficient responses, optimizing the use of 
available resources.

The Dispatcher Team is ideal for scenarios where fast and 
direct responses are crucial, as it minimizes wait times 
and simplifies task management, allowing the team to 
operate in an agile and effective manner.
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

from enum import Enum
from abc import abstractmethod
from .worker import Task, Worker
from ..kernel.agent import Queue
from ..kernel.agent import Agent
from ..kernel.agent import Action
from ..kernel.util import generate_short_uuid

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
 
class DispatcherException(Exception):
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
        ag = self.agent.get_free_queue().get()
        self.agent.get_request_dict()[ag] = {
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
        ag = self.agent.get_free_queue().get()
        self.agent.get_request_dict()[ag] = {
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
        self.agent.get_free_queue().put(data)

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

    def execute(self, data: dict) -> None:
        """ Execute
        @param data: Data
        """
        request = self.agent.get_request_dict()[data['source']]
        if 'timeout' in data:
            self.send_response(request)
        else:
            request['dtoList'].append(data['result'])
            if len(request['dtoList']) >= self.agent.get_buffer_size():
                self.send_response(request)

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class DispatcherController(Agent):
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
        self.__request_dict = {}
        self.__free_queue = Queue(pool_size)
        self.__agent_list = []
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
            raise DispatcherException('[Warn, bindDelegateAction]: The controller is a blocking type. No need to define delegator')

    def suscribe_agent(self, agent:Agent) -> None:
        """ Suscribes an agent to the controller
        @param agent: Agent
        """
        self.__agent_list.append(agent.id)
        agent.set_controller(self.id)
        agent.set_controller_type('POOL')
        self.__free_queue.put(agent.id)
        actions = agent.get_actions()
        for action in actions:
            action.set_is_pool(True)
            action.set_enable_response(self.__type == PoolType.BLOCK)

    def suscribe_remote_agent(self, agent_id:str) -> None:
        """ Suscribes an agent to the controller
        @param agent_id: Agent ID
        """
        if not isinstance(agent_id, str):
            raise DispatcherException('[Warn, suscribeRemoteAgent]: The object to subscribe is not an agent ID')
        self.__agent_list.append(agent_id)
        self.__free_queue.put(agent_id)
    
    def broadcast_event(self, event:any, data:any) -> None:
        """ Broadcasts an event to the agents
        @param event: Event
        @param data: Data
        """
        from pbesa.kernel.system.adm import Adm
        for agent_id in self.__agent_list:
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
        return self.__request_dict

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


# --------------------------------------------------------
# Builder Methods
# --------------------------------------------------------

# --------------------------------------------------------
# Define Dispacher Agent

class DispacherAgent(DispatcherController):
    """ Through a class the concept of agent is defined """
        
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        pass

    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass

# --------------------------------------------------------
# Define Worker Agent

class WorkerAgent(Worker):
    """ Through a class the concept of agent is defined """

    def __init__(self, agent_id:str, task:Task) -> None:
        """ Constructor
        @param agent_id: Agent ID
        @param task: Task
        """
        self.__task = task
        super().__init__(agent_id)
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bind_task(self.__task)
        
    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass

# --------------------------------------------------------
# Define build Method

def build_dispatcher_controller(name_team:str, agent_count, task:Task) -> DispatcherController:
    """ Builds the controller
    @param name_team: Team name
    @param agent_count: Agent count
    @param task: Task
    @return: Controller
    """
    # Define worker agent list
    w_ag_list = []
    # Iterate over the number of agents
    for i in range(agent_count):
        w_id = f"{name_team}-ag-{i}"
        # Create the agent
        w_ag = WorkerAgent(w_id, task)
        # Start the agent
        w_ag.start()
        # Add the agent to the list
        w_ag_list.append(w_ag)
    # Create the controller
    dispatcher = DispacherAgent(name_team, PoolType.BLOCK, 1, agent_count)
    # Subscribe the agents to the controller
    for w_ag in w_ag_list:
        dispatcher.suscribe_agent(w_ag)
    # Start the controller
    dispatcher.start()
    # Return the controller
    return dispatcher