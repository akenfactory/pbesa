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

from threading import Timer
from abc import abstractmethod
from ..kernel.agent import Agent
from ..kernel.agent import Action

# ----------------------------------------------------------
# Defines system component exceptions
# ----------------------------------------------------------
 
class TaskException(Exception):
    """ Base class for exceptions of agent """
    pass

class WorkerException(Exception):
    """ Base class for exceptions of agent """
    pass

# ----------------------------------------------------------
# Define the TimeoutAction
# ----------------------------------------------------------

class TimeoutAction(Action):
    """
    @See Action
    """

    def handler(self) -> None:
        """ Timeout handler """
        if self.agent.is_timeout():
            self.agent.set_timeout(False)
            self.adm.send_event(self.agent.id, 'response', 'timeout')

    def execute(self, data:any) -> None:
        """ Execute
        @param data: Data
        """
        if not self.agent.is_timeout():
            self.agent.set_timeout(True)
            r = Timer(data['time'], self.handler)
            r.start()

# --------------------------------------------------------
# Define Task Action
# --------------------------------------------------------

class Task(Action):
    """ An action is a response to the occurrence of an event """

    def __init__(self) -> None:
        self.__is_pool = False
        self.__enable_response = False
        super().__init__()

    def execute(self, data:any) -> None:
        """ 
        Response.
        @param data Event data 
        """
        self.run(data)

        if self.__is_pool:
            self.adm.send_event(self.agent.get_controller(), 'notify', self.agent.id)

    def active_timeout(self, time:int) -> None:
        """ Active timeout
        @param time: Time
        """       
        self.adm.send_event(self.agent.id, 'timeout', {'time': time, 'dto': None})

    def send_response(self, data:any) -> None:
        """ Send response
        @param data: Data
        """
        if self.__enable_response:
            response = {
                'source': self.agent.id,
                'result': data
            }
            self.adm.send_event(self.agent.get_controller(), 'response', response) 
        else:
            raise TaskException('[Warn, sendResponse]: The type of control does not allow synchronous responses (see Linear or Pool type Block)')
    
    @abstractmethod
    def run(self, data:any) -> None:
        """ Run
        @param data: Data
        """
        pass

    def set_is_pool(self, is_pool:bool) -> None:
        """ Set is pool
        @param is_pool: Is pool
        """
        self.__is_pool = is_pool
    
    def set_enable_response(self, enable_response) -> None:
        """ Set enable response
        @param enable_response: Enable response
        """
        self.__enable_response = enable_response

# --------------------------------------------------------
# Define Worker component
# --------------------------------------------------------

class Worker(Agent):
    """ Represents the agent that executes the actions """

    def __init__(self, agent_id:str) -> None:
        """ Constructor
        @param agent_id: Agent ID
        """
        self.__task_list = []
        self.__controller = None
        self.__controller_type = None    
        super().__init__(agent_id)

    def setup(self) -> None:
        """ Set up method """
        self.add_behavior('Task')
        self.add_behavior('Timeout')
        self.bind_action('Timeout', 'timeout', TimeoutAction())
        self.build()

    def bind_task(self, action:Task) -> None:
        """ Bind task
        @param action: Task
        """
        if isinstance(action, Task):
            self.__task_list.append(action)    
            self.bind_action('Task', 'task', action)
        else:
            raise WorkerException('[Warn, bindTask]: The action must inherit from the task type')

    def suscribe_remote_controller(self, controller_id:str) -> None:
        """ Suscribe remote controller
        @param controller_id: Controller ID
        """
        self.set_controller(controller_id)
        self.set_controller_type('LINEAL')
        actions = self.get_actions()
        for action in actions:
            action.set_is_pool(False)
            action.set_enable_response(True)

    @abstractmethod
    def build(self) -> None:
        """ Build """
        pass

    def get_actions(self) -> list:
        """ Get actions
        @return: Actions
        """
        return self.__task_list

    def get_controller(self) -> str:
        """ Get controller
        @return: Controller
        """
        return self.__controller

    def set_controller(self, controller:str) -> None:
        """ Set controller
        @param controller: Controller
        """
        self.__controller = controller

    def set_controller_type(self, controller_type:str) -> None:
        """ Set controller type
        @param controller_type: Controller type
        """
        self.__controller_type = controller_type