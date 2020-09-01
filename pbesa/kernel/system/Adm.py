# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 3.0.1
@date 27/07/20
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------
import os
import gc
import sys
import json
import socket
from time import sleep
from ...kernel.util.Queue import Queue
from ...kernel.system.Directory import Directory
from ...middleware.remote.RemoteAdm import RemoteAdm
from ...kernel.adapter.FileAdapter import FileAdapter
from ...kernel.system.exceptions import SystemException
from ...middleware.remote.AdmListener import AdmListener

# --------------------------------------------------------
# Define component
# --------------------------------------------------------
class Adm(object):
    """ Represents the agent container manager """

    class __Adm:
        """ Singleton design pattern """

        def __init__(self):
            """ Default constructor """
            self.val = None
            self.conf = None
            self.adapters = {}
            self.agentsTable = {}
            self.containerList = []
            
        def __str__(self):
            """ To string """
            return repr(self) + self.val

        def start(self):
            """ Default administrator startup """
            self.conf = {
                "user" : "local",
                "ip" : "localhost",
                "port" : 8080,
                "remote" : None     
            }

        def startByConf(self, conf):            
            """
            Administrator startup by configuration.
            @param conf configuration dictionary or 
                   configuration file path
            @exceptions SystemException
            """
            if conf:
                if not isinstance(conf, str):
                    if 'user' in conf and 'ip' in conf and 'port' in conf:
                        if conf['user'] and conf['ip'] and conf['port']:
                            self.conf = conf
                        else:
                            raise SystemException('[Warn, startByConf]: Configuration parameters cannot be null')        
                    else:
                        raise SystemException('[Warn, startByConf]: A parameter is missing. The parameters are: {user, ip, port, remote(optional)}')
                else:
                    CONF_DIR = conf
                    fa = FileAdapter({'alias':'JsonAdapter', 'type': 'JSON', 'path': CONF_DIR})
                    fa.setUp()
                    param = fa.request()
                    self.conf = param['conf']
                if self.conf['remote']:
                    remote = self.conf['remote']                
                    if remote['mode'] == 'MASTER':
                        self.remoteAdm = RemoteAdm(remote['ip'], remote['port'])
                        self.remoteAdm.start()    
                    else:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        
                        attempts = remote['attempts']
                        master = remote['master']
                        data = '{"command": "REGISTER", "alias":"' + remote['container_alias'] + '", "ip":"' + remote['ip'] + '", "port":"'+ str(remote['port']) +'"}'
                        received = None
                        for x in range(1, attempts):                        
                            try:                            
                                sock.connect((master['master_ip'], master['master_port']))                            
                                sock.sendall(bytes(data + "\n", "utf-8"))
                                received = str(sock.recv(1024), "utf-8")                                                           
                                if received == 'ACK' + "\n":
                                    break
                            except:
                                sleep(1)
                            finally:
                                sock.close()
                        if received == 'ACK' + "\n":
                            admListener = AdmListener(remote['ip'], remote['port'])
                            admListener.start()
                        else:
                            raise SystemException('[Warn, startByConf]: The administrator could not connect with the administrator master')            
            else:
                raise SystemException('[Warn, startByConf]: The parameter "conf" cannot be null')

        def killAgent(self, agent):
            """
            Remove an agent of the system.
            @param agent Agent to add
            @exceptions SystemException  
            """
            del self.agentsTable[agent.id]
            Directory().removeAgent(agent.id)
            agent.kill()
            if self.conf['remote']:
                remote = self.conf['remote']
                agents = directory.getAgents()
                dto = '{"command":"UPDATE", "agents" : ' + json.dumps(agents, ensure_ascii=False) + '}'                
                if remote['mode'] == 'MASTER':
                    containers = directory.getContainers()                    
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

        def addAgent(self, agent):
            """
            Add an agent to the system.
            @param agent Agent to add
            @exceptions SystemException  
            """
            if agent.id in self.agentsTable:
                raise SystemException('[Warn, addAgent]: Agent ID already exists in container')
            else:
                self.agentsTable[agent.id] = agent
                ip = self.conf['ip']
                port = self.conf['port']
                if self.conf['remote']:
                    remote = self.conf['remote'] 
                    ip = remote['ip']
                    port = remote['port']
                directory = Directory()
                directory.addAgent({'agent': agent.id, 'ip': ip, 'port' : port})
                if self.conf['remote']:
                    remote = self.conf['remote']
                    agents = directory.getAgents()
                    dto = '{"command":"UPDATE", "agents" : ' + json.dumps(agents, ensure_ascii=False) + '}'                
                    if remote['mode'] == 'MASTER':
                        containers = directory.getContainers()                    
                        for ctn in containers:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            try:                            
                                sock.connect( (ctn['ip'], int(ctn['port'])) )                            
                                sock.sendall(bytes(dto + "\n", "utf-8"))
                            except:
                                raise SystemException('[Warn, addAgent]: Could not update container with IP %s' % ctn['ip'])                    
                            finally:
                                sock.close()
                    else:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        master = remote['master']                                              
                        try:                            
                            sock.connect((master['master_ip'], master['master_port']))                            
                            sock.sendall(bytes(dto + "\n", "utf-8"))
                        except:
                            raise SystemException('[Warn, addAgent]: Could not update container master')
                        finally:
                            sock.close()
                
        def sendEvent(self, agentID, event, data):
            """
            Send an event to another agent.
            @param agentID Destination agent ID
            @param event Event to send
            @param data Event data
            @return :bool True if the submission was 
                    successful | False otherwise
            @exceptions SystemException
            """
            if agentID in self.agentsTable:
                ag = self.agentsTable[agentID]
                ag.sendEvent(event, data)
                return True
            else:
                if self.conf['remote']:
                    remote = self.conf['remote'] 
                    attempts = remote['attempts']
                    agents = Directory().getAgents()
                    for agent in agents:
                        if agentID == agent['agent']:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            aux = str(data)
                            aux = aux.replace("\'", "\"")                                                
                            dto = '{"command": "SENDEVENT", "alias":"' + agentID + '", "event":"' + event + '", "data":'+ aux +'}' 
                            for x in range(1, attempts):                        
                                try:                            
                                    sock.connect((agent['ip'], agent['port']))                            
                                    sock.sendall(bytes(dto + "\n", "utf-8"))
                                    received = str(sock.recv(1024), "utf-8")                                                            
                                    if received == 'ACK' + "\n":
                                        break
                                except:
                                    sleep(1)
                                finally:
                                    sock.close()
                    if received == 'ACK' + "\n":
                        return True
                    else:
                        raise SystemException('[Warn, sendEvent]: An agent with the ID %s could not be found in the system' % agentID)                     
                else:
                    raise SystemException('[Warn, sendEvent]: An agent with the ID %s could not be found in the system' % agentID)

        def addAdapter(self, id, adapter):
            self.adapters[id] = adapter

        def getAdapter(self, id):
            return self.adapters[id]

        def getConf(self):
            return self.conf

        def addContainer(self, container):
            self.containerList.append(container)

        def moveAgent(self, agentID, container):
            """
            Add an agent to the system.
            @param agent Agent to add
            @exceptions SystemException  
            """
            ag = self.agentsTable[agentID]
            ag.finalize()
            dto = ag.toDTO()
            print (dto)
            containers = Directory().getContainers()
            for ctn in containers:
                if container == ctn['alias']:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:                            
                        sock.connect( (ctn['ip'], int(ctn['port'])) )                            
                        sock.sendall(bytes(dto + "\n", "utf-8"))
                    except:
                        raise SystemException('[Error, moveAgent]: Could not update container with IP %s' % ctn['ip'])
                    finally:
                        sock.close()
                    break    
            self.agentsTable[agentID] = None
            Directory().removeAgent(agentID)

        def setEndPoint(self, agID, socket):
            ag = self.agentsTable[agID]
            ag.setSocket(socket)

        def callAgent(self, agentID, data):
            """
            Call a social agent.
            @param data Call data
            """
            if agentID in self.agentsTable:
                ag = self.agentsTable[agentID]
                if 'social' in ag.state:
                    queue = Queue(1)
                    dto = {
                        'dto': data,
                        'gateway': queue
                    }
                    ag.sendEvent('delegate', dto)
                    result = queue.get()
                    queue.task_done()
                    return result
                else:
                    raise SystemException('[Warn, callAgent]: Only social agents can be invoked in this method')
            else:
                raise SystemException('[Warn, sendEvent]: An agent with the ID %s could not be found in the system' % agentID) 

        def destroy(self):
            for agent in self.agentsTable:
                self.killAgent(agent)
            self.val = None
            self.conf = None
            self.adapters = None
            self.agentsTable = None
            self.containerList = None
            gc.collect()        
    
    # ----------------------------------------------------
    # Defines singleton instance
    # ----------------------------------------------------

    instance = None
    def __new__(cls):
        if not Adm.instance:
            Adm.instance = Adm.__Adm()
        return Adm.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)
