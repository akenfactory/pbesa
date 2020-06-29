from abc import ABC, abstractmethod

class Adapter(ABC):
    
    data = None
    config = None
    
    def __init__(self):
        #Adm().addAdapter(self)
        super().__init__()

    @abstractmethod
    def setUp(self):
        pass

    @abstractmethod
    def response(self):
        pass
    
    @abstractmethod
    def request(self):
        pass

    @abstractmethod
    def finalize(self):
        pass
