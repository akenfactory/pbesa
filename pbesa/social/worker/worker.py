
from .task import Task
from abc import abstractmethod
from ...kernel.agent.Agent import Agent

class Worker(Agent):

    def setUp(self):
        self.state = {
            'controller': None
        }
        self.addBehavior('Task')
        self.build()

    def bindTask(self, action):
        self.bindAction('Task', 'task', action)

    @abstractmethod
    def build(self):
        pass
