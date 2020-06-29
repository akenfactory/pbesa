from threading import Thread
#from ...kernel.system.Adm import Adm
from ...kernel.adapter.Adapter import Adapter
from ...middleware.adapter.WSSNJHandler import WSSNJHandler
from ...middleware.adapter.SubProcessAdapter import SubProcessAdapter
from ...kernel.io.TCPServer import TCPServer

import os
import sys
import json
#import socketserver

import threading

class WSSNJAdapter(Adapter, Thread):

    IP = None
    adm = None
    PORT = None
    server = None

    def __init__(self):
        self.adm = Adm()
        conf = self.adm.getConf()
        self.IP = conf['ip']
        self.PORT = conf['port']
        self.INTERNAL_PORT = conf['internal_port']
        super().__init__()

    def setUp(self):
        DIR = os.path.dirname(os.path.abspath(__file__)) 
        FILE = os.path.join(DIR,"WSSNJWrapper.js")
        spa = SubProcessAdapter("node", FILE, self.IP + '-' + str(self.PORT) + '-' + str(self.INTERNAL_PORT))
        spa.start()
        
    def response(self, response):
        pass
    
    def request(self):
        pass

    def finalize(self):
        self.server.shutdown()
        self.server.server_close()        

    def run(self):
        self.server = TCPServerTK((self.IP, self.INTERNAL_PORT), WSSNJHandlerTK)
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

