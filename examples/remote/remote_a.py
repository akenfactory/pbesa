# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 3.0.1
@date 27/07/20
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------
import time
import traceback
from pbesa.kernel.system.Adm import Adm
from mas.worker.counteragent import CounterAgent
from mas.controller.countercontroller import CounterController

# --------------------------------------------------------
# Main
# --------------------------------------------------------
if __name__ == "__main__":
    """ Main """
    try:
        #-------------------------------------------------
        # Initialize the master container
        conf = {
            "user" : "master",
            "host" : "172.23.0.4",
            "port" : 8001,
            "remote" : {
                "master_mode": True,
                "attempts": 10
            }
        }
        mas = Adm()
        mas.startByConf(conf)

        # Defines the controller ID
        ctrID = 'Jarvis'

        #-------------------------------------------------
        # Create the worker agents
        for it in range(1, 4):
            wID = 'w_%d' % it
            w = CounterAgent(wID)
            w.suscribeRemoteController(ctrID)
            w.start()
        
        #-------------------------------------------------
        # Create the controller agent
        ag = CounterController(ctrID)
        for it in range(1, 10):
            wID = 'w_%d' % it
            ag.suscribeRemoteAgent(wID)
        ag.start()

        # Wait for the start of the slave containers
        mas.waitFull(['slaveB', 'slaveC'])

        #-------------------------------------------------
        # Start the dynamic
        result = mas.callAgent(ctrID, None)
        print(result)
    except:
        traceback.print_exc()
