# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 09/08/24

The Collaborative Team consists of a controller and a 
group of agents who work together to complete tasks 
synchronously with the client. When a client submits a 
request, the controller breaks down the task into smaller 
parts, assigning each part to a specific agent. The 
agents perform their portion of the work and then send 
their results back to the controller. The controller 
then consolidates all the partial responses into a single 
comprehensive response, which is delivered to the client. 
This structure allows the team to efficiently tackle 
complex tasks by leveraging the agents' ability to work 
in parallel. By maintaining a synchronous interaction 
with the client, the Collaborative Team ensures 
that requests are managed in an organized and structured 
manner, providing a unified and cohesive response. 
This approach is ideal for situations where precision 
and consistency are essential, as it allows for close 
coordination among all team members and the delivery of 
clear and unified results.
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import logging
from threading import Timer
from abc import abstractmethod
from ..kernel.agent import Agent
from ..kernel.agent import Action

# ----------------------------------------------------------
# Defines system component exceptions
# ----------------------------------------------------------
 
class CollaborativeException(Exception):
    """ Base class for exceptions of agent """
    pass

# ----------------------------------------------------------
# Define the TimeoutAction component
# ----------------------------------------------------------

class TimeoutAction(Action):
    """ Represents the action that manages the timeout """

    def __init__(self) -> None:
        """ Constructor """
        self.__timer = None
        super().__init__()

    def handler(self) -> None:
        """ Timeout handler """
        if self.agent.is_timeout():
            self.agent.set_timeout(False)
            self.adm.send_event(self.agent.id, 'response', 'timeout')

    def execute(self, data:any) -> None:
        """ Execute the action
        @param data: Event data
        """
        if data['command'] == 'start':
            if not self.agent.is_timeout():
                self.agent.set_timeout(True)
                self.__timer = Timer(data['time'], self.handler)
                self.__timer.start()
        else:
            if self.__timer:
                self.__timer.cancel()
                self.__timer = None

# --------------------------------------------------------
# Define DelegateAction component
# --------------------------------------------------------

class DelegateAction(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data:any) -> None:
        """ 
        Response.
        @param data Event data 
        """
        self.agent.set_gateway(data['gateway'])
        self.agent.reset()
        self.delegate(data['dto'])
        
    def active_timeout(self, time:int) -> None:
        """ Active timeout
        @param time: Time
        """
        self.adm.send_event(self.agent.id, 'timeout', {'time': time, 'command': 'start'})

    def toAssign(self, data:any) -> None:
        """ Assign data to an agent
        @param data: Data
        """
        if len(self.agent.get_free_list()) > 0:
            ag = self.agent.get_free_list().pop(0)
            self.adm.send_event(ag, 'task', data)
        else:
            raise CollaborativeException('[Warn, toAssign]: The number of data packets exceeds the number of agents')
        
    def get_list_agents(self) -> list:
        """ Get list of agents
        @return: List of agents
        """
        return self.agent.get_free_list()
    
    def to_individual_assign(self, ag_id, data:any) -> bool:
        """ Assign data to an agent
        @param data: Data
        """
        if len(self.agent.get_free_list()) > 0:
            index = self.agent.get_free_list().index(ag_id)
            if index >= 0:
                self.agent.get_free_list().pop(index)
                self.adm.send_event(ag_id, 'task', data)
            else:
                return False
        else:
            raise CollaborativeException('[Warn, toAssign]: The number of data packets exceeds the number of agents')
        return True

    @abstractmethod
    def delegate(self, data:any) -> None:
        """ Delegate method
        @param data: Data
        """
        pass

    def send_response(self, response:any) -> None:
        """ Send response
        @param response: Response
        """
        self.agent.get_gateway().put(response)

# --------------------------------------------------------
# Define ResponseAction component
# --------------------------------------------------------

class ResponseAction(Action):
    """ An action is a response to the occurrence of an event """
    
    def execute(self, data:any) -> None:
        """ Execute the action
        @param data: Event data
        """
        if 'timeout' == data:
            logging.info('Timeout fired')
            if self.agent.is_timeout():
                results = {}
                for key, res in self.agent.get_check_dict().items():
                    results[key] = res
                self.end_of_process(results, True)
                logging.info('Response by TIMEOUT')
            else:
                logging.info('Timeout ignored')
        else:
            logging.info("Response received")
            logging.info(data)
            result = 'None'
            agentID = data['source']
            if 'result' in data and data['result']:
                result =  data['result']
                self.agent.get_check_dict()[agentID] = result
            else:
                logging.warning(f"No result received for agent {agentID}")
                self.agent.get_check_dict()[agentID] = "None"
            if self.check():
                logging.info("All agents have responded")
                results = {}
                for key, res in self.agent.get_check_dict().items():
                    results[key] = res
                self.end_of_process(results, False)

    def check(self):
        for res in self.agent.get_check_dict().values():
            if not res:
                return False
        return True

    def send_response(self, response:any) -> None:
        """ Send response
        @param response: Response
        """
        self.agent.set_timeout(False)
        self.adm.send_event(self.agent.id, 'timeout', {'command': 'cancel'})
        self.agent.get_gateway().put(response) 
    
    @abstractmethod
    def end_of_process(self, results:dict, timeout:int) -> None:
        """ End of process
        @param results: Results
        @param timeout: Timeout
        """
        pass

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class CollaborativeController(Agent):
    """ Represents the agent that delegates the execution of actions to other agents """
    
    def __init__(self, agent_id:str) -> None:
        """ Constructor
        @param agent_id: Agent ID
        """
        self.__agent_list = []
        self.__check_dict = {}
        self.__gateway = None
        self.__free_list = None
        self.__timeout = False
        self.__poolSize = None
        self.__request_dict = {}    
        super().__init__(agent_id)

    def setup(self) -> None:
        """ Set up method """
        self._social = True
        self.add_behavior('Timeout')
        self.bind_action('Timeout', 'timeout', TimeoutAction())
        self.add_behavior('Delegate')
        self.add_behavior('Response')
        self.build()

    def bind_delegate_action(self, action:DelegateAction) -> None:
        """ Binds the delegate action to the agent
        @param action: Delegate action
        """
        self.bind_action('Delegate', 'delegate', action)

    def bind_response_action(self, action:ResponseAction) -> None:
        """ Binds the response action to the agent
        @param action: Response action
        """
        self.bind_action('Response', 'response', action)

    def suscribe_agent(self, agent:Agent) -> None:
        """ Suscribes an agent to the controller
        @param agent: Agent
        """
        if not isinstance(agent, Agent):
            raise CollaborativeException('[Warn, suscribeAgent]: The object to subscribe is not an agent')
        agent.set_controller(self.id)
        agent.set_controller_type('LINEAL')
        self.__check_dict[agent.id] = None
        self.__agent_list.append(agent.id)
        actions = agent.get_actions()
        for action in actions:
            action.set_is_pool(False)
            action.set_enable_response(True)
    
    def suscribe_remote_agent(self, agent_id:str) -> None:
        """ Suscribes an agent to the controller
        @param agent_id: Agent ID
        """
        if not isinstance(agent_id, str):
            raise CollaborativeException('[Warn, suscribeRemoteAgent]: The object to subscribe is not an agent ID')
        self.__check_dict[agent_id] = None
        self.__agent_list.append(agent_id)
        
    def reset(self) -> None:
        """ Reset method """
        self.__free_list = []
        for ag in self.__agent_list:
            self.__check_dict[ag] = None
            self.__free_list.append(ag)

    @abstractmethod
    def build(self) -> None:
        """ Build method """
        pass

    def start(self) -> None:
        """ Start method """
        if len(self.__agent_list) <= 0:
            raise CollaborativeException('[Warn, toAssign]: Controller agent list is empty. Agents must be subscribed to the controller')
        super().start()

    def get_free_list(self) -> list:
        """ Get free list
        @return: Free list
        """
        return self.__free_list

    def get_request_dict(self) -> dict:
        """ Get request dictionary
        @return: Request dictionary
        """
        return self.__request_dict

    def get_gateway(self) -> str:
        """ Get gateway
        @return: Gateway
        """
        return self.__gateway

    def set_gateway(self, gateway:str) -> None:
        """ Set gateway
        @param gateway: Gateway
        """
        self.__gateway = gateway

    def get_check_dict(self) -> dict:
        """ Get check dictionary
        @return: Check dictionary
        """
        return self.__check_dict
    
    def is_timeout(self) -> bool:
        """ Check if the controller has a timeout
        @return: True if the controller has a timeout, False otherwise
        """
        return self.__timeout

    def set_timeout(self, timeout:bool) -> None:
        """ Set timeout
        @param timeout: Timeout
        """
        self.__timeout = timeout

    def is_block(self) -> bool:
        """ Check if the controller is blocked
        @return: True if the controller is blocked, False otherwise
        """
        return True
