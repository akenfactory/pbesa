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
import base64
import socket
import traceback
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
                "host" : "localhost",
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
                    if 'user' in conf and 'host' in conf and 'port' in conf:
                        if conf['user'] and conf['host'] and conf['port']:
                            self.conf = conf
                        else:
                            raise SystemException('[Warn, startByConf]: Configuration parameters cannot be null')        
                    else:
                        raise SystemException('[Warn, startByConf]: A parameter is missing. The parameters are: {user, host, port, remote(optional)}')
                else:
                    CONF_DIR = conf
                    fa = FileAdapter({'alias':'JsonAdapter', 'type': 'JSON', 'path': CONF_DIR})
                    fa.setUp()
                    param = fa.request()
                    self.conf = param['conf']
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

        def killAgent(self, agent):
            """
            Remove an agent of the system.
            @param agent Agent to add
            @exceptions SystemException  
            """
            del self.agentsTable[agent.id]
            directory = Directory()
            directory.removeAgent(agent.id)
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
                raise SystemException('[Warn, addAgent]: Agent ID: "%s" already exists in container' % agent.id)
            else:
                self.agentsTable[agent.id] = agent
                host = self.conf['host']
                port = self.conf['port']
                if 'remote' in self.conf and self.conf['remote']:
                    remote = self.conf['remote'] 
                    #host = remote['host']
                    #port = remote['port']
                directory = Directory()
                agentDTO = {'agent': agent.id, 'host': host, 'port' : port}
                directory.addAgent(agentDTO)
                if 'remote' in self.conf and self.conf['remote']:
                    remote = self.conf['remote']
                    if remote['master_mode']:
                        agents = directory.getAgents()
                        dto = '{"command":"UPDATE", "agents": ' + json.dumps(agents, ensure_ascii=False) + '}'
                        containers = directory.getContainers()                    
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
                if 'remote' in self.conf and self.conf['remote']:
                    remote = self.conf['remote'] 
                    attempts = remote['attempts']
                    agent = Directory().getAgent(agentID)
                    received = None
                    if agent:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        aux = 'None'
                        if data:
                            data = json.dumps(data)
                            data = data.encode('utf-8')
                            data = base64.b64encode(data)
                            aux = data.decode('utf-8')                                                
                        dto = '{"command": "SENDEVENT", "id":"' + agentID + '", "event":"' + event + '", "data":"'+ aux +'"}' 
                        for it in range(1, attempts):                        
                            try:
                                print('attempt: %d' % it)                            
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
                        raise SystemException('[Warn, sendEvent]: The event could not be sent to the agent with the ID: %s ' % agentID)                     
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
                if ag.isSocial():
                    if ag.isBlock():
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
                        raise SystemException('[Warn, callAgent]: The "callAgent" method is only for blocking controllers')
                else:
                    raise SystemException('[Warn, callAgent]: Only social agents can be invoked in this method')
            else:
                raise SystemException('[Warn, callAgent]: An agent with the ID %s could not be found in the system' % agentID) 

        def submitAgent(self, agentID, data):
            """
            Call a social agent.
            @param data Call data
            """
            if agentID in self.agentsTable:
                ag = self.agentsTable[agentID]
                if ag.isSocial():
                    if not ag.isBlock():
                        ag.sendEvent('delegate', data)
                    else:
                        raise SystemException('[Warn, submitAgent]: The "submitAgent" method is only for non-blocking controllers')
                else:
                    raise SystemException('[Warn, submitAgent]: Only social agents can be invoked in this method')
            else:
                raise SystemException('[Warn, submitAgent]: An agent with the ID %s could not be found in the system' % agentID) 

        def waitFull(self, containerList):
            gateway = Queue(1)
            Directory().setCheckList(gateway, containerList)
            gateway.get()
            gateway.task_done()

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
