from ...kernel.adapter.Adapter import Adapter
from ...kernel.io.SystemFile import SystemFile

class FileAdapter(Adapter):

    def __init__(self, config):
        self.config = config
        super().__init__()

    def setUp(self):
        if self.config['type'] == 'JSON':            
            sf = SystemFile(self.config['path'])
            self.data = sf.readJsonFile()

    def response(self):
        pass
    
    def request(self):
        return self.data

    def finalize(self):
        pass

