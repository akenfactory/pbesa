from ....kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class AssertFactAction(Action):
    
    def execute(self, data):
        self.agent.engine.assert_fact(data)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

