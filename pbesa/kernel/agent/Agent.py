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
import logging
from abc import ABC, abstractmethod
from ...kernel.system.Adm import Adm
from ...kernel.util.Queue import Queue
from ...kernel.agent.Channel import Channel
from ...kernel.agent.BehaviorExe import BehaviorExe
from ...kernel.agent.exceptions import AgentException

# --------------------------------------------------------
# Define component
# --------------------------------------------------------
class Agent(ABC):
    """ Represents a system agent """
    
    def __init__(self, agentID):
        """
        Agent constructor method.
        @param agentID Unic agent ID
        """
        if agentID and isinstance(agentID, str):    
            self.id = agentID
            self.state = {}
            self.__eventsTable = {}
            self.__channelsTable = {}
            self.__workerList = []
            self.__channelList = []
            self.__behaviors = {}
            self._social = False
            self.log = None
            self.__buildAgent()
            Adm().addAgent(self)
            super().__init__()
        else:
            raise AgentException('[Fatal, __init__]: The agent ID must be a str')
    
    def __buildAgent(self):
        """ Build the agent structure """
        self.setUp()
        if len(self.__behaviors) > 0: 
            for key, beh in self.__behaviors.items():            
                queue = Queue(100)
                channel = Channel(queue)    
                worker = BehaviorExe(queue)
                self.__channelsTable[key] = {'channel' : channel, 'worker': worker}  
                self.__workerList.append(worker)
                self.__channelList.append(channel)
                for evts in beh:
                    try:
                        evts['action'].setAgent(self)
                        self.__eventsTable[evts['event']] = {'behavior' : key, 'action': evts['action']}
                    except:
                        raise AgentException('[Fatal, buildAgent]: The action must be instantiated: %s' % str(evts['action']))            
        else:
            raise AgentException('[Fatal, buildAgent]: Agent behaviors must be defined')
     
    @abstractmethod
    def setUp(self):
        """ Method to create and initialize the agent structure """
        pass

    @abstractmethod
    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass

    def sendEvent(self, event, data):
        """
        Method that registers an event to the agent.
        @param event Envent
        @param Data event
        @exceptions AgentException
        """
        if event in self.__eventsTable:    
            behavior = self.__eventsTable[event]
            channel = self.__channelsTable[behavior['behavior']]
            evt = {'event': event, 'data': data, 'action': behavior['action']}              
            channel['channel'].sendEvent(evt)
        else:
            raise AgentException('[Warn, sendEvent]: The agent has not registered the event %s' % event)
    
    def start(self):
        for w in self.__workerList:
            w.setLet(True)
            w.start()
            
    def wait(self):
        for w in self.__workerList:
            w.setLet(False)

    def finalize(self):
        for w in self.__workerList:
            w.setAlive(False)
            w.finalize()
    
    def kill(self):
        """ Remove the agent from the system """
        if 'persistence' in Adm().conf:
            self.persist()
        self.shutdown()
        self.id = None
        self.log = None
        self.state = None
        self.__eventsTable = None
        self.__channelsTable = None
        self.finalize()
        self.__workerList = None
        self.__channelList = None
        self.__behaviors = None

    def toDTO(self):
        dto = {
            'command': 'MOVE',
            'class': self.__class__.__name__,
            'path': self.__module__,
            'id': self.id,
            'state': self.state  
        }
        rtn = str(dto)
        rtn = rtn.replace("'", "\"")  
        return rtn

    def addBehavior(self, behavior):
        """
        Add the new behavior to the agent's behavior.
        @param behavior New behavior
        """
        self.__behaviors[behavior] = []

    def bindAction(self, behavior, event, action):
        """
        Link behavior to event with action.
        @param behavior Behavior
        @param event Event link to behavior
        @param action Action link to event
        @exceptions AgentException
        """
        if behavior in self.__behaviors:
            self.__behaviors[behavior].append({
                'event': event, 
                'action': action
            })
        else:
            raise AgentException('[Fatal, bindAction]: The behavior "%s" is not associated with the agent. Must be added before behavior' % behavior)

    def setUpLogger(self, loggerName, loggerFile, level):
        """
        Inicia un componente de seguimiento de la aplicacion.
        @param loggerName nombre del log
        @param loggerFile ruta del archivo
        """
        l = logging.getLogger(loggerName)
        formatter = logging.Formatter('[PBESA]: %(asctime)s %(name)-12s %(lineno)d %(levelname)-8s %(message)s')
        fileHandler = logging.FileHandler(loggerFile, 'w', 'utf-8')
        fileHandler.setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        l.setLevel(level)
        l.addHandler(fileHandler)
        l.addHandler(streamHandler)

    def activeLogger(self, logger, level=logging.INFO):
        if not level:
            level = logging.INFO
        self.setUpLogger(logger, '%s.log' % logger, level)
        self.log = logging.getLogger(logger)
    
    def suscribeLogger(self, logger):
        self.log = logging.getLogger(logger)

    def persist(self):
        db = Adm().getDBConnection()
        db[self.id].delete_many({})
        db[self.id].insert_one(self.state)

    def isSocial(self):
        return self._social

