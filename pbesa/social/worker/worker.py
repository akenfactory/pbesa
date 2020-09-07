from .task import Task
from abc import abstractmethod
from .exceptions import WorkerException
from ...kernel.agent.Agent import Agent
from .timeoutaction import TimeoutAction

class Worker(Agent):

    __taskList = []
    __controller = None
    __controllerType = None

    def setUp(self):
        self.addBehavior('Task')
        self.addBehavior('Timeout')
        self.bindAction('Timeout', 'timeout', TimeoutAction())
        self.build()

    def bindTask(self, action):
        if isinstance(action, Task):
            self.__taskList.append(action)    
            self.bindAction('Task', 'task', action)
        else:
            raise WorkerException('[Warn, bindTask]: The action must inherit from the task type')

    @abstractmethod
    def build(self):
        pass

    def getActions(self):
        return self.__taskList

    def getController(self):
        return self.__controller

    def setController(self, controller):
        self.__controller = controller

    def setControllerType(self, controllerType):
        self.__controllerType = controllerType
