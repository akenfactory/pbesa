
class WebAgTK():
    
    socket = None 

    def response(self, data):
        data = str(data)
        data = data.replace("'", "\"") + '\n'
        self.socket.sendall(data.encode()) 
        
    def setSocket(self, socket):
        self.socket = socket

    def updateID(self, id):
        pass
