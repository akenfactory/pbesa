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

import traceback
from pbesa.mas import Adm

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
        mas.start_by_conf(conf)
    except:
        traceback.print_exc()
