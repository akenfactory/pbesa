from .counterdelegate import CounterDelegate
from .counterresponse import CounterResponse
from pbesa.social.linealcontroller.linealcontroller import LinealController

class CounterController(LinealController):
    """ Through a class the concept of agent is defined """
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bindDelegateAction(CounterDelegate())
        # Assign an action to the behavior
        self.bindResponseAction(CounterResponse())

    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass
