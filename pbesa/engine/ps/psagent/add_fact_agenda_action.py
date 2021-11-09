from ....kernel.agent.Action import Action

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------
class AddFactAgendaAction(Action):
    
    def execute(self, data):
        self.agent.engine.add_fact_agenda(data)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass

