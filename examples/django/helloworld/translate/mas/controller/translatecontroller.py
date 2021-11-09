from .translatedelegate import TranslateDelegate
from .translateresponse import TranslateResponse
from pbesa.social.linealcontroller.linealcontroller import LinealController

class TranslateController(LinealController):
    """ Through a class the concept of agent is defined """
    
    def build(self):
        """
        Method that allows defining the structure and 
        resources of the agent
        """
        # Assign an action to the behavior
        self.bindDelegateAction(TranslateDelegate())
        # Assign an action to the behavior
        self.bindResponseAction(TranslateResponse())

    def shutdown(self):
        """ Method to free up the resources taken by the agent """
        pass
