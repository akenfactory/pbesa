# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 09/08/24
"""

import traceback
import socketserver
from threading import Thread
from .exceptions import RemoteException
from .remote_adm_handler import RemoteAdmHandler

class RemoteAdm(Thread):
    """ RemoteAdm class """

    # IP
    __IP = None
    # PORT
    __PORT = None

    def __init__(self, ip:str, port:str) -> None:
        """ Constructor
        @param ip: IP
        @param port: PORT
        """
        self.__IP = ip
        self.__PORT = port
        super().__init__()

    def run(self) -> None:
        """ Run method """
        try:        
            server = socketserver.TCPServer((self.__IP, self.__PORT), RemoteAdmHandler)
            server.serve_forever()
        except:
            traceback.print_exc()
            raise RemoteException("Could not initialize master container on %s host and %d port" % (self.__IP, self.__PORT))
