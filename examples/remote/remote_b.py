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
from pbesa.kernel.system.adm import Adm
from mas.worker.counteragent import CounterAgent

# --------------------------------------------------------
# Main
# --------------------------------------------------------
if __name__ == "__main__":
    """ Main """
    try:
        #-------------------------------------------------
        # Initialize the master container
        conf = {
            "container_name": "slaveB",
            "user" : "containerB",
            "host" : "172.23.0.2",
            "port" : 8002,
            "remote" : {
                "master_mode": False,
                "attempts": 10,
                "master_host": "172.23.0.4",
                "master_port": 8001
            }
        }
        mas = Adm()
        mas.start_by_conf(conf)

        # Defines the controller ID
        ctrID = 'Jarvis'

        #-------------------------------------------------
        # Create the worker agents
        workeList = []
        for it in range(4, 7):
            wID = 'w_%d' % it
            w = CounterAgent(wID)
            w.suscribe_remote_controller(ctrID)
            w.start()
    except:
        traceback.print_exc()
