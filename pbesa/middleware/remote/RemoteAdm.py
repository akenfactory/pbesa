import traceback
import socketserver
from threading import Thread
from .exceptions import RemoteException
from ...middleware.remote.RemoteAdmHandler import RemoteAdmHandler

class RemoteAdm(Thread):

    __IP = None
    __PORT = None

    def __init__(self, ip, port):
        self.__IP = ip
        self.__PORT = port
        super().__init__()

    def run(self):
        try:        
            server = socketserver.TCPServer((self.__IP, self.__PORT), RemoteAdmHandler)
            server.serve_forever()
        except:
            traceback.print_exc()
            raise RemoteException("Could not initialize master container on %s host and %d port" % (self.__IP, self.__PORT))
