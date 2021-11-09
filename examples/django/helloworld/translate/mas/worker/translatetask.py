from pbesa.social.worker.task import Task

class TranslateTask(Task):
    """ An action is a response to the occurrence of an event """

    def goHead(self, data):
        """
        Execute.
        @param data Event data
        """
        if data == 'hello':
            self.sendResponse('Hola')
        if data == 'world':
            self.sendResponse('Mundo')

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
