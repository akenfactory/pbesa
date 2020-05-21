# -*- coding: utf-8 -*-
import os
import sys
import json
import socket
from time import sleep
from ...kernel.util.Log import Log
from ...kernel.util.HashTable import HashTable
from ...kernel.system.Directory import Directory
from ...kernel.adapter.FileAdapter import FileAdapter
from ...middleware.remote.RemoteAdm import RemoteAdm
from ...middleware.remote.AdmListener import AdmListener

class Adm(object):
    class __Adm:
        def __init__(self):
            self.val = None
            self.conf = None
            self.adapters = HashTable()
            self.agentsTable = HashTable()
            self.containerList = []
            
        def __str__(self):
            return repr(self) + self.val

        def start(self):
            self.startByConf('')

        def startByConf(self, conf):            
            log = Log()

            if conf == '':
                CONF_DIR = os.path.dirname(os.path.abspath(__file__))             
                CONF_DIR = os.path.join(CONF_DIR.replace("system", ""), "res", "conf.json")
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
                    for x in range(1, attempts):                        
                        try:                            
                            sock.connect((master['master_ip'], master['master_port']))                            
                            sock.sendall(bytes(data + "\n", "utf-8"))
                            received = str(sock.recv(1024), "utf-8")
                            print("Received: {}".format(received))                                                            
                            if received == 'ACK' + "\n":
                                break
                        except:
                            log.warn('The container could not connect to the master. Attempt:' + str(x))
                            sleep(1) # 1 second.
                        finally:
                            sock.close()

                    admListener = AdmListener(remote['ip'], remote['port'])
                    admListener.start()
            
        def addAgent(self, agent):
            self.agentsTable[agent.id] = agent
            ip = ''
            port = ''
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
                            log.warn('The container could not connect to container:' + ctn['alias'])
                        finally:
                            sock.close()
                else:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                        
                    attempts = remote['attempts']
                    master = remote['master']                                              
                    try:                            
                        sock.connect((master['master_ip'], master['master_port']))                            
                        sock.sendall(bytes(dto + "\n", "utf-8"))
                    except:
                        log.warn('The container could not connect to the master.')
                        sleep(1) # 1 second.
                    finally:
                        sock.close()
            
        def sendEvent(self, agentID, event, data):
            try:
                ag = self.agentsTable[agentID]
                if (ag):
                    ag.sendEvent(event, data)
                    return True
                else:
                    log = Log()
                    remote = self.conf['remote'] 
                    attempts = remote['attempts']
                    agents = Directory().getAgents()
                    for agent in agents:
                        if agentID == agent['agent']:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            aux = str(data)
                            aux = aux.replace("\'", "\"")                                                
                            dto = '{"command": "SENDEVENT", "alias":"' + agentID + '", "event":"' + event + '", "data":'+ aux +'}'
                            print('Send::')
                            print(dto)                               
                            for x in range(1, attempts):                        
                                try:                            
                                    sock.connect((agent['ip'], agent['port']))                            
                                    sock.sendall(bytes(dto + "\n", "utf-8"))
                                    received = str(sock.recv(1024), "utf-8")
                                    print("Received: {}".format(received))                                                            
                                    if received == 'ACK' + "\n":
                                        break
                                except:
                                    log.warn('The container could not connect to the master. Attempt:' + str(x))
                                    sleep(1) # 1 second.
                                finally:
                                    sock.close()
                    return True

            except Exception as inst:
                print('Controled ecxeption in Adm: ')
                print(inst)
                return False

        def addAdapter(self, id, adapter):
            self.adapters[id] = adapter

        def getAdapter(self, id):
            return self.adapters[id]

        def getConf(self):
            return self.conf

        def addContainer(self, container):
            self.containerList.append(container)

        def moveAgent(self, agentID, container):
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
                        Log().warn('The container could not connect to container: ' + ctn['alias'])
                    finally:
                        sock.close()
                    break    
            self.agentsTable[agentID] = None
            Directory().removeAgent(agentID)

        def setEndPoint(self, agID, socket):
            ag = self.agentsTable[agID]
            ag.setSocket(socket)
        
    instance = None
    def __new__(cls):
        if not Adm.instance:
            Adm.instance = Adm.__Adm()
        return Adm.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)
