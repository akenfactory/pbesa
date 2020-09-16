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
from abc import ABC, abstractmethod
from ...kernel.system.Adm import Adm

# --------------------------------------------------------
# Define component
# --------------------------------------------------------
class Action(ABC):
    """ Represents the reaction to the occurrence of an event """
    
    def __init__(self):
        self.id = None
        self.log = None
        self.adm = None
        self.agent = None      
        super().__init__()
        
    @abstractmethod
    def execute(self, data):
        pass

    @abstractmethod
    def catchException(self, exception):
        pass

    def setAgent(self, agent):
        self.adm = Adm()
        self.agent = agent
        self.log = agent.log
