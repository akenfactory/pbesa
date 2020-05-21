from abc import ABC, abstractmethod
from TokenForce.KernelTK.Util.Queue import Queue
from TokenForce.KernelTK.SystemTK.Adm import Adm
from TokenForce.MiddlewareTK.BDITK.BDIMachine import BDIMachine 

class BDIAgTK(ABC):

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
