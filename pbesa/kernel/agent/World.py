from abc import ABC, abstractmethod

class WorldTK(ABC):
	
	agent = None

	def __init__(self):
		super().__init__()
	
	@abstractmethod
	def update(self, event, data):
		pass

	def setAgent(self, agent):
		self.agent = agent
