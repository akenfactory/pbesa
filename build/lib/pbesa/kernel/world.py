# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 08/08/24
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

from .agent import Agent
from abc import ABC, abstractmethod

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class World(ABC):
	""" World class """
	
	def __init__(self) -> None:
		""" Constructor """
		self.agent = None
		super().__init__()
	
	@abstractmethod
	def update(self, event, data) -> None:
		""" Update world
		:param event: Event
		:param data: Data
		"""
		pass

	def set_agent(self, agent:Agent) -> None:
		""" Set agent
		:param agent: Agent
		"""
		self.agent = agent