from threading import Thread
import time
import random

class GoalExe(Thread):

    let = None
    pool = None
    alive = None
    goal = None
    planQueue = None

    def __init__(self, pool, planQueue):
        self.let = True
        self.pool = pool
        self.alive = True
        self.planQueue = planQueue
        super().__init__()

    def run(self):
        while self.alive:
            if self.let:
                goal = self.planQueue.get()
                self.planQueue.task_done()
                for action in goal.plan:
                    action.execute('')
                goal.execute = False    
                self.pool.put(self)                
            #time.sleep(random.random())
    
    def setLet(self, val):
        self.let = val

    def setAlive(self, val):
        self.alive = val

