from pbesa.social.linealcontroller.delegateaction import DelegateAction

class CounterDelegate(DelegateAction):
    """ An action is a response to the occurrence of an event """

    def delegate(self, data):
        """
        Catch the exception.
        @param exception Response exception
        """
        for it in range(1, 10):
            self.toAssign(10)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        print(exception)
