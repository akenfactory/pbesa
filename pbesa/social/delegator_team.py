# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 09/08/24

The Delegator Team consists of one delegator and agents 
working asynchronously to handle tasks. In this team, a 
delegator transfers their responsibility to a specific 
agent who then performs the task. The interaction with 
the client is asynchronous, meaning the client does not
receive an immediate response. Agents are responsible for 
modifying client resources, such as databases or webhooks, 
making necessary updates or changes according to the 
request. 

This approach allows the delegator to focus on other 
tasks while agents manage the modifications efficiently. 
The Delegator Team is ideal for scenarios where the task
involves changes to specific resources and can be 
carried out independently from the client interaction 
process, enhancing team efficiency and flexibility.
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

from abc import abstractmethod
from .worker import Task, Worker
from ..kernel.agent import Queue
from ..kernel.agent import Agent
from ..kernel.agent import Action
from ..kernel.util import generate_short_uuid

# ----------------------------------------------------------
# Defines system component exceptions
# ----------------------------------------------------------
 
class DelegatorException(Exception):
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

class Delegator(Agent):
    """ Represents the agent that delegates the execution of actions to other agents """
    
    def __init__(self, agent_id:str, buffer_size:int, pool_size:int) -> None:
        """ Constructor
        @param agent_id: Agent ID
        @param buffer_size: Buffer size
        @param pool_size: Pool size
        """
        self.__type = type
        self.__buffer_size = buffer_size
        self.__request_dict = {}
        self.__free_queue = Queue(pool_size)
        self.__agent_list = []
        super().__init__(agent_id)

    def setup(self) -> None:
        """ Set up method """
        self._social = True
        self.add_behavior('Delegate')
        self.add_behavior('Notify')
        self.bind_action('Notify', 'notify', NotifyFreeAction())
        self.add_behavior('Response')
        self.bind_action('Response', 'response', ResponseAction())
        self.build()

    def bind_delegate_action(self, action:Delegate) -> None:
        """ Binds the delegate action to the agent
        @param action: Delegate action
        @raise PoolException: If the controller is a blocking type
        """
        self.bind_action('Delegate', 'delegate', action)
        
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
            action.set_enable_response(False)

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
        return False


# --------------------------------------------------------
# Builder Methods
# --------------------------------------------------------

# --------------------------------------------------------
# Define Dispacher Agent

class DelegatorAgent(Delegator):
    """ Through a class the concept of agent is defined """

    def __init__(self, agent_id:str, buffer_size:int, pool_size:int, delegate:DelegateAction) -> None:
        """ Constructor
        @param agent_id: Agent ID
        @param buffer_size: Buffer size
        @param pool_size: Pool size
        @param delegate: Delegate action
        """
        # Assign an action to the behavior
        self.__delegate = delegate
        super().__init__(agent_id, buffer_size, pool_size)
        
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bind_delegate_action(self.__delegate)

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

def build_delegator(name_team:str, agent_count, task_class:Task, delegate_class:DelegateAction) -> Delegator:
    """ Builds the delegator
    @param name_team: Team name
    @param agent_count: Agent count
    @param task: Task
    @param delegate: Delegate
    @return: Delegator
    """
    # Define worker agent list
    w_ag_list = []
    # Iterate over the number of agents
    for i in range(agent_count):
        short_uuid = generate_short_uuid()
        w_id = f"{name_team}-{i}-{short_uuid}"
        # Create the agent
        w_ag = WorkerAgent(w_id, task_class())
        # Start the agent
        w_ag.start()
        # Add the agent to the list
        w_ag_list.append(w_ag)
    # Create the delegator
    delegator = DelegatorAgent(name_team, 1, agent_count, delegate_class())
    # Subscribe the agents to the delegator
    for w_ag in w_ag_list:
        delegator.suscribe_agent(w_ag)
    # Start the delegator
    delegator.start()
    # Return the delegator
    return delegator