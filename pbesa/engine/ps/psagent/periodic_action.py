from threading import Timer
from abc import abstractmethod
from ....kernel.agent.Action import Action
from .sp_periodic_data import PeriodicState, SPPeriodicData

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class PeriodicAction(Action):

    def __init__(self):
        self.__timer = None
        super().__init__()
    
    @abstractmethod
    def periodic_execute(self):
        pass

    def handler(self):
        """ Timeout handler """
        self.periodic_execute()
        self.adm.sendEvent(self.agent.id, 'periodic', SPPeriodicData(PeriodicState.PROCESS))

    def execute(self, data):
        """
        @param data
        """
        if isinstance(data, SPPeriodicData):
            if data.command == PeriodicState.START:
                self.agent.state['alive'] = True
                self.agent.state['time'] = data.time
                self.__timer = Timer(data.time, self.handler)
                self.__timer.start()
            elif data.command == PeriodicState.STOP:
                self.agent.state['alive'] = False
                if self.__timer:
                    self.__timer.cancel()
                    self.__timer = None
            elif data.command == PeriodicState.PROCESS:
                if self.agent.state['alive']:
                    self.__timer = Timer(self.agent.state['time'], self.handler)
                    self.__timer.start()
