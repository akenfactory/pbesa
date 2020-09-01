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
from ...kernel.agent.exceptions import ActionException

# --------------------------------------------------------
# Define component
# --------------------------------------------------------
class BehaviorExe(Thread):
    """ Behavior executor component """

    let = None
    alive = None
    queue = None

    def __init__(self, queue):
        self.let = False
        self.alive = True
        self.queue = queue
        super().__init__()

    def run(self):
        while self.alive:
            evt = self.queue.get()
            if self.let:
                self.queue.task_done()
                try:
                    evt['action'].execute(evt['data'])
                except Exception as e:
                    evt['action'].catchException(e)
            else:
                time.sleep(1)                

    def setLet(self, val):
        self.let = val

    def setAlive(self, val):
        self.alive = val

    def finalize(self):
        self.let = False
        self.queue.put(None)
