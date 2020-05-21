from abc import ABC, abstractmethod

class RationalAg(ABC):

	id = None
	state = None     
	brain = None
	world = None
	exePool = None
	settings = None

	def __init__(self):
		self.settings = self.setUp()
		self.id = self.settings['id']
		self.state = self.settings['state']
		self.brain = self.settings['brain']
		self.world = self.settings['world']
		size = self.settings['pool_size']
		Adm().addAgent(self)
		self.exePool = Queue(size)        
		for x in range(1, size):
			self.exePool.put(ActionExe(self.exePool))
		super().__init__()

	@abstractmethod
	def setUp(self, settings):
		pass

	def sendEvent(self, event, data):
		self.world.update(event, data)
		actions = self.brain.derive(event, data)
		if actions:
			for action in actions:
				aExe = self.getFree()
				aExe.setAction()
				aExe.setData()
				aExe.start()

	def getFree(self):
		exeA = self.pool.get()
		self.pool.task_done()
		return exeA 

