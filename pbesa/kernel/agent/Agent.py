from abc import ABC, abstractmethod
from pbesa.kernel.util.Queue import Queue
from pbesa.kernel.system.Adm import Adm
from pbesa.kernel.agent.Channel import Channel
from pbesa.kernel.util.HashTable import HashTable
from pbesa.kernel.agent.BehaviorExe import BehaviorExe

class Agent(ABC):
    
    id = None
    state = None
    settings = None    
    behaviors = None
    channelsTable = None
    behaviorsTable = None
    workerList = None
    channelList = None
            
    def __init__(self, arg):

        self.settings = self.setUp(arg)
        self.id = self.settings['id']
        self.state = self.settings['state']
        Adm().addAgent(self)

        self.eventsTable = HashTable()
        self.channelsTable = HashTable()

        self.workerList = []
        self.channelList = []

        self.behaviors = self.settings['behaviors']
        
        for beh in self.behaviors:            
            queue = Queue(10)
            channel = Channel(queue)    
            worker = BehaviorExe(queue)
            
            self.channelsTable[beh['name']] = {'channel' : channel, 'worker': worker}  

            self.workerList.append(worker)
            self.channelList.append(channel)

            events = beh['events']
            for evts in events:
                evts['action'].setAgent(self)
                self.eventsTable[evts['performative']] = {'behavior' : beh['name'], 'action': evts['action']} 

        super().__init__()
        
    @abstractmethod
    def setUp(self, settings):
        pass
    
    def sendEvent(self, event, data):
        behavior = self.eventsTable[event]
        channel = self.channelsTable[behavior['behavior']]
        evt = {'event': event, 'data': data, 'action': behavior['action']}              
        channel['channel'].sendEvent(evt)
    
    def start(self):
        for w in self.workerList:
            w.setLet(True)
            w.start()
            
    def wait(self):
        for w in self.workerList:
            w.setLet(False)

    def finalize(self):
        for w in self.workerList:
            w.setAlive(False)
    
    def kill(self):
        # TODO Call garbachcollector
        pass

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

    def getState(self):
        return self.state
