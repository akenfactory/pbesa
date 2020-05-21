import socketserver
from threading import Thread
from ...middleware.remote.AdmListenerHandler import AdmListenerHandler

class AdmListener(Thread):

    IP = None
    PORT = None

    def __init__(self, ip, port):
        self.IP = ip
        self.PORT = port
        super().__init__()

    def run(self):        
        server = socketserver.TCPServer((self.IP, self.PORT), AdmListenerHandler)
        server.serve_forever()
