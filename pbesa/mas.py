# -*- coding: utf-8 -*-
"""
------------------------------------------------------------
-------------------------- PBESA --------------------------- 
------------------------------------------------------------

@autor AKEN & SIDRE
@version 3.0.1
@date 27/07/20
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import gc
import json
import base64
import socket
import traceback
from time import sleep
from pymongo import MongoClient
from .kernel.agent import Agent
from .kernel.agent import Queue
from .remote.remote_adm import RemoteAdm
from .remote.adm_listener import AdmListener
from .kernel.adapter import Adapter, FileAdapter

# ----------------------------------------------------------
# Defines system component exceptions
# ----------------------------------------------------------

class SystemException(Exception):
    """ Base class for exceptions of system """
    pass

# --------------------------------------------------------
# Define Component
# --------------------------------------------------------

class Directory(object):
    """ Directory class """

    class __Directory:
        """ Directory singleton class """
        
        def __init__(self) -> None:
            """ Directory constructor """
            self.container_list = []
            self.agent_list = []
            self.gateway = None
            self.check_to_list = None
                    
        def add_container(self, container:str) -> None:
            """ Add container to container list
            @param container Container to add
            """
            self.container_list.append(container)

        def add_agent(self, agent:Agent) -> None:
            """ Add agent to agent list
            @param agent Agent to add
            """
            self.agent_list.append(agent)

        def get_containers(self) -> list:
            """ Get container list
            @return list Container list
            """
            return self.container_list

        def get_agents(self) -> list:
            """ Get agent list
            @return list Agent list
            """
            return self.agent_list
        
        def set_agent_list(self, agent_list: list) -> None:
            """ Set agent list
            @param agentList Agent list
            """
            self.agent_list = agent_list
            
        def get_agent(self, agent_id: str) -> Agent:
            """ Get agent by id
            @param agentID Agent ID
            @return Agent Agent
            """
            for agent in self.agent_list:
                if agent_id == agent['agent']:
                    return agent
            return None

        def reset_agent_list(self) -> None:
            """ Reset agent list """
            self.agent_list = []

        def remove_agent(self, agent: Agent) -> None:
            """ Remove agent from agent list """ 
            for ag in self.agent_list:
                if ag['agent'] == agent:
                    self.agent_list.remove(ag)

        def set_check_list(self, gateway:str, check_to_list:list) -> None:
            """ Set check list
            @param gateway Gateway
            @param checkToList Check list
            """
            self.gateway = gateway
            self.check_to_list = check_to_list
        
        def check_full(self, container_name:str) -> None:
            """ Check if container name is in check list
            @param containerName Container name
            """
            if self.check_to_list:
                if container_name in self.check_to_list:
                    self.check_to_list.remove(container_name)
                    if len(self.check_to_list) == 0:
                        self.gateway.put(None)
                else:
                    raise SystemException('Container name: "%s" does not match' % container_name)
                
    # --------------------------------------------------------
    # Singleton
    # --------------------------------------------------------

    # Singleton instance
    instance = None

    def __new__(cls) -> object:
        """ Create new instance """
        if not Directory.instance:
            Directory.instance = Directory.__Directory()
        return Directory.instance
    
    def __getattr__(self, name: str) -> object:
        """ Get attribute
        @param name Attribute name
        @return object Attribute
        """
        return getattr(self.instance, name)
    
    def __setattr__(self, name:str) -> object:
        """ Set attribute
        @param name Attribute name
        @return object Attribute
        """
        return setattr(self.instance, name)

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class Adm(object):
    """ Represents the agent container manager """

    class __Adm:
        """ Singleton design pattern """

        def __init__(self) -> None:
            """ Default constructor """
            self.val = None
            self.conf = None
            self.adapters = {}
            self.agents_table = {}
            self.container_list = []
            self.__db = None
            self.__client = None
            
        def __str__(self) -> str:
            """ To string """
            return repr(self) + self.val

        def connect_database(self) -> None:
            """Connects to mongo database"""
            database_server = 'localhost'
            database_port = 27017
            if 'database_server' in self.conf['persistence']:
                database_server = self.conf['persistence']['database_server']
            if 'database_port' in self.conf['persistence']:
                database_port = self.conf['persistence']['database_port']
            try:
                self.__client = MongoClient(database_server, database_port)
                self.__db = self.__client[self.conf['persistence']['database_name']]
                # Check if exist mas structure
                collist = self.__db.list_collection_names()
                if not "mas" in collist:
                    self.__db.create_collection("mas")
                    self.__db.create_collection("agents")
                    self.__db.create_collection("agenda")
                    self.__db.create_collection("work_memory")
            except:
                name = self.conf['persistence']['database_name']
                raise SystemException(f'[Error, connect_database]: Cannot connect to database: {name}')
                
        def start(self) -> None:
            """ Default administrator startup """
            self.conf = {
                "user" : "local",
                "host" : "localhost",
                "port" : 8080,
                "remote" : None     
            }
        
        def start_by_conf(self, conf:dict) -> None:            
            """
            Administrator startup by configuration.
            @param conf configuration dictionary or 
                   configuration file path
            @exceptions SystemException
            """
            if conf:
                # Sets local everoment from dictionary
                if not isinstance(conf, str):
                    if 'user' in conf and 'host' in conf and 'port' in conf:
                        if conf['user'] and conf['host'] and conf['port']:
                            self.conf = conf
                        else:
                            raise SystemException('[Warn, startByConf]: Configuration parameters cannot be null')        
                    if 'persistence' in conf:
                        if 'database_name' in conf['persistence'] and conf['persistence']['database_name']:
                            if 'user' in conf and 'host' in conf and 'port' in conf:
                                self.conf = conf
                            else:
                                self.conf = {
                                    "user" : "local",
                                    "host" : "localhost",
                                    "port" : 8080,
                                    "remote" : None,
                                    "persistence": conf['persistence']     
                                }
                            self.connect_database()
                        else:
                            raise SystemException('[Warn, startByConf]: Name of databes is requerried')                        
                else:
                    CONF_DIR = conf
                    fa = FileAdapter({'alias':'JsonAdapter', 'type': 'JSON', 'path': CONF_DIR})
                    fa.setup()
                    param = fa.request()
                    self.conf = param['conf']
                # Sets remote everoment
                if 'remote' in self.conf and self.conf['remote']:
                    remote = self.conf['remote']                
                    if remote['master_mode']:
                        self.remoteAdm = RemoteAdm(self.conf['host'], self.conf['port'])
                        self.remoteAdm.start()
                    else:
                        if 'container_name' in self.conf and 'master_host' in remote and 'master_port' in remote:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        
                            attempts = remote['attempts']
                            data = '{"command": "REGISTER", "name":"' + self.conf['container_name'] + '", "host":"' + self.conf['host'] + '", "port":"'+ str(self.conf['port']) +'"}'
                            received = None
                            for x in range(1, attempts):                        
                                try:
                                    sock.connect((remote['master_host'], remote['master_port']))                            
                                    sock.sendall(bytes(data + "\n", "utf-8"))
                                    received = str(sock.recv(1024), "utf-8")                                                           
                                    if received == 'ACK' + "\n":
                                        break
                                except:
                                    sleep(1)
                                finally:
                                    sock.close()
                            if received == 'ACK' + "\n":
                                admListener = AdmListener(self.conf['host'], self.conf['port'])
                                admListener.start()
                            else:
                                raise SystemException('[Warn, startByConf]: The administrator could not connect with the administrator master') 
                        else:
                            raise SystemException('[Warn, startByConf]: A parameter is missing. The parameters are: {container_name, master_host, master_port}')
            else:
                raise SystemException('[Warn, startByConf]: The parameter "conf" cannot be NoneType')

        def kill_agent(self, agent:Agent) -> None:
            """
            Remove an agent of the system.
            @param agent Agent to add
            @exceptions SystemException  
            """
            del self.agents_table[agent.id]
            directory = Directory()
            directory.remove_agent(agent.id)
            agent.kill()
            if self.conf['remote']:
                remote = self.conf['remote']
                agents = directory.get_agents()
                dto = '{"command":"UPDATE", "agents" : ' + json.dumps(agents, ensure_ascii=False) + '}'                
                if remote['mode'] == 'MASTER':
                    containers = directory.get_containers()                    
                    for ctn in containers:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        try:                            
                            sock.connect( (ctn['ip'], int(ctn['port'])) )                            
                            sock.sendall(bytes(dto + "\n", "utf-8"))
                        except:
                            raise SystemException('[Warn, killAgent]: Could not update container with IP %s' % ctn['ip'])                    
                        finally:
                            sock.close()
                else:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    master = remote['master']                                              
                    try:                            
                        sock.connect((master['master_ip'], master['master_port']))                            
                        sock.sendall(bytes(dto + "\n", "utf-8"))
                    except:
                        raise SystemException('[Warn, killAgent]: Could not update container master')
                    finally:
                        sock.close()
            agent = None
            gc.collect()

        def add_agent(self, agent:Agent) -> None:
            """
            Add an agent to the system.
            @param agent Agent to add
            @exceptions SystemException  
            """
            if agent.id in self.agents_table:
                raise SystemException('[Warn, addAgent]: Agent ID: "%s" already exists in container' % agent.id)
            else:
                # Register new agent to container
                self.agents_table[agent.id] = agent
                host = self.conf['host']
                port = self.conf['port']
                if 'remote' in self.conf and self.conf['remote']:
                    remote = self.conf['remote'] 
                directory = Directory()
                agentDTO = {'agent': agent.id, 'host': host, 'port' : port}
                directory.add_agent(agentDTO)
                if 'remote' in self.conf and self.conf['remote']:
                    remote = self.conf['remote']
                    if remote['master_mode']:
                        agents = directory.get_agents()
                        dto = '{"command":"UPDATE", "agents": ' + json.dumps(agents, ensure_ascii=False) + '}'
                        containers = directory.get_containers()                    
                        for ctn in containers:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            try:                            
                                sock.connect( (ctn['host'], int(ctn['port'])) )                            
                                sock.sendall(bytes(dto + "\n", "utf-8"))
                            except:
                                raise SystemException('[Warn, addAgent]: Could not update container with %s host' % ctn['host'])                    
                            finally:
                                sock.close()
                    else:
                        dto = '{"command":"ADD", "agent": ' + json.dumps(agentDTO, ensure_ascii=False) + '}'
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                             
                        try:                            
                            sock.connect((remote['master_host'], remote['master_port']))                            
                            sock.sendall(bytes(dto + "\n", "utf-8"))
                        except:
                            raise SystemException('[Warn, addAgent]: Could not update container master')
                        finally:
                            sock.close()
            # Persist agent information
            if 'persistence' in self.conf:
                agent_count = self.__db["agents"].count_documents({'agent_id': agent.id})
                if agent_count == 0:
                    # Create new agent document
                    self.__db["agents"].insert_one({'agent_id': agent.id})
                    self.__db.create_collection(agent.id)
                    # Create new agent state document
                    self.__db[agent.id].insert_one(agent.state)
                else:
                    # Get current state
                    state_list = self.__db[agent.id].find({})
                    agent.state = state_list[0]
                    
        def get_agent(self, agent_id:str) -> Agent:
            """ Get an agent from the system
            @param agentID Agent ID
            @return Agent Agent
            """
            return self.agents_table[agent_id]
                    
        def send_event(self, agent_id:str, event:any, data:any) -> bool:
            """
            Send an event to another agent.
            @param agentID Destination agent ID
            @param event Event to send
            @param data Event data
            @return :bool True if the submission was 
                    successful | False otherwise
            @exceptions SystemException
            """
            if agent_id in self.agents_table:
                ag = self.agents_table[agent_id]
                ag.send_event(event, data)
                return True
            else:
                if 'remote' in self.conf and self.conf['remote']:
                    remote = self.conf['remote'] 
                    attempts = remote['attempts']
                    agent = Directory().get_agent(agent_id)
                    received = None
                    if agent:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        aux = 'None'
                        if data:
                            data = json.dumps(data)
                            data = data.encode('utf-8')
                            data = base64.b64encode(data)
                            aux = data.decode('utf-8')                                                
                        dto = '{"command": "SENDEVENT", "id":"' + agent_id + '", "event":"' + event + '", "data":"'+ aux +'"}' 
                        for it in range(1, attempts):                        
                            try:
                                sock.connect((agent['host'], agent['port']))                            
                                sock.sendall(bytes(dto + "\n", "utf-8"))
                                received = str(sock.recv(1024), "utf-8")                                                            
                                if received == 'ACK' + "\n":
                                    break
                            except:
                                traceback.print_exc()
                                sleep(1)
                            finally:
                                sock.close()
                    if received == 'ACK' + "\n":
                        return True
                    else:
                        raise SystemException('[Warn, send_event]: The event could not be sent to the agent with the ID: %s ' % agent_id)                     
                else:
                    raise SystemException('[Warn, send_event]: An agent with the ID %s could not be found in the system' % agent_id)

        def add_adapter(self, id:str, adapter:Adapter) -> None:
            """ Add an adapter to the system
            @param id Adapter ID
            @param adapter Adapter to add
            """
            self.adapters[id] = adapter

        def get_adapter(self, id:str) -> Adapter:
            """ Get an adapter from the system
            @param id Adapter ID
            @return Adapter Adapter
            """
            return self.adapters[id]

        def get_conf(self) -> dict:
            """ Get configuration
            @return dict Configuration
            """
            return self.conf

        def add_container(self, container:str) -> None:
            """ Add a container to the system
            @param container Container to add
            """
            self.container_list.append(container)

        def move_agent(self, agent_id:str, container:str) -> None:
            """
            Add an agent to the system.
            @param agent Agent to add
            @exceptions SystemException  
            """
            ag = self.agents_table[agent_id]
            ag.finalize()
            dto = ag.toDTO()
            containers = Directory().get_containers()
            for ctn in containers:
                if container == ctn['name']:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:                            
                        sock.connect( (ctn['host'], int(ctn['port'])) )                            
                        sock.sendall(bytes(dto + "\n", "utf-8"))
                    except:
                        raise SystemException('[Error, moveAgent]: Could not update container with IP %s' % ctn['host'])
                    finally:
                        sock.close()
                    break    
            self.agents_table[agent_id] = None
            Directory().remove_agent(agent_id)

        def set_end_point(self, agent_id:str, socket:socket) -> None:
            """ Set the endpoint of an agent
            @param agentID Agent ID
            @param socket Socket
            """
            ag = self.agents_table[agent_id]
            ag.set_socket(socket)

        def call_agent(self, agent_id:str, data:any) -> any:
            """
            Call a social agent.
            @param data Call data
            """
            if agent_id in self.agents_table:
                ag = self.agents_table[agent_id]
                if ag.is_social():
                    if ag.is_block():
                        queue = Queue(1)
                        dto = {
                            'dto': data,
                            'gateway': queue
                        }
                        ag.send_event('delegate', dto)
                        result = queue.get()
                        queue.task_done()
                        return result
                    else:
                        raise SystemException('[Warn, callAgent]: The "callAgent" method is only for blocking controllers')
                else:
                    raise SystemException('[Warn, callAgent]: Only social agents can be invoked in this method')
            else:
                raise SystemException('[Warn, callAgent]: An agent with the ID %s could not be found in the system' % agent_id) 

        def submit_agent(self, agent_id:str, data:any) -> None:
            """
            Call a social agent.
            @param data Call data
            """
            if agent_id in self.agents_table:
                ag = self.agents_table[agent_id]
                if ag.is_social():
                    if not ag.is_block():
                        ag.send_event('delegate', data)
                    else:
                        raise SystemException('[Warn, submitAgent]: The "submitAgent" method is only for non-blocking controllers')
                else:
                    raise SystemException('[Warn, submitAgent]: Only social agents can be invoked in this method')
            else:
                raise SystemException('[Warn, submitAgent]: An agent with the ID %s could not be found in the system' % agent_id) 

        def wait_full(self, container_list) -> None:
            """ Wait for the container list to be full
            @param containerList Container list
            """
            gateway = Queue(1)
            Directory().set_check_list(gateway, container_list)
            gateway.get()
            gateway.task_done()

        def destroy(self) -> None:
            """ Destroy the administrator """
            for agent in self.agents_table:
                self.kill_agent(agent)
            self.val = None
            self.conf = None
            self.adapters = None
            self.agents_table = None
            self.container_list = None
            if self.__db:
                self.__client.close()
                self.__client = None
            self.__db = None
            gc.collect()

        def get_db_connection(self) -> MongoClient:
            """ Get database connection """
            return self.__db
    
    # ----------------------------------------------------
    # Defines singleton instance
    # ----------------------------------------------------

    # Singleton instance
    instance = None

    def __new__(cls) -> __Adm:
        """ Singleton design pattern """
        if not Adm.instance:
            Adm.instance = Adm.__Adm()
        return Adm.instance
    
    def __getattr__(self, name: str) -> any:
        """ Get attribute """
        return getattr(self.instance, name)
    
    def __setattr__(self, name: str) -> None:
        """ Set attribute """
        return setattr(self.instance, name)