from pbesa.social.linealcontroller.responseaction import ResponseAction

class TranslateResponse(ResponseAction):
    """ An action is a response to the occurrence of an event """

    def endOfProcess(self, resultDict, timeout):
        """
        Catch the exception.
        @param exception Response exception
        """
        result = "%s %s" % (resultDict['w1'], resultDict['w2'])
        self.sendResponse(result)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
