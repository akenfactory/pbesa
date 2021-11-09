import os
import sys
import json
import base64
import inspect
import socketserver
from time import sleep
from importlib.machinery import SourceFileLoader
from ...kernel.system.Directory import Directory

import types

class AdmListenerHandler(socketserver.StreamRequestHandler):

    def handle(self):
        self.data = self.rfile.readline().strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        msg = str(self.data, "utf-8")
        info = json.loads(msg)    
        if info['command'] == 'UPDATE':        
            agents = info['agents']
            directory = Directory()
            directory.setAgentList(agents)
        if info['command'] == 'MOVE':   
            appPath = os.path.abspath(os.path.dirname(sys.argv[0]))
            appPathSplit = appPath.split(os.sep)
            classPath = info['path']
            classPathSplit = classPath.split('.')
            path = appPathSplit[0]
            findFlag = False
            for x in range(1, len(appPathSplit) ):
                if appPathSplit[x] == classPathSplit[0]:
                    path = path + os.sep + appPathSplit[x]
                    for y in range(1, len(classPathSplit) ):
                        path = path + os.sep + classPathSplit[y]
                    break
                else:
                    path = path + os.sep + appPathSplit[x]            
            path = path + '.py'
            module = SourceFileLoader(info['class'], path).load_module()
            agType = getattr(module, info['class'])
            ag = agType(info['id'])
            ag.state = info['state']
            ag.start()
        if info['command'] == 'SENDEVENT':
            from ...kernel.system.Adm import Adm
            data = info['data']
            aux = None
            if data and not data == 'None':
                data = data.encode('utf-8')
                data = base64.b64decode(data)
                data = data.decode('utf-8')
                aux = json.loads(data) 
            Adm().sendEvent(info['id'], info['event'], aux)
            rsp = 'ACK'
            self.wfile.write(bytes(rsp + "\n", "utf-8"))
