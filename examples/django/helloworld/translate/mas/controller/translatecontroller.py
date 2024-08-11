from .translatedelegate import TranslateDelegate
from .translateresponse import TranslateResponse
from pbesa.social.secuencial_team.secuencial_team import SecuencialController

class TranslateController(SecuencialController):
    """ Through a class the concept of agent is defined """
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bind_delegate_action(TranslateDelegate())
        # Assign an action to the behavior
        self.bind_response_action(TranslateResponse())

    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass
