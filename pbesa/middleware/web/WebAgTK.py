from pbesa.kernel.util.Log import Log

class WebAgTK():
    
    socket = None 

    def response(self, data):
        data = str(data)
        data = data.replace("'", "\"") + '\n'
        self.socket.sendall(data.encode()) 
        Log().info('[WS-RESPONSE]: ' + data + '.')

    def setSocket(self, socket):
        self.socket = socket

    def updateID(self, id):
        pass
