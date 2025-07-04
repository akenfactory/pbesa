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

import time
import logging
import traceback
import pandas as pd
from abc import abstractmethod
from .worker import Task, Worker
from ..kernel.agent import Queue
from ..kernel.agent import Agent
from ..kernel.agent import Action
from datetime import datetime, timedelta
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
# Define AgentDTO
# --------------------------------------------------------

class AgentDto():
    """ Data Transfer Object """
    def __init__(self, agent_id:str) -> None:
        """ Constructor
        @param agent_id: Agent ID
        """
        self.id = agent_id

# --------------------------------------------------------
# Define Buffer Dispatcher
# --------------------------------------------------------

class BufferDispatcher(Action):

    def active_timeout(self, ag, time: int) -> None:
        """ Active timeout
        @param time: Time
        """
        logging.info(f"[Delegate] Send event timeout {time}")
        self.adm.send_event(ag, 'timeout', {'time': time, 'command': 'start'})
    
    def execute(self, event: any) -> None:
        """ 
        Response.
        @param data Event event 
        """
        try:
            while self.agent.alive:
                for key, item_list in list(self.agent.hold_dict.items()):
                    for item in item_list:                        
                        data = item['data']
                        mayor_ag_id = item['mayor_ag_id']
                        session_id = item['session_id']

                        free_dict = self.agent.get_free_dict()


                        agent_id = None

                        for k in free_dict:
                            if mayor_ag_id in k:
                                agent_id = k
                                break


                        if agent_id:
                            logging.info(f'The agent {agent_id} is assigned')
                            self.agent.get_request_dict()[agent_id] = {
                                'gateway': data['gateway'],
                                'dtoList': []
                            }
                            self.adm.send_event(agent_id, 'task', data['dto'])
                            # Registra la sesion
                            self.agent.planilla[session_id] = mayor_ag_id
                            # Remove the item from the hold dict
                            self.agent.hold_dict[key].remove(item)
                            if len(self.agent.hold_dict[key]) == 0:
                                self.agent.hold_dict.pop(key, None)
                            # Remove agnebt from free dict
                            free_dict.pop(agent_id, None)
                            # Check timeout    
                            if 'timeout' in self.agent.state:
                                self.active_timeout(agent_id, self.agent.state['timeout'])                            
                            else:
                                data['gateway'].put('ERROR')
                                logging.error('[Delegate]: Timeout not defined in the state as "timeout" key')
                            break
                        else:
                            logging.debug('The agent does not match the role')
                            if self.agent.check_time(data):
                                logging.info(f"[Select]:[Dispacher]: Se mantiene el hold a: {data['dto']['text']}")
                            else:
                                logging.info(f"[Select]:[Dispacher]: Se elimina el hold a: {data['dto']['text']}")
                                self.agent.hold_dict.pop(key, None)
                                self.agent.planilla.pop(data['dto']['session']['session_id'], None)                 
                                data['gateway'].put('ERROR')
                                logging.error('[Error, toAssign]: The agent is not available')
                logging.info(f"[Select]:[Dispacher]: Hold dict elements {len(self.agent.hold_dict)}")
                time.sleep(10)
        except Exception as e:
            traceback.print_exc()
            logging.error(f"[Delegate][{self.agent.id}]: {str(e)}")

class SelectedDispatcher(Action):
    """ An action is a response to the occurrence of an event """

    def __init__(self) -> None:
        """ Constructor """  
        super().__init__()
        
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
            assistant = data['dto']['session']['assistant'] if 'session' in data['dto'] and 'assistant' in data['dto']['session'] else None            
            if assistant:
                logging.info('The session is already assigned')
                logging.info(f'The agent type: {assistant} will be assigned')
                self.agent.add_to_hold(data, assistant, session_id)
            else:
                score_mayor = 0 
                mayor_ag = self.manual_selection(data['dto'])
                if mayor_ag:
                    logging.info(f'The agent {mayor_ag.id} will be assigned')
                    self.agent.add_to_hold(data, mayor_ag.id, session_id)
                else:
                    roles = []
                    # Get the agent asocciated with the data.
                    agent_list = self.agent.get_agent_list()            
                    for agent_id in agent_list:
                        agent = self.adm.get_agent(agent_id)
                        # Chec if the agent is instance of AugmentedGeneration
                        if isinstance(agent, Dialog) or isinstance(agent, AugmentedGeneration):
                            # Get the role
                            role = agent.get_role()
                            
                            if not role.name in roles:
                                score = self.calculate_close(role.description, data)
                                logging.info(f"Score: {score}")
                                if score > score_mayor:
                                    score_mayor = score
                                    mayor_ag = agent

                            if not role.name in roles:
                                roles.append(role.name)
                        else:
                            logging.info(f"The {agent_id} is not instance of AugmentedGeneration or Dialog")
                    
                    # Check if the mayor agent is the same as the agent        
                    if mayor_ag:
                        logging.info(f'The agent {mayor_ag.id} will be assigned')
                        self.agent.add_to_hold(data, mayor_ag.id, session_id)
                    else:
                        logging.error('[Error, toAssign]: No agent found for the request')
                        data['gateway'].put('ERROR')
        except Exception as e:
            traceback.print_exc()
            logging.error(f"[Delegate][{self.agent.id}]: {str(e)}")
            data['gateway'].put('ERROR')
    
    def get_planilla(self) -> dict:
        return self.agent.planilla

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
        self.agent.get_free_dict()[data] = None

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
        self.__free_dict = {}
        self.__agent_list = []
        self.__delegate = delegate
        self.__delegate_obj = None

        self.alive = True
        self.hold_dict = {}
        self.umbral_cinco_minutos = timedelta(minutes=5)
        self.planilla = {}

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
        self.add_behavior('BufferDispatcher')
        self.bind_action('BufferDispatcher', 'buffer_dispatcher', BufferDispatcher())
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
        self.__free_dict[agent.id] = agent
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
        self.__free_dict[agent_id] = None
    
    def broadcast_event(self, event:any, data:any) -> None:
        """ Broadcasts an event to the agents
        @param event: Event
        @param data: Data
        """
        from ..mas import Adm
        for agent_id in self.__agent_list:
            Adm().send_event(agent_id, event, data)

    def check_hold(self, data):
        text = data['dto']['text']
        text_hash = hash(text)
        if text_hash in self.hold_dict:
            for item in self.hold_dict[text_hash]:
                if item['data']['dto']['text'] == text:
                    logging.info(f"[Select]:[Dispacher]: La consulta {text} ya esta en hold")
                    return True
        return False

    def check_time(self, data):
        """
        Retorna True si esta por debajo de 5 minutos,
        False en caso contrario.
        """
        item = None
        text = data['dto']['text']
        text_hash = hash(data['dto']['text'])
        current = datetime.now()
        for itm in self.hold_dict[text_hash]:
            if itm['data']['dto']['text'] == text:
                item = itm
                break
        diferencia_tiempo = current - item["lasttime"]
        return diferencia_tiempo < self.umbral_cinco_minutos

    def add_to_hold(self, data, mayor_ag_id, session_id):
        text = data['dto']['text']
        if not self.check_hold(data):
            self.hold_dict[hash(text)] = []
        self.hold_dict[hash(text)].append({
            "data": data,
            "lasttime": datetime.now(),
            "mayor_ag_id": mayor_ag_id,
            "session_id": session_id
        })
        logging.info(f"[Select]:[Dispacher]: Se asigan en el hold la consulta {data['dto']['text']}")
    

    def star_behavior(self, adm, agent_id) -> None:
        """ Active timeout
        @param time: Time
        """
        logging.info("[Delegate]: Starting periodict behavior...")
        adm.send_event(agent_id, 'buffer_dispatcher', None)
        logging.info("[Delegate]: Periodict behavior started")
        
    @abstractmethod
    def build(self) -> None:
        """ Builds the agent """
        pass

    def get_agent_list(self) -> list:
        """ Gets the agent list
        @return: Agent list
        """
        return self.__agent_list

    def get_free_dict(self) -> Queue:
        """ Gets the free queue
        @return: Free queue
        """
        return self.__free_dict

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
            response = None
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
                    select_agent, response = self.agent.special_dispatch(data)
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
                            tipo = "-".join(agent_obj.id.split('-')[0:-1])
                            if select_agent == tipo:
                                logging.info(f'The agent {ag} is assigned')
                                self.agent.get_request_dict()[ag] = {
                                    'gateway': data['gateway'],
                                    'dtoList': []
                                }
                                if response:
                                    data['dto']['rq_query'] = response
                                self.adm.send_event(ag, 'task', data['dto'])
                                self.__rewier[ag] = 0
                                exit = True
                                self.planilla[session_id] = agent_obj.id
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
