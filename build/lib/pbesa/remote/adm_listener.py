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

import socketserver
from threading import Thread
from .adm_listener_handler import AdmListenerHandler

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class AdmListener(Thread):
    """ ADM Listener class """

    # IP
    IP = None
    # PORT
    PORT = None

    def __init__(self, ip:str, port:int) -> None:
        """ Constructor
        :param ip: IP
        :param port: PORT
        """
        self.IP = ip
        self.PORT = port
        super().__init__()

    def run(self) -> None:
        """ Run """        
        server = socketserver.TCPServer((self.IP, self.PORT), AdmListenerHandler)
        server.serve_forever()