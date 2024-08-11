from pbesa.social.worker.task import Task

class TranslateTask(Task):
    """ An action is a response to the occurrence of an event """

    def run(self, data):
        """
        Execute.
        @param data Event data
        """
        if data == 'hello':
            self.send_response('Hola')
        if data == 'world':
            self.send_response('Mundo')

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        pass
