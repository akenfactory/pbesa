from ....kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class RunAgendaAction(Action):
    
    def execute(self, data):
        self.agent.engine.run_agenda()

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

