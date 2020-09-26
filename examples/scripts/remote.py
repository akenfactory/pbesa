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

# --------------------------------------------------------
# Main
# --------------------------------------------------------
if __name__ == "__main__":
    """ Main """
    try:
        # Initialize the master container
        conf = {
            "user" : "local",
            "ip" : "localhost",
            "port" : 8001,
            "remote" : {
                "master_mode": True
            }     
        }
        mas = Adm()
        mas.startByConf(conf)
    except:
        traceback.print_exc()
