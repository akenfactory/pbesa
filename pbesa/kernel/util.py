# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN & SIDRE
@version 4.0.0
@date 09/08/24
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import uuid
import base64

# --------------------------------------------------------
# Define generate short uuid
# --------------------------------------------------------

def generate_short_uuid(length=5):
    # Generate a UUID
    uuid_str = str(uuid.uuid4())
    
    # Encode UUID to bytes
    uuid_bytes = uuid.UUID(uuid_str).bytes
    
    # Encode bytes to base64 and strip non-alphanumeric characters
    base64_str = base64.urlsafe_b64encode(uuid_bytes).decode('utf-8').rstrip('=')
    
    # Return a substring of the desired length
    short_uuid = base64_str[:length]
    short_uuid.replace('_', 'A')
    short_uuid.replace('-', 'B')
    short_uuid.replace('=', 'C')
    return short_uuid.lower()