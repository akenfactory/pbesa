# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 4.0.0
@date 09/08/24
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import logging
import traceback
from threading import Thread
from abc import ABC, abstractmethod
from time import time as _time

try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading
from collections import deque
import heapq

# ----------------------------------------------------------
# Defines system component exceptions
# ----------------------------------------------------------
 
class AgentException(Exception):
    """ Base class for exceptions of agent """
    pass

class ActionException(Exception):
    """ Base class for exceptions of agent """
    pass

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

__all__ = ['Empty', 'Full', 'Queue', 'PriorityQueue', 'LifoQueue']

class Empty(Exception):
    "Exception raised by Queue.get(block=0)/get_nowait()."
    pass

class Full(Exception):
    "Exception raised by Queue.put(block=0)/put_nowait()."
    pass

class Queue:
    """Create a queue object with a given maximum size.
    If maxsize is <= 0, the queue size is infinite.
    """
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)
        # mutex must be held whenever the queue is mutating.  All methods
        # that acquire mutex must release it before returning.  mutex
        # is shared between the three conditions, so acquiring and
        # releasing the conditions also acquires and releases mutex.
        self.mutex = _threading.Lock()
        # Notify not_empty whenever an item is added to the queue; a
        # thread waiting to get is notified then.
        self.not_empty = _threading.Condition(self.mutex)
        # Notify not_full whenever an item is removed from the queue;
        # a thread waiting to put is notified then.
        self.not_full = _threading.Condition(self.mutex)
        # Notify all_tasks_done whenever the number of unfinished tasks
        # drops to zero; thread waiting to join() is notified to resume
        self.all_tasks_done = _threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def task_done(self):
        """Indicate that a formerly enqueued task is complete.
        Used by Queue consumer threads.  For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.
        If a join() is currently blocking, it will resume when all items
        have been processed (meaning that a task_done() call was received
        for every item that had been put() into the queue).
        Raises a ValueError if called more times than there were items
        placed in the queue.
        """
        self.all_tasks_done.acquire()
        try:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished
        finally:
            self.all_tasks_done.release()

    def join(self):
        """Blocks until all items in the Queue have been gotten and processed.
        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved and all work on it is complete.
        When the count of unfinished tasks drops to zero, join() unblocks.
        """
        self.all_tasks_done.acquire()
        try:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()
        finally:
            self.all_tasks_done.release()

    def qsize(self):
        """Return the approximate size of the queue (not reliable!)."""
        self.mutex.acquire()
        n = self._qsize()
        self.mutex.release()
        return n

    def empty(self):
        """Return True if the queue is empty, False otherwise (not reliable!)."""
        self.mutex.acquire()
        n = not self._qsize()
        self.mutex.release()
        return n

    def full(self):
        """Return True if the queue is full, False otherwise (not reliable!)."""
        self.mutex.acquire()
        n = 0 < self.maxsize == self._qsize()
        self.mutex.release()
        return n

    def put(self, item, block=True, timeout=None):
        """Put an item into the queue.
        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).
        """
        self.not_full.acquire()
        try:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() == self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() == self.maxsize:
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = _time() + timeout
                    while self._qsize() == self.maxsize:
                        remaining = endtime - _time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()
        finally:
            self.not_full.release()

    def put_nowait(self, item):
        """Put an item into the queue without blocking.
        Only enqueue the item if a free slot is immediately available.
        Otherwise raise the Full exception.
        """
        return self.put(item, False)

    def get(self, block=True, timeout=None):
        """Remove and return an item from the queue.
        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """
        self.not_empty.acquire()
        try:
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = _time() + timeout
                while not self._qsize():
                    remaining = endtime - _time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            return item
        finally:
            self.not_empty.release()

    def get_nowait(self):
        """Remove and return an item from the queue without blocking.
        Only get an item if one is immediately available. Otherwise
        raise the Empty exception.
        """
        return self.get(False)

    # Override these methods to implement other queue organizations
    # (e.g. stack or priority queue).
    # These will only be called with appropriate locks held

    # Initialize the queue representation
    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self, len=len):
        return len(self.queue)

    # Put a new item in the queue
    def _put(self, item):
        self.queue.append(item)

    # Get an item from the queue
    def _get(self):
        return self.queue.popleft()


class PriorityQueue(Queue):
    '''Variant of Queue that retrieves open entries in priority order (lowest first).
    Entries are typically tuples of the form:  (priority number, data).
    '''

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item, heappush=heapq.heappush):
        heappush(self.queue, item)

    def _get(self, heappop=heapq.heappop):
        return heappop(self.queue)


class LifoQueue(Queue):
    '''Variant of Queue that retrieves most recently added entries first.'''

    def _init(self, maxsize):
        self.queue = []

    def _qsize(self, len=len):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)

    def _get(self):
        return self.queue.pop()
    
# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class Channel():
    """ Channel class """

    def __init__(self, queue: Queue) -> None:
        """ Constructor
        :param queue: Queue
        """       
        self.queue = queue
        super().__init__()
    
    def send_event(self, event:any) -> None:
        """ Send event
        :param event: Event
        """
        self.queue.put(event)

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class BehaviorExe(Thread):
    """ Behavior executor component """

    def __init__(self, queue:Queue) -> None:
        """ Constructor
        @param queue: Queue
        """
        self.__let = False
        self.__alive = True
        self.__stop_agent = Queue(1)
        self.__queue = queue
        super().__init__()

    def run(self) -> None:
        """ Run """
        while self.__alive:
            evt = self.__queue.get()
            if not self.__let:
                self.__stop_agent.get()
            try:
                if self.__alive:
                    evt['action'].execute(evt['data'])
            except Exception as e:
                traceback.print_exc()
                self.__let = False        
            self.__queue.task_done()
        
    def set_let(self, val:bool) -> None:
        """ Set let
        @param val: Value
        """
        self.__let = val
       
    def notify_let(self) -> None:
        """ Notify let"""
        self.__stop_agent.put(None)
        
    def set_alive(self, val:bool) -> None:
        """ Set alive
        @param val: Value
        """
        self.__alive = val

    def finalize(self) -> None:
        """ Finalize """
        self.__let = False
        self.__queue.put(None)
        self.__stop_agent.put(None)

# --------------------------------------------------------
# Define Action component
# --------------------------------------------------------

class Action(ABC):
    """ Represents the reaction to the occurrence of an event """
    
    def __init__(self) -> None:
        """ Constructor """
        self.id = None
        self.log = None
        self.adm = None
        self.agent = None      
        super().__init__()
        
    @abstractmethod
    def execute(self, data:any) -> None:
        """ Execute
        @param data: Data
        """
        pass

    def set_agent(self, agent) -> None:
        """ Set agent
        @param agent: Agent
        """
        from ..mas import Adm
        self.adm = Adm()
        self.agent = agent
        self.log = agent.log

# --------------------------------------------------------
# Define Agent component
# --------------------------------------------------------

class Agent(ABC):
    """ Represents a basic agent """
    
    def __init__(self, agent_id:str) -> None:
        """
        Agent constructor method.
        @param agentID Unic agent ID
        """
        if agent_id and isinstance(agent_id, str):    
            self.id = agent_id
            self.state = {}
            self.__events_table = {}
            self.__channels_table = {}
            self.__worker_list = []
            self.__channel_list = []
            self.__behaviors = {}
            self._social = False
            self.log = None
            self.__build_agent()
            from ..mas import Adm
            Adm().add_agent(self)
            super().__init__()
        else:
            raise AgentException('[Fatal, __init__]: The agent ID must be a str')
    
    def __build_agent(self) -> None:
        """ Build the agent structure """
        self.setup()
        if len(self.__behaviors) > 0: 
            for key, beh in self.__behaviors.items():            
                queue = Queue(100)
                channel = Channel(queue)    
                worker = BehaviorExe(queue)
                self.__channels_table[key] = {'channel' : channel, 'worker': worker}  
                self.__worker_list.append(worker)
                self.__channel_list.append(channel)
                for evts in beh:
                    try:
                        evts['action'].set_agent(self)
                        self.__events_table[evts['event']] = {'behavior' : key, 'action': evts['action']}
                    except:
                        raise AgentException('[Fatal, buildAgent]: The action must be instantiated: %s' % str(evts['action']))            
        else:
            raise AgentException('[Fatal, buildAgent]: Agent behaviors must be defined')
     
    @abstractmethod
    def setup(self) -> None:
        """ Method to create and initialize the agent structure """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """ Method to free up the resources taken by the agent """
        pass

    def send_event(self, event:any, data:any) -> None:
        """
        Method that registers an event to the agent.
        @param event Envent
        @param Data event
        @exceptions AgentException
        """
        if event in self.__events_table:    
            behavior = self.__events_table[event]
            channel = self.__channels_table[behavior['behavior']]
            evt = {'event': event, 'data': data, 'action': behavior['action']}              
            channel['channel'].send_event(evt)
        else:
            raise AgentException('[Warn, send_event]: The agent has not registered the event %s' % event)
    
    def start(self) -> None:
        """ Start the agent """
        for w in self.__worker_list:
            w.set_let(True)
            w.start()
            
    def wait(self) -> None:
        """ Wait for the agent to finish """
        for w in self.__worker_list:
            w.set_let(False)

    def finalize(self) -> None:
        """ Finalize the agent """
        for w in self.__worker_list:
            w.set_alive(False)
            w.finalize()
    
    def kill(self) -> None:
        """ Remove the agent from the system """
        from ..mas import Adm
        if 'persistence' in Adm().conf:
            self.persist()
        self.shutdown()
        self.id = None
        self.log = None
        self.state = None
        self.__events_table = None
        self.__channels_table = None
        self.finalize()
        self.__worker_list = None
        self.__channel_list = None
        self.__behaviors = None

    def to_dto(self) -> str:
        """ Convert the agent to a DTO """
        dto = {
            'command': 'MOVE',
            'class': self.__class__.__name__,
            'path': self.__module__,
            'id': self.id,
            'state': self.state  
        }
        rtn = str(dto)
        rtn = rtn.replace("'", "\"")  
        return rtn

    def add_behavior(self, behavior:str) -> None:
        """
        Add the new behavior to the agent's behavior.
        @param behavior New behavior
        """
        self.__behaviors[behavior] = []

    def bind_action(self, behavior:str, event:any, action:Action) -> None:
        """
        Link behavior to event with action.
        @param behavior Behavior
        @param event Event link to behavior
        @param action Action link to event
        @exceptions AgentException
        """
        if behavior in self.__behaviors:
            self.__behaviors[behavior].append({
                'event': event, 
                'action': action
            })
        else:
            raise AgentException('[Fatal, bindAction]: The behavior "%s" is not associated with the agent. Must be added before behavior' % behavior)

    def set_up_logger(self, logger_name:str, logger_file:str, level:int) -> None:
        """
        Inicia un componente de seguimiento de la aplicacion.
        @param loggerName nombre del log
        @param loggerFile ruta del archivo
        """
        l = logging.getLogger(logger_name)
        formatter = logging.Formatter('[PBESA]: %(asctime)s %(name)-12s %(lineno)d %(levelname)-8s %(message)s')
        fileHandler = logging.FileHandler(logger_file, 'w', 'utf-8')
        fileHandler.setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        l.setLevel(level)
        l.addHandler(fileHandler)
        l.addHandler(streamHandler)

    def active_logger(self, logger:str, level:int=logging.INFO) -> None:
        """ Activa el log de la aplicacion """
        if not level:
            level = logging.INFO
        self.set_up_logger(logger, '%s.log' % logger, level)
        self.log = logging.getLogger(logger)
    
    def suscribe_logger(self, logger:str) -> None:
        """ Suscribe el log de la aplicacion
        @param logger Nombre del log
        """
        self.log = logging.getLogger(logger)

    def persist(self) -> None:
        """ Persist the agent state
        @exceptions AgentException
        """
        from ..mas import Adm
        db = Adm().get_db_connection()
        db[self.id].delete_many({})
        db[self.id].insert_one(self.state)

    def is_social(self) -> bool:
        """ Check if the agent is social
        @return bool
        """
        return self._social