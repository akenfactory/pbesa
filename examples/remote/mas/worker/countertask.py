import time
from pbesa.social.worker.task import Task

class CounterTask(Task):
    """ An action is a response to the occurrence of an event """

    def goHead(self, data):
        """
        Execute.
        @param data Event data
        """
        for it in range(1, data + 1):
            time.sleep(1)
            print("AG: %s Count: %d" % (self.agent.id, it))
        self.sendResponse(10)

    def catchException(self, exception):
        """
        Catch the exception.
        @param exception Response exception
        """
        print(exception)
