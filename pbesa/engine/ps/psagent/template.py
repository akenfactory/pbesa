from enum import Enum 

class TypeSlot(Enum):
    KEY = 1
    PROPERTY = 2
    COUNTER = 3
    
class Slot():

    def __init__(self, name, slot_type):
        self.name = name
        self.slot_type = slot_type

class Template():

    def __init__(self, name, *slots):
        self.slots = []
        self.name = name
        for slot in slots:
            self.slots.append(slot)