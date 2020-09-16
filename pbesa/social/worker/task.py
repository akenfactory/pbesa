from abc import abstractmethod
from ...kernel.agent.Action import Action
from ...social.worker.exceptions import TaskException

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class Task(Action):
    """ An action is a response to the occurrence of an event """

    def __init__(self):
        self.__isPool = False
        self.__enableResponse = False
        super().__init__()

    def execute(self, data):
        """ 
        Response.
        @param data Event data 
        """
        self.goHead(data)

        if self.__isPool:
            self.adm.sendEvent(self.agent.getController(), 'notify', self.agent.id)

    def activeTimeout(self, time):       
        self.adm.sendEvent(self.agent.id, 'timeout', {'time': time, 'dto': None})

    def sendResponse(self, data):
        if self.__enableResponse:
            response = {
                'source': self.agent.id,
                'result': data
            }
            self.adm.sendEvent(self.agent.getController(), 'response', response) 
        else:
            raise TaskException('[Warn, sendResponse]: The type of control does not allow synchronous responses (see Linear or Pool type Block)')
    
    @abstractmethod
    def goHead(self, data):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

    def setIsPool(self, isPool):
        self.__isPool = isPool
    
    def setEnableResponse(self, enableResponse):
        self.__enableResponse = enableResponse
