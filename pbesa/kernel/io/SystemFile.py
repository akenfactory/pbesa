import json

class SystemFile(object):
    
    path = None

    def __init__(self, path):
        self.path = path
    
    def readJsonFile(self):
        with open(self.path) as f:
            data = json.load(f)
        return data
