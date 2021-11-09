from ....kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class UpdateFactAction(Action):
    
    def execute(self, data):
        self.agent.engine.update_fact(data)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

