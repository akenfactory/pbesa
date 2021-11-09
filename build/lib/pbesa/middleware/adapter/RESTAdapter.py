from threading import Thread
#from ...kernel.system.Adm import Adm
from ...kernel.util.Queue import Queue
from ...kernel.adapter.Adapter import Adapter

#import web
import json

class RESTAdapter(Adapter, Thread):

    app = None
    adm = None
    conf = None
    
    def __init__(self):
        self.adm = None #Adm()
        super().__init__()

    def setUp(self):
        urls = ('/(.*)', 'RESTAdapter')
        self.app = web.application(urls, globals())
        
    def response(self, response):
        pass
    
    def request(self):
        pass

    def finalize(self):
        pass

    def run(self):
        self.app.run()

    def GET(self, name):
        if not name:
            name = 'World'
        return 'Hello, ' + name + '!'

    def POST(self, rqst):
        data = json.loads(web.data().decode('utf-8'))                        
        queue = Queue(10)        
        dto = {'queue': queue,'url': rqst, 'data': data}
        self.adm.sendEvent('front_controller', 'request', dto)
        response = queue.get()
        queue.task_done()
        web.header('Access-Control-Allow-Origin',      '*')
        web.header('Access-Control-Allow-Credentials', 'true')        
        return str(response).replace("'", "\"")



