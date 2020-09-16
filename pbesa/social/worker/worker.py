from .task import Task
from abc import abstractmethod
from .exceptions import WorkerException
from ...kernel.agent.Agent import Agent
from .timeoutaction import TimeoutAction

class Worker(Agent):

    def __init__(self, agentID):
        self.__taskList = []
        self.__controller = None
        self.__controllerType = None    
        super().__init__(agentID)

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

    def suscribeRemoteController(self, controllerID):
        self.setController(controllerID)
        self.setControllerType('LINEAL')
        actions = self.getActions()
        for action in actions:
            action.setIsPool(False)
            action.setEnableResponse(True)

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
