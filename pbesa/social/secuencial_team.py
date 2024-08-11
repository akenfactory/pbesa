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
 
class SecuencialException(Exception):
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
        if self.agent.isTimeout():
            self.agent.setTimeout(False)
            self.adm.send_event(self.agent.id, 'response', 'timeout')

    def execute(self, data:any) -> None:
        """ Execute the action
        @param data: Event data
        """
        if data['command'] == 'start':
            if not self.agent.isTimeout():
                self.agent.setTimeout(True)
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
        self.agent.setGateway(data['gateway'])
        self.agent.reset()
        self.delegate(data['dto'])
        
    def activeTimeout(self, time:int) -> None:
        """ Active timeout
        @param time: Time
        """
        self.adm.send_event(self.agent.id, 'timeout', {'time': time, 'command': 'start'})

    def toAssign(self, data:any) -> None:
        """ Assign data to an agent
        @param data: Data
        """
        if len(self.agent.getFreeList()) > 0:
            ag = self.agent.getFreeList().pop(0)
            self.adm.send_event(ag, 'task', data)
        else:
            raise SecuencialException('[Warn, toAssign]: The number of data packets exceeds the number of agents')

    @abstractmethod
    def delegate(self, data:any) -> None:
        """ Delegate method
        @param data: Data
        """
        pass

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
            results = {}
            for key, res in self.agent.getCheckDict().items():
                results[key] = res
            self.end_of_process(results, True)
        else:
            result = 'None'
            agentID = data['source']
            if data['result']:
                result =  data['result']
            self.agent.getCheckDict()[agentID] = result
            if self.check():
                results = {}
                for key, res in self.agent.getCheckDict().items():
                    results[key] = res
                self.end_of_process(results, False)

    def check(self):
        for res in self.agent.getCheckDict().values():
            if not res:
                return False
        return True

    def send_response(self, response:any) -> None:
        """ Send response
        @param response: Response
        """
        self.agent.setTimeout(False)
        self.adm.send_event(self.agent.id, 'timeout', {'command': 'cancel'})
        self.agent.getGateway().put(response) 
    
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

class SecuencialController(Agent):
    """ Represents the agent that delegates the execution of actions to other agents """
    
    def __init__(self, agent_id:str) -> None:
        """ Constructor
        @param agent_id: Agent ID
        """
        self.__agentList = []
        self.__checkDict = {}
        self.__gateway = None
        self.__freeList = None
        self.__timeout = False
        self.__poolSize = None
        self.__requestDict = {}    
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
            raise SecuencialException('[Warn, suscribeAgent]: The object to subscribe is not an agent')
        agent.setController(self.id)
        agent.setControllerType('LINEAL')
        self.__checkDict[agent.id] = None
        self.__agentList.append(agent.id)
        actions = agent.getActions()
        for action in actions:
            action.setIsPool(False)
            action.setEnableResponse(True)
    
    def suscribe_remote_agent(self, agent_id:str) -> None:
        """ Suscribes an agent to the controller
        @param agent_id: Agent ID
        """
        if not isinstance(agent_id, str):
            raise SecuencialException('[Warn, suscribeRemoteAgent]: The object to subscribe is not an agent ID')
        self.__checkDict[agent_id] = None
        self.__agentList.append(agent_id)
        
    def reset(self) -> None:
        """ Reset method """
        self.__freeList = []
        for ag in self.__agentList:
            self.__checkDict[ag] = None
            self.__freeList.append(ag)

    @abstractmethod
    def build(self) -> None:
        """ Build method """
        pass

    def start(self) -> None:
        """ Start method """
        if len(self.__agentList) <= 0:
            raise SecuencialException('[Warn, toAssign]: Controller agent list is empty. Agents must be subscribed to the controller')
        super().start()

    def get_free_list(self) -> list:
        """ Get free list
        @return: Free list
        """
        return self.__freeList

    def get_request_dict(self) -> dict:
        """ Get request dictionary
        @return: Request dictionary
        """
        return self.__requestDict

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
        return self.__checkDict
    
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
