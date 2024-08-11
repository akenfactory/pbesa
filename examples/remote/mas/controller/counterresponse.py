from pbesa.social.secuencial_team.response_action import ResponseAction

class CounterResponse(ResponseAction):
    """ An action is a response to the occurrence of an event """

    def end_of_process(self, resultDict, timeout):
        """
        Catch the exception.
        @param exception Response exception
        """
        result = 0
        for res in resultDict.values():
            result += res
        self.send_response(result)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        print(exception)
