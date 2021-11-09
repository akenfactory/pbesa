from threading import Thread
import time
import random

class ActionExe(Thread):

    let = None
    pool = None
    alive = None
    action = None

    def __init__(self, pool):
        self.let = False
        self.pool = pool
        self.alive = True
        super().__init__()

    def run(self):
        while self.alive:
            if self.let:
                self.action.execute(self.data)
                self.pool.addExe(self)                
            #time.sleep(random.random())

    def setLet(self, val):
        self.let = val

    def setAlive(self, val):
        self.alive = val

    def setAction(self, action):
    	self.action = action

    def setData(self, data):
    	self.data = data