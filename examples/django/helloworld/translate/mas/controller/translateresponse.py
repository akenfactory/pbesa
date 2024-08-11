from pbesa.social.secuencial_team.response_action import ResponseAction

class TranslateResponse(ResponseAction):
    """ An action is a response to the occurrence of an event """

    def end_of_process(self, resultDict, timeout):
        """
        Catch the exception.
        @param exception Response exception
        """
        result = "%s %s" % (resultDict['w1'], resultDict['w2'])
        self.send_response(result)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
