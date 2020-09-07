from pbesa.social.linealcontroller.delegateaction import DelegateAction

class TranslateDelegate(DelegateAction):
    """ An action is a response to the occurrence of an event """

    def delegate(self, data):
        """
        Catch the exception.
        @param exception Response exception
        """
        tokens = None
        if '_' in data:
            tokens = data.split('_')
        if ' ' in data:
            tokens = data.split('_')
        self.toAssign(tokens[0].lower())
        self.toAssign(tokens[1].lower())
        self.activeTimeout(3)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
