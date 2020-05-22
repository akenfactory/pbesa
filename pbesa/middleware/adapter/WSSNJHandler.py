import json
import socket
import socketserver
from time import sleep
#from ...kernel.system.Adm import Adm
from ...kernel.system.Directory import Directory

class WSSNJHandler(socketserver.BaseRequestHandler):

    def handle(self):
        try:
            while True:
                #data = self.rfile.readline().strip()
                data = self.request.recv(1024)
                print("[REQUEST]: {}".format(self.client_address[0]))
                print(data)
                msg = str(data, "utf-8")
                rqst = json.loads(msg)                
                dto = {'socket': self.request, 'request': rqst}
                Adm().sendEvent('front_controller', 'wsnj_delegate', dto)
        except Exception as inst:
            print('Controled ecxeption in WSSNJHandler: ')
            print(inst)
