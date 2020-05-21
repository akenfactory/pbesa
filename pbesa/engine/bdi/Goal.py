from abc import ABC, abstractmethod

class Goal(ABC):

    id = None
    plan = None
    execute = None
    priority = None
    settings = None
    
    def __init__(self):
        self.execute = False
        self.settings = self.setUp()
        self.id = self.settings['id']
        self.plan = self.settings['plan']
        self.priority = self.settings['priority']
        super().__init__()

    @abstractmethod
    def setUp(self):
        pass

    @abstractmethod
    def eval(self, believes):
        pass



