# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 3.0.1
@date 27/07/20
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------
import time
import random
import traceback
from threading import Thread
from ...kernel.util.Queue import Queue
from ...kernel.agent.exceptions import ActionException

# --------------------------------------------------------
# Define component
# --------------------------------------------------------
class BehaviorExe(Thread):
    """ Behavior executor component """

    def __init__(self, queue):
        self.__let = False
        self.__alive = True
        self.__stopAgent = Queue(1)
        self.__queue = queue
        super().__init__()

    def run(self):
        while self.__alive:
            evt = self.__queue.get()
            if not self.__let:
                self.__stopAgent.get()
            try:
                if self.__alive:
                    evt['action'].execute(evt['data'])
            except Exception as e:
                traceback.print_exc()
                evt['action'].catchException(e)
                self.__let = False        
            self.__queue.task_done()
        
    def setLet(self, val):
        self.__let = val
       
    def notifyLet(self, val):
        self.__stopAgent.put(None)
        
    def setAlive(self, val):
        self.__alive = val

    def finalize(self):
        self.__let = False
        self.__queue.put(None)
        self.__stopAgent.put(None)
