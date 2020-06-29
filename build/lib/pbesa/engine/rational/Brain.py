from abc import ABC, abstractmethod

class Brain(ABC):

	def __init__(self):
		super().__init__()

	@abstractmethod
	def derive(self, event, data):
		pass
