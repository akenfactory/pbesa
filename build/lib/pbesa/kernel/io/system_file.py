# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
-------------------------- PBESA -------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 08/08/24
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import json

# --------------------------------------------------------
# Define component
# --------------------------------------------------------

class SystemFile(object):
    """ System file class """
    
    # Path
    path = None

    def __init__(self, path) -> None:
        """ Constructor
        :param path: Path
        """
        self.path = path
    
    def read_json_file(self) -> dict:
        """ Read JSON file """
        with open(self.path) as f:
            data = json.load(f)
        return data