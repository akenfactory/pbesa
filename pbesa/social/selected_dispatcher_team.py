# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 09/08/24

The Selected Dispatcher Team is a group of artificial intelligence 
agents coordinated by a controller that acts as a task 
dispatcher with selection. Unlike teams that consolidate responses, 
in this system, the controller assigns the task to delegate agent 
accord to selection function. Each agent operates 
independently and responds through Controller to the 
client once they have processed the assigned task.

When the client sends a request, the controller directs 
it to the agent who is free at that moment. If all agents 
are busy, the request is put on hold until one of them 
becomes available to handle it. This approach ensures 
quick and efficient responses, optimizing the use of 
available resources.

The Selected Dispatcher Team is ideal for scenarios where
is required to select the agent to handle the task, as it 
direct responses are crucial, as it minimizes wait times 
and simplifies task management, allowing the team to 
operate in an agile and effective manner.
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

from abc import abstractmethod

from pbesa.cognitive import AugmentedGeneration, Dialog
from pbesa.mas import Directory

from .worker import Task, Worker
from ..kernel.agent import Queue
from ..kernel.agent import Agent
from ..kernel.agent import Action
from ..kernel.util import generate_short_uuid

# ----------------------------------------------------------
# Defines system component exceptions
# ----------------------------------------------------------
 
class SelectedDispatcherException(Exception):
    """ Base class for exceptions of agent """
    pass

# --------------------------------------------------------
# Define DelegateAction
# --------------------------------------------------------

class DelegateAction(Action):
    """ An action is a response to the occurrence of an event """

    def __init__(self) -> None:
        """ Constructor """  
        super().__init__()
        self.__rewier = {}

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

    def to_assign(self, data: any, operation=None) -> None:
        """ Assign
        @param data: Data
        """
        print('Assign to agent')
        ag = self.agent.get_free_queue().get()
        agent_obj = self.adm.get_agent(ag)
        agent_count = len(self.agent.get_agent_list()) 
        if operation:
            print(f'With operation {operation}')
            exit = False
            while not exit:
                # Chec if the agent is instance of AugmentedGeneration
                if isinstance(agent_obj, AugmentedGeneration) or isinstance(agent_obj, Dialog):
                    # Get the role
                    role = agent_obj.get_role()
                    if role.tool == operation:
                        self.agent.get_request_dict()[ag] = {
                            'gateway': data['gateway'],
                            'dtoList': []
                        }
                        self.adm.send_event(ag, 'task', data['dto']['text'])
                        self.__rewier[ag] = 0
                        exit = True
                    else:
                        print('The agent is not available')
                        self.adm.send_event(agent_obj.get_controller(), 'notify', ag)
                        if ag in self.__rewier:
                            self.__rewier[ag] = self.__rewier[ag] + 1
                        else:
                            self.__rewier[ag] = 0
                        if self.__rewier[ag] >= agent_count * 3:
                            raise SelectedDispatcherException('[Error, toAssign]: The agent is not available')
                else:
                    print('The agent is operational')
                    self.adm.send_event(agent_obj.get_controller(), 'notify', ag)
                    if ag in self.__rewier:
                        self.__rewier[ag] = self.__rewier[ag] + 1
                    else:
                        self.__rewier[ag] = 0
                    if self.__rewier[ag] >= agent_count * 3:
                        raise SelectedDispatcherException('[Error, toAssign]: The agent is not available')
        else:
            print('Without operation')
            self.agent.get_request_dict()[ag] = {
                'gateway': data['gateway'],
                'dtoList': []
            }
            self.adm.send_event(ag, 'task', data['dto'])

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

class SelectedDispatcherController(Agent):
    """ Represents the agent that delegates the execution of actions to other agents """
    
    def __init__(self, agent_id:str, buffer_size:int, pool_size:int) -> None:
        """ Constructor
        @param agent_id: Agent ID
        @param type: Pool type
        @param buffer_size: Buffer size
        @param pool_size: Pool size
        """
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

    def bind_delegate_action(self, action:DelegateAction) -> None:
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
            action.set_enable_response(True)

    def suscribe_remote_agent(self, agent_id:str) -> None:
        """ Suscribes an agent to the controller
        @param agent_id: Agent ID
        """
        if not isinstance(agent_id, str):
            raise SelectedDispatcherException('[Warn, suscribeRemoteAgent]: The object to subscribe is not an agent ID')
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
    
    def get_agent_list(self) -> list:
        """ Gets the agent list
        @return: Agent list
        """
        return self.__agent_list

    def is_block(self) -> bool:
        """ Checks if the pool is blocking
        @return: True if the pool is blocking, False otherwise
        """
        return True


# --------------------------------------------------------
# Builder Methods
# --------------------------------------------------------

# --------------------------------------------------------
# Define Selected Dispacher Agent

class SelectedDispacherAgent(SelectedDispatcherController):
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

def build_selected_dispatcher(name_team:str, agent_count, task_class:Task) -> SelectedDispatcherController:
    """ Builds the controller
    @param name_team: Team name
    @param agent_count: Agent count
    @param task_class: Task Class
    @return: Controller
    """
    # Define worker agent list
    w_ag_list = []
    # Iterate over the number of agents
    for i in range(agent_count):
        short_uuid = generate_short_uuid()
        w_id = f"worker-agent-{i}-{short_uuid}"
        # Create the agent
        w_ag = WorkerAgent(w_id, task_class())
        # Start the agent
        w_ag.start()
        # Add the agent to the list
        w_ag_list.append(w_ag)
    # Create the controller
    dispatcher = SelectedDispatcherController(name_team, 1, agent_count)
    # Subscribe the agents to the controller
    for w_ag in w_ag_list:
        dispatcher.suscribe_agent(w_ag)
    # Start the controller
    dispatcher.start()
    # Return the controller
    return dispatcher