from subprocess import call
from threading import Thread
from ...kernel.adapter.Adapter import Adapter

class SubProcessAdapter(Adapter, Thread):

    app = None
    file = None    
    args = None

    def __init__(self, app, file, args):
        self.app = app
        self.file = file
        self.args = args
        super().__init__()

    def run(self):
        call([self.app, self.file, self.args])

    def setUp(self):
        pass
        
    def response(self, response):
        pass
    
    def request(self):
        pass

    def finalize(self):
        pass