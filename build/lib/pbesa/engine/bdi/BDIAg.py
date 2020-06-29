from abc import ABC, abstractmethod
from ...kernel.util.Queue import Queue
from ...kernel.system.Adm import Adm
from .BDIMachine import BDIMachine 

class BDIAg(ABC):

    id = None    
    queue = None     
    world = None
    goals = None
    believes = None
    settings = None

    def __init__(self):
        self.settings = self.setUp()
        self.id = self.settings['id']		
        self.world = self.settings['world']
        self.goals = self.settings['goals']
        self.believes = self.settings['believes']
        Adm().addAgent(self)

        self.queue = Queue(10)
        self.machine = BDIMachine(self)

        self.world.setAgent(self)

        for goal in self.goals:
            for act in goal.plan:
                act.setAgent(self)

        super().__init__()

    def sendEvent(self, event, data):
        self.queue.put({'event': event, 'data': data})

    def start(self):
        self.machine.start()

    @abstractmethod
    def setUp(self):
        pass
