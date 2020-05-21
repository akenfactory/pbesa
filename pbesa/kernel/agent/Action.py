from abc import ABC, abstractmethod
from pbesa.kernel.system.Adm import Adm
import logging

class Action(ABC):
    
    id = None
    adm = None
    agent = None
    log = None
    
    def __init__(self):        
        super().__init__()
        
    @abstractmethod
    def execute(self, data):
        pass

    def setAgent(self, agent):
    	self.adm = Adm()
    	self.agent = agent

    def setupLogger(self, name, log_file, logg):
        level = None
        if logg == 'debug': 
            level = logging.DEBUG
        if logg == 'info': 
            level = logging.INFO,
        if logg == 'warning': 
            level = logging.WARNING,
        if logg == 'error': 
            level = logging.ERROR,
        if logg == 'critical': 
            level = logging.CRITICAL
        self.log = logging.getLogger(name)
        if not self.log:        
            formatter = logging.Formatter('%(asctime)s %(name)-12s %(lineno)d %(levelname)-8s %(message)s')
            handler = logging.FileHandler(log_file)        
            handler.setFormatter(formatter)
            self.log = logging.getLogger(name)
            self.log.setLevel(level)
            self.log.addHandler(handler)
    
    def setupLocalLogger(self):
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(lineno)d %(levelname)-8s %(message)s')
        handler = logging.FileHandler('agents.log')        
        handler.setFormatter(formatter)
        self.log = logging.getLogger('agents')
        self.log.setLevel(logging.INFO)
        self.log.addHandler(handler)
