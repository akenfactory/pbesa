# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 3.0.1
@date 11/09/21
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

from ..kernel.agent.Agent import Agent

# --------------------------------------------------------
# Define component
# --------------------------------------------------------
class SpiderAgent(Agent):
    """ Represents a system crawl agent """
    
    def __init__(self, agentID):
        self.class_element = None
        super().__init__(agentID)

    def setSpiderClass(self, class_element):
        """Set the crawl class"""
        self.class_element = class_element
