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

from threading import Thread
from abc import ABC, abstractmethod
from .kernel.agent import Action, Queue

# --------------------------------------------------------
# Define Action component
# --------------------------------------------------------

class ActionExe(Thread):
    """ ActionExe class """

    # Attributes
    let = None
    # Methods
    pool = None
    # Attributes
    alive = None
    # Methods
    action = None

    def __init__(self, pool: Queue) -> None:
        """ Constructor
        :param pool: Queue
        """
        self.let = False
        self.pool = pool
        self.alive = True
        super().__init__()

    def run(self) -> None:
        """ Run method """
        while self.alive:
            if self.let:
                self.action.execute(self.data)
                self.pool.addExe(self)                
            
    def setLet(self, val:bool) -> None:
        """ Set let attribute
        :param val: bool
        """
        self.let = val

    def setAlive(self, val:bool) -> None:
        """ Set alive attribute
        :param val: bool
        """
        self.alive = val

    def setAction(self, action: Action) -> None:
        """ Set action attribute
        :param action: Action
        """
        self.action = action

    def setData(self, data:any) -> None:
        """ Set data attribute
        :param data: any
        """
        self.data = data

# --------------------------------------------------------
# Define Brain component
# --------------------------------------------------------

class Brain(ABC):
    """ Brain class """

    def __init__(self):
        """ Constructor """
        super().__init__()

    @abstractmethod
    def derive(self, event:any, data:any) -> list:
        """ Derive method
        :param event: any
        :param data: any
        :return list
		"""
        pass

# --------------------------------------------------------
# Define RationalAgent component
# --------------------------------------------------------

class RationalAgent(ABC):
    """ RationalAgent class """

	# ID of the agent
    id = None
    # State of the agent
    state = None
    # Brain of the agent
    brain = None
	# World of the agent
    world = None
    # Pool of the agent
    exePool = None
    # Settings of the agent
    settings = None

    def __init__(self):
        """ Constructor """
        self.settings = self.setup()
        self.id = self.settings['id']
        self.state = self.settings['state']
        self.brain = self.settings['brain']
        self.world = self.settings['world']
        size = self.settings['pool_size']
        from .mas import Adm
        Adm().addAgent(self)
        self.exePool = Queue(size)        
        for x in range(1, size):
            self.exePool.put(ActionExe(self.exePool))
        super().__init__()

    @abstractmethod
    def setup(self, settings:dict) -> dict:
        """ Setup method
        :param settings: dict
        :return dict
		"""
        pass

    def send_event(self, event:any, data:any) -> None:
        """ Send event method
        :param event: any
        :param data: any
        """
        self.world.update(event, data)
        actions = self.brain.derive(event, data)
        if actions:
            for action in actions:
                aExe = self.get_free()
                aExe.setAction()
                aExe.setData()
                aExe.start()

    def get_free(self):
        """ Get free method
        :return ActionExe
		"""
        exeA = self.pool.get()
        self.pool.task_done()
        return exeA