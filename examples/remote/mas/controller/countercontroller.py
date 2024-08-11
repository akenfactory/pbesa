from .counterdelegate import CounterDelegate
from .counterresponse import CounterResponse
from pbesa.social.secuencial_team.secuencial_team import SecuencialController

class CounterController(SecuencialController):
    """ Through a class the concept of agent is defined """
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bind_delegate_action(CounterDelegate())
        # Assign an action to the behavior
        self.bind_response_action(CounterResponse())

    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass
