from threading import Thread
from abc import ABC, abstractmethod
#from ...kernel.system.Adm import Adm
from ...kernel.adapter.Adapter import Adapter

import os
import random
import pygame
import math
import sys

class GameAdapter(Adapter, Thread):

    adm = None
    conf = None
    clock = None
    screen = None
    agentList = None

    def __init__(self, conf):        
        self.conf = conf
        self.agentList = []
        self.adm = None #Adm()
        super().__init__()

    def setUp(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        self.screen = pygame.display.set_mode((self.conf['width'], self.conf['height']))
        pygame.display.set_caption(self.conf['title'])
        self.clock = pygame.time.Clock()
        pygame.init()
        self.clock = pygame.time.Clock()

    def response(self):
        pass
    
    def request(self):
        return self.data

    def finalize(self):
        pass

    def addAgent(self, ag):
        self.agentList.append(ag)

    def run(self):
        running = True       
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.frame()
            pygame.display.update()
            self.clock.tick(40)

    def updateWorlds(self, event, data):
        for ag in self.agentList:
            self.adm.sendEvent(ag.id, event, data)

    def getPygame(self):
        return pygame

    def frame(self):
        pass