# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 08/08/24
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import os
import json
import base64
import socket
import socketserver
from time import sleep
from importlib.machinery import SourceFileLoader

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class RemoteAdmHandler(socketserver.StreamRequestHandler):
    """ Remote ADM Handler class """

    def handle(self):
        """ Handle """
        from ..mas import Directory
        self.data = self.rfile.readline().strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        msg = str(self.data, "utf-8")
        info = json.loads(msg)
        if info['command'] == 'REGISTER':
            directory = Directory()
            directory.add_container({'name': info['name'], 'host': info['host'], 'port': info['port']})
            data = 'ACK'
            self.wfile.write(bytes(data + "\n", "utf-8"))
            sleep(2) # 2 seconds.
            containers = directory.get_containers()
            agents = directory.get_agents()
            dto = '{"command":"UPDATE", "agents" : ' + json.dumps(agents, ensure_ascii=False) + '}'
            for ctn in containers:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:                            
                    sock.connect( (ctn['host'], int(ctn['port'])) )                            
                    sock.sendall(bytes(dto + "\n", "utf-8"))
                except:
                    pass
                    
                finally:
                    sock.close()
            directory.check_full(info['name'])
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
        if info['command'] == 'ADD':
            agent = info['agent']
            host = agent['host']
            directory = Directory()
            directory.add_agent(agent)    
            containers = directory.get_containers()
            agents = directory.get_agents()
            dto = '{"command":"UPDATE", "agents" : ' + json.dumps(agents, ensure_ascii=False) + '}'
            for ctn in containers:
                if not ctn['host'] == host:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:                            
                        sock.connect( (ctn['host'], int(ctn['port'])) )                            
                        sock.sendall(bytes(dto + "\n", "utf-8"))
                    except:
                        pass
                    finally:
                        sock.close()        
        if info['command'] == 'SENDEVENT':
            from ..mas import Adm
            data = info['data']
            aux = None
            if data and not data == 'None':
                data = data.encode('utf-8')
                data = base64.b64decode(data)
                data = data.decode('utf-8')
                aux = json.loads(data)
            Adm().send_event(info['id'], info['event'], data)
            rsp = 'ACK'
            self.wfile.write(bytes(rsp + "\n", "utf-8"))
