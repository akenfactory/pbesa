from abc import ABC, abstractmethod

class World(ABC):
	
	def __init__(self):
		self.agent = None
		super().__init__()
	
	@abstractmethod
	def update(self, event, data):
		pass

	def setAgent(self, agent):
		self.agent = agent
