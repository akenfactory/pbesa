from threading import Thread
from ...kernel.util.Queue import Queue
from .GoalExe import GoalExe
from .BDILevel import BDILevel

import time
import random

class BDIMachine(Thread):

    let = None
    alive = None
    agent = None
    queue = None
    planQueue = None

    executeList = None

    machine = None
    physiologyList = None
    safetyList = None
    socialList = None
    esteemList = None
    selfrealizationList = None

    def __init__(self, agent):
        self.let = True
        self.alive = True
        self.agent = agent
        self.queue = agent.queue

        self.executeList = []

        self.physiologyList = []
        self.safetyList = []
        self.socialList = []
        self.esteemList = []
        self.selfrealizationList = []

        goals = agent.settings['goals']
        for goa in goals:
            if goa.priority == BDILevel.PHYSIOLOGY:
                self.physiologyList.append(goa)
            if goa.priority == BDILevel.SAFETY:
                self.safetyList.append(goa)
            if goa.priority == BDILevel.SOCIAL:
                self.socialList.append(goa)
            if goa.priority == BDILevel.ESTEEM:
                self.esteemList.append(goa)
            if goa.priority == BDILevel.SELF_REALIZATION:
                self.selfrealizationList.append(goa)

        self.pool = Queue(10)
        self.planQueue = Queue(10)

        for x in range(1,5):
            ge = GoalExe(self.pool, self.planQueue)
            ge.start()
            self.pool.put(ge)

        super().__init__()

    def run(self):        
        while self.alive:
            if self.let:
                evt = self.queue.get()
                self.queue.task_done()

                # Update World
                self.agent.world.update(evt['event'], evt['data']) 

                # Run Machine                                
                if self.checkFire(self.physiologyList):
                    self.executeGoals()
                else:
                    if self.checkFire(self.safetyList):
                        self.executeGoals()
                    else:
                        if self.checkFire(self.socialList):
                            self.executeGoals()
                        else:
                            if self.checkFire(self.esteemList):
                                self.executeGoals()
                            else:
                                if self.checkFire(self.selfrealizationList):
                                    self.executeGoals()


    def executeGoals(self):
        for goal in self.executeList:
            if not goal.execute:
                self.pool.get()
                self.pool.task_done()
                goal.execute = True
                self.executeList.remove(goal)
                self.planQueue.put(goal)                
                
    def contains(self, goal, lst):
        for go in lst:
            if go.id == goal.id:
                return True
        return False

    def checkFire(self, lst):
        for goa in lst:
            if not goa.execute and goa.eval(self.agent.believes):
                if not self.contains(goa, self.executeList):
                    self.executeList.append(goa)
        return ( len(self.executeList) > 0 )

    def setLet(self, val):
        self.let = val

    def setAlive(self, val):
        self.alive = val

