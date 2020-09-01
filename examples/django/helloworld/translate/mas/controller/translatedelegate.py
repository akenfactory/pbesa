from pbesa.social.linealcontroller.delegateaction import DelegateAction

class TranslateDelegate(DelegateAction):
    """ An action is a response to the occurrence of an event """

    def delegate(self, data):
        """
        Catch the exception.
        @param exception Response exception
        """
        #
        tokens = data.split('_')
        self.toAssign(tokens[0])
        self.toAssign(tokens[1])
        self.activeTimeout(3)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
