class Channel():

    def __init__(self, queue):       
        self.queue = queue
        super().__init__()
    
    def sendEvent(self, num):
        self.queue.put(num)
