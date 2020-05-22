from abc import ABC, abstractmethod
from ...kernel.system.Adm import Adm

class Action(ABC):
    
    id = None
    adm = None
    agent = None
    
    def __init__(self):        
        super().__init__()
        
    @abstractmethod
    def execute(self, data):
        pass

    def setAgent(self, agent):
    	self.adm = Adm()
    	self.agent = agent
