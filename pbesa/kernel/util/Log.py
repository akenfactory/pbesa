import logging

class Log(object):
    class __Log:
        def __init__(self):
            self.val = None

            FORMAT = '%(message)s %(asctime)-15s %(clientip)s %(user)-8s'
            logging.basicConfig(format=FORMAT)            
                        
            self.logger = logging.getLogger('tcpserver')            
            self.d = {'clientip': "IP", 'user': "USER"}
            
        def __str__(self):
            return repr(self) + self.val
        
        def debugMode(self, flag):
            if flag:
                self.logger.setLevel(logging.DEBUG)
            else:
                self.logger.setLevel(logging.INFO)
        
        def info(self, msg):
            self.logger.setLevel(logging.INFO)
            self.logger.info('[INFO]: %s\t at', msg, extra=self.d)
            
        def warn(self, msg):            
            self.logger.setLevel(logging.WARNING)
            self.logger.warning('[WARN]: %s\t at', msg, extra=self.d)
            
        def error(self, msg):
            self.logger.setLevel(logging.ERROR)
            self.logger.error('[ERRO]: %s\t at', msg, extra=self.d)
        
        def debug(self, msg):            
            self.logger.debug('[DEBG]: %s\t at', msg, extra=self.d)
            
    instance = None
    def __new__(cls):
        if not Log.instance:
            Log.instance = Log.__Log()
        return Log.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)
    