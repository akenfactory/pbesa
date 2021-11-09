from enum import Enum 

class PeriodicState(Enum):
    START = 1
    STOP = 2
    PROCESS = 3

class SPPeriodicData():
    command = None
    def __init__(self, command = PeriodicState.START, time = 60):
        self.command = command
        self.time = time
