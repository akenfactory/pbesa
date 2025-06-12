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

import logging
import traceback
import pandas as pd
from abc import abstractmethod
from .worker import Task, Worker
from ..kernel.agent import Queue
from ..kernel.agent import Agent
from ..kernel.agent import Action
from ..kernel.util import generate_short_uuid
from ..cognitive import Dialog, AugmentedGeneration
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# ----------------------------------------------------------
# Defines system component exceptions
# ----------------------------------------------------------
 
class DispatcherException(Exception):
    """ Base class for exceptions of agent """
    pass

# --------------------------------------------------------
# Define Delegate Action
# --------------------------------------------------------

class AgentDto():
    """ Data Transfer Object """
    def __init__(self, agent_id:str) -> None:
        """ Constructor
        @param agent_id: Agent ID
        """
        self.id = agent_id

class SelectedDispatcher(Action):
    """ An action is a response to the occurrence of an event """

    def __init__(self) -> None:
        """ Constructor """  
        super().__init__()
        self.__rewier = {}
        self.planilla = {}

    def active_timeout(self, ag, time: int) -> None:
        """ Active timeout
        @param time: Time
        """
        logging.info(f"[Delegate] Send event timeout {time}")
        self.adm.send_event(ag, 'timeout', {'time': time, 'command': 'start'})

    def calculate_close(self, description, data: any) -> bool:
        """ Check close
        @param data: Data
        @return: True if the agent is closed, False otherwise
        """
        text1 = description
        text2 = data['dto']['text'] if data and 'dto' in data and data['dto']['text'] is not None else ''
        logging.info(f"Text1: {text1}")
        logging.info(f"Query: {text2}")
        documents = [text1, text2]
        count_vectorizer = CountVectorizer()
        sparse_matrix = count_vectorizer.fit_transform(documents)
        doc_term_matrix = sparse_matrix.todense()
        df = pd.DataFrame(
            doc_term_matrix,
            columns=count_vectorizer.get_feature_names_out(),
            index=[text1, text2],
        )
        res = cosine_similarity(df, df)
        similarity = res[0][1]
        return similarity

    @abstractmethod    
    def manual_selection(self, data: any) -> object:
        """ Manual selection
        @param data: Data
        @return: Tuple with the agent and the score
        """
        raise NotImplementedError("The method manual_selection must be implemented in the subclass")
    
    def execute(self, data: any) -> None:
        """ 
        Response.
        @param data Event data 
        """
        try:
            logging.info('Assign to agent...')
            session_id = data['dto']['session']['session_id'] if 'session' in data['dto'] else None
            agent_list = self.agent.get_agent_list()
            agent_count = len(agent_list)
            logging.debug('List of agents: ' + str(agent_list))
            if session_id in self.planilla:
                mayor_ag_id = self.planilla[session_id]
                logging.info('The session is already assigned')
                logging.info(f'The agent {mayor_ag_id} will be assigned')
                exit = False
                while not exit:
                    ag = self.agent.get_free_queue().get()
                    agent_obj = self.adm.get_agent(ag)
                    # Get the role
                    if mayor_ag_id == agent_obj.id:
                        logging.info(f'The agent {ag} is assigned')
                        self.agent.get_request_dict()[ag] = {
                            'gateway': data['gateway'],
                            'dtoList': []
                        }
                        self.adm.send_event(ag, 'task', data['dto'])
                        self.__rewier[ag] = 0
                        exit = True
                    else:
                        logging.debug('The agent does not match the role')
                        self.adm.send_event(agent_obj.get_controller(), 'notify', ag)
                        if ag in self.__rewier:
                            self.__rewier[ag] = self.__rewier[ag] + 1
                        else:
                            self.__rewier[ag] = 0
                        if self.__rewier[ag] >= agent_count * 3:
                            data['gateway'].put('ERROR')
                            logging.error('[Error, toAssign]: The agent is not available')
            else:
                score_mayor = 0 
                mayor_ag = self.manual_selection(data['dto'])
                if mayor_ag:
                    score_mayor = 7
                else:
                    # Get the agent asocciated with the data.
                    for agent_id in agent_list:
                        agent = self.adm.get_agent(agent_id)
                        # Chec if the agent is instance of AugmentedGeneration
                        if isinstance(agent, Dialog) or isinstance(agent, AugmentedGeneration):
                            # Get the role
                            role = agent.get_role()
                            score = self.calculate_close(role.description, data)
                            logging.info(f"Score: {score}")
                            if score > score_mayor:
                                score_mayor = score
                                mayor_ag = agent
                        else:
                            logging.info(f"The {agent_id} is not instance of AugmentedGeneration or Dialog")
                # Check if the mayor agent is the same as the agent        
                if score_mayor < 2:
                    logging.info(f'The agent {mayor_ag.id} will be assigned')
                    exit = False
                    while not exit:
                        ag = self.agent.get_free_queue().get()
                        agent_obj = self.adm.get_agent(ag)
                        # Chec if the agent is instance of AugmentedGeneration
                        if isinstance(agent_obj, Dialog) or isinstance(agent_obj, AugmentedGeneration):
                            # Get the role
                            if mayor_ag.id == agent_obj.id:
                                logging.info(f'The agent {ag} is assigned')
                                self.agent.get_request_dict()[ag] = {
                                    'gateway': data['gateway'],
                                    'dtoList': []
                                }
                                self.adm.send_event(ag, 'task', data['dto'])
                                self.__rewier[ag] = 0
                                exit = True
                                self.planilla[session_id] = mayor_ag.id
                            else:
                                logging.debug('The agent does not match the role')
                                self.adm.send_event(agent_obj.get_controller(), 'notify', ag)
                                if ag in self.__rewier:
                                    self.__rewier[ag] = self.__rewier[ag] + 1
                                else:
                                    self.__rewier[ag] = 0
                                if self.__rewier[ag] >= agent_count * 3:
                                    data['gateway'].put('ERROR')
                                    logging.error('[Error, toAssign]: The agent is not available')
                        else:
                            self.agent.get_request_dict()[ag] = {
                                'gateway': data['gateway'],
                                'dtoList': []
                            }
                            self.adm.send_event(ag, 'task', data['dto'])
                            exit = True
                else:
                    ag = self.agent.get_free_queue().get()
                    self.agent.get_request_dict()[ag] = {
                        'gateway': data['gateway'],
                        'dtoList': []
                    }
                    self.adm.send_event(ag, 'task', data['dto'])
                # Check timeout    
                if 'timeout' in self.agent.state:
                    self.active_timeout(ag, self.agent.state['timeout'])
                else:
                    data['gateway'].put('ERROR')
                    logging.error('[Delegate]: Timeout not defined in the state as "timeout" key')
        except Exception as e:
            traceback.print_exc()
            logging.error(f"[Delegate][{self.agent.id}]: {str(e)}")
            data['gateway'].put('ERROR')
    
    def get_planilla(self) -> dict:
        return self.planilla

# --------------------------------------------------------
# Define Delegate Action by default
# --------------------------------------------------------

class Delegate(Action):
    """ An action is a response to the occurrence of an event """

    def active_timeout(self, ag, time: int) -> None:
        """ Active timeout
        @param time: Time
        """
        logging.info(f"[Delegate] Send event timeout {time}")
        self.adm.send_event(ag, 'timeout', {'time': time, 'command': 'start'})

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
        logging.info(f"[Delegate][{self.agent.id}]: Assign to agent {ag}")
        self.adm.send_event(ag, 'task', data['dto'])
        logging.info(f"[Delegate][{self.agent.id}]: Agent {ag} assigned")
        if 'timeout' in self.agent.state:
            self.active_timeout(ag, self.agent.state['timeout'])
        else:
            raise DispatcherException('[Delegate]: Timeout not defined in the state as "timeout" key')

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
        #@TODO: Check if the data is valid
        #logging.info(f"[ResponseAction][{self.agent.id}]: Obtiene respuesta")
        if data['source'] in self.agent.get_request_dict():
            request = self.agent.get_request_dict()[data['source']]
        
            if 'timeout' in data:
                logging.info(f"[ResponseAction][{self.agent.id}]: Timeout ******************")
                request['gateway'].put("TIMEOUT")
            else:
                request['dtoList'].append(data['result'])
                if len(request['dtoList']) >= self.agent.get_buffer_size():
                    self.send_response(request)
                    self.adm.send_event(data['source'], 'timeout', {'command': 'stop'})
                    if data['reset']:
                        logging.info(f"[ResponseAction][{self.agent.id}]: Reset ******************")
                        delegate = self.agent.get_delegate()
                        print(f"Delegate: {delegate}")
                        planilla = delegate.get_planilla()
                        print(f"Planilla: {planilla}")
                        planilla.pop(data['session_id'], None)
                        logging.info(f"[ResponseAction][{self.agent.id}]: Planilla: actualizada")
        else:
            logging.warning(f"[ResponseAction][{self.agent.id}]: Warning ******************")
            logging.warning(f"[ResponseAction][{self.agent.id}]: {data}")

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class DispatcherController(Agent):
    """ Represents the agent that delegates the execution of actions to other agents """
    
    def __init__(self, agent_id:str, buffer_size:int, pool_size:int, delegate=None) -> None:
        """ Constructor
        @param agent_id: Agent ID
        @param type: Pool type
        @param buffer_size: Buffer size
        @param pool_size: Pool size
        """
        self.__buffer_size = buffer_size
        self.__request_dict = {}
        self.__pool_size = pool_size
        self.__free_queue = Queue(pool_size)
        self.__agent_list = []
        self.__delegate = delegate
        self.__delegate_obj = None
        super().__init__(agent_id)

    def setup(self) -> None:
        """ Set up method """
        self._social = True
        self.add_behavior('Delegate')
        if self.__delegate:
            self.__delegate_obj = self.__delegate()
            self.bind_action('Delegate', 'delegate', self.__delegate_obj)
        else:
            self.bind_action('Delegate', 'delegate', Delegate())
        self.add_behavior('Notify')
        self.bind_action('Notify', 'notify', NotifyFreeAction())
        self.add_behavior('Response')
        self.bind_action('Response', 'response', ResponseAction())
        self.build()

    def suscribe_agent(self, agent:Agent) -> None:
        """ Suscribes an agent to the controller
        @param agent: Agent
        """
        self.__agent_list.append(agent.id)
        agent.set_controller(self.id)
        agent.set_controller_type('POOL')
        if len(self.__agent_list) > self.__pool_size:
            raise DispatcherException('[Warn, suscribeAgent]: The pool is full')
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
            raise DispatcherException('[Warn, suscribeRemoteAgent]: The object to subscribe is not an agent ID')
        self.__agent_list.append(agent_id)
        self.__free_queue.put(agent_id)
    
    def broadcast_event(self, event:any, data:any) -> None:
        """ Broadcasts an event to the agents
        @param event: Event
        @param data: Data
        """
        from ..mas import Adm
        for agent_id in self.__agent_list:
            Adm().send_event(agent_id, event, data)
    
    @abstractmethod
    def build(self) -> None:
        """ Builds the agent """
        pass

    def get_agent_list(self) -> list:
        """ Gets the agent list
        @return: Agent list
        """
        return self.__agent_list

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
    
    def get_delegate(self) -> Action:
        """ Gets the delegate
        @return: Delegate
        """
        return self.__delegate_obj

    def is_block(self) -> bool:
        """ Checks if the pool is blocking
        @return: True if the pool is blocking, False otherwise
        """
        return True


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

def build_dispatcher_controller(name_team:str, agent_count, task_class:Task) -> DispatcherController:
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
    dispatcher = DispacherAgent(name_team, 1, agent_count)
    # Subscribe the agents to the controller
    for w_ag in w_ag_list:
        dispatcher.suscribe_agent(w_ag)
    # Start the controller
    dispatcher.start()
    # Return the controller
    return dispatcher


class LLMDispatcherDelegate(Action):
    """ An action is a response to the occurrence of an event """

    def __init__(self) -> None:
        """ Constructor """  
        super().__init__()
        self.__rewier = {}
        self.planilla = {}

    def active_timeout(self, ag, time: int) -> None:
        """ Active timeout
        @param time: Time
        """
        logging.info(f"[Delegate] Send event timeout {time}")
        self.adm.send_event(ag, 'timeout', {'time': time, 'command': 'start'})
    
    @abstractmethod    
    def manual_selection(self, data: any) -> object:
        """ Manual selection
        @param data: Data
        @return: Tuple with the agent and the score
        """
        raise NotImplementedError("The method manual_selection must be implemented in the subclass")
    
    def execute(self, data: any) -> None:
        """ 
        Response.
        @param data Event data 
        """
        try:
            logging.info('Assign to agent...')
            session_id = data['dto']['session']['session_id'] if 'session' in data['dto'] else None
            agent_list = self.agent.get_agent_list()
            agent_count = len(agent_list)
            logging.debug('List of agents: ' + str(agent_list))
            if session_id in self.planilla:
                mayor_ag_id = self.planilla[session_id]
                logging.info('The session is already assigned')
                logging.info(f'The agent {mayor_ag_id} will be assigned')
                exit = False
                while not exit:
                    ag = self.agent.get_free_queue().get()
                    agent_obj = self.adm.get_agent(ag)
                    # Get the role
                    if mayor_ag_id == agent_obj.id:
                        logging.info(f'The agent {ag} is assigned')
                        self.agent.get_request_dict()[ag] = {
                            'gateway': data['gateway'],
                            'dtoList': []
                        }
                        self.adm.send_event(ag, 'task', data['dto'])
                        self.__rewier[ag] = 0
                        exit = True
                    else:
                        logging.debug('The agent does not match the role')
                        self.adm.send_event(agent_obj.get_controller(), 'notify', ag)
                        if ag in self.__rewier:
                            self.__rewier[ag] = self.__rewier[ag] + 1
                        else:
                            self.__rewier[ag] = 0
                        if self.__rewier[ag] >= agent_count * 3:
                            data['gateway'].put('ERROR')
                            logging.error('[Error, toAssign]: The agent is not available')
            else:
                select_agent = self.manual_selection(data['dto'])
                # Check if agent was selected
                if not select_agent:
                    select_agent = self.agent.special_dispatch(data)
                # Check if agent was selected        
                if select_agent:
                    logging.info(f'The agent {select_agent} will be assigned')
                    exit = False
                    while not exit:
                        ag = self.agent.get_free_queue().get()
                        agent_obj = self.adm.get_agent(ag)
                        # Chec if the agent is instance of AugmentedGeneration
                        if isinstance(agent_obj, Dialog):
                            # Get the role
                            if select_agent == agent_obj.id:
                                logging.info(f'The agent {ag} is assigned')
                                self.agent.get_request_dict()[ag] = {
                                    'gateway': data['gateway'],
                                    'dtoList': []
                                }
                                self.adm.send_event(ag, 'task', data['dto'])
                                self.__rewier[ag] = 0
                                exit = True
                                self.planilla[session_id] = select_agent
                            else:
                                logging.debug('The agent does not match the role')
                                self.adm.send_event(agent_obj.get_controller(), 'notify', ag)
                                if ag in self.__rewier:
                                    self.__rewier[ag] = self.__rewier[ag] + 1
                                else:
                                    self.__rewier[ag] = 0
                                if self.__rewier[ag] >= agent_count * 3:
                                    data['gateway'].put('ERROR')
                                    logging.error('[Error, toAssign]: The agent is not available')
                        else:
                            self.agent.get_request_dict()[ag] = {
                                'gateway': data['gateway'],
                                'dtoList': []
                            }
                            self.adm.send_event(ag, 'task', data['dto'])
                            exit = True
                else:
                    ag = self.agent.get_free_queue().get()
                    self.agent.get_request_dict()[ag] = {
                        'gateway': data['gateway'],
                        'dtoList': []
                    }
                    self.adm.send_event(ag, 'task', data['dto'])
                # Check timeout    
                if 'timeout' in self.agent.state:
                    self.active_timeout(ag, self.agent.state['timeout'])
                else:
                    data['gateway'].put('ERROR')
                    logging.error('[Delegate]: Timeout not defined in the state as "timeout" key')
        except Exception as e:
            traceback.print_exc()
            logging.error(f"[Delegate][{self.agent.id}]: {str(e)}")
            data['gateway'].put('ERROR')
            
    def get_planilla(self) -> dict:
        return self.planilla
