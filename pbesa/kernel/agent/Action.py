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

    id = None
    log = None
    adm = None
    agent = None
    state = None
        
    def __init__(self):        
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
        self.state = agent.state
