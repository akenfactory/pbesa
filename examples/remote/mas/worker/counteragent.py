from .countertask import CounterTask
from pbesa.social.worker.worker import Worker

class CounterAgent(Worker):
    """ Through a class the concept of agent is defined """
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bindTask(CounterTask())
        
    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass
