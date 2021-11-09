from threading import Thread
#from ...kernel.SystemTK.Adm import Adm
from ...kernel.util.Queue import Queue
from ...kernel.adapter.Adapter import Adapter

import json
import asyncio
#import websockets

class WSSAdapter(Adapter, Thread):

    IP = None
    adm = None
    PORT = None
    server = None

    def __init__(self):
        self.adm = Adm()
        conf = self.adm.getConf()
        self.IP = conf['ip']
        self.PORT = conf['port']
        super().__init__()

    def setUp(self):
        pass
        
    def response(self, response):
        pass
    
    def request(self):
        pass

    def finalize(self):
        pass

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        start_server = websockets.serve(self.handler, self.IP, self.PORT)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    # async def handler(self, websocket, path):
    #     queue = Queue(10)
    #     consumer_task = asyncio.ensure_future(self.requestHandler(websocket, path, queue))
    #     producer_task = asyncio.ensure_future(self.responseHandler(websocket, path, queue))
    #     done, pending = await asyncio.wait(
    #         [consumer_task, producer_task],
    #         return_when=asyncio.FIRST_COMPLETED,
    #     )
    #     for task in pending:
    #         task.cancel()

    async def requestHandler(self, websocket, path, queue):
        while True:
            print(queue)
            async for message in websocket:
                request = json.loads(message)
                dto = {'socket': queue, 'request': request}
                self.adm.sendEvent('front_controller', 'ws_request', dto)

    async def responseHandler(self, websocket, path, queue):
        while True:
            message = await queue.get()
            await websocket.send(message)

    async def handler(self, websocket, path):
        queue = Queue(10)
        try:
            while True:
                request = json.loads(await websocket.recv())
                print ('REQUEST: ', request)
                dto = {'socket': queue, 'request': request}
                self.adm.sendEvent('front_controller', 'ws_request', dto)
                response = str(queue.get())
                response = response.replace("'", "\"")
                print ('RESPONSE: ', response)
                await websocket.send(response)
        except Exception as inst:
            print('Controled ecxeption: ')
            print(inst)



