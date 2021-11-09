from pbesa.social.linealcontroller.responseaction import ResponseAction

class CounterResponse(ResponseAction):
    """ An action is a response to the occurrence of an event """

    def endOfProcess(self, resultDict, timeout):
        """
        Catch the exception.
        @param exception Response exception
        """
        result = 0
        for res in resultDict.values():
            result += res
        self.sendResponse(result)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        print(exception)
