from django.apps import AppConfig
from translate.mas.worker.workeragent import WorkerAgent
from translate.mas.controller.translatecontroller import TranslateController

class TranslateConfig(AppConfig):
    name = 'translate'

    def ready(self):
        #-----------------------------------------------------
        # Create the worker agents
        w1ID = 'w1'
        w1 = WorkerAgent(w1ID)
        w1.start()
        w2ID = 'w2'
        w2 = WorkerAgent(w2ID)
        w2.start()
        
        #-----------------------------------------------------
        # Create the controller agent
        ctrID = 'Jarvis'
        ag = TranslateController(ctrID)
        ag.suscribe_agent(w1)
        ag.suscribe_agent(w2)
        ag.start()
