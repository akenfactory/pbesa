from ....kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class RetractFactAction(Action):
    
    def execute(self, data):
        self.agent.engine.retract_fact(data)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

