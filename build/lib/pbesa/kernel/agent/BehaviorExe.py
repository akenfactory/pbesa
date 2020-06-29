from threading import Thread
import time
import random
import traceback

class BehaviorExe(Thread):

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
            if self.let:
                evt = self.queue.get()
                self.queue.task_done()
                try:
                    evt['action'].execute(evt['data'])
                except Exception as e:
                    print(e)
                    traceback.print_exc()                

    def setLet(self, val):
        self.let = val

    def setAlive(self, val):
        self.alive = val
