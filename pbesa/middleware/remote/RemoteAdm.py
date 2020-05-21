import socketserver
from threading import Thread
from pbesa.middleware.remote.RemoteAdmHandler import RemoteAdmHandler

class RemoteAdm(Thread):

    IP = None
    PORT = None

    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        super().__init__()

    def run(self):        
        server = socketserver.TCPServer((self.IP, self.PORT), RemoteAdmHandler)
        server.serve_forever()                
