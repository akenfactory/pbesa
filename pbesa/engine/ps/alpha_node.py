from ...kernel.system.Adm import Adm
from .psagent.template import TypeSlot

class AlphaNode():
    
    def __init__(self, pattern):
        self.id = None
        self.__children = []
        self.alpha_memory = []
        self.counter_list = []
        self.pattern = pattern.name
        for slot in pattern.slots:
            if slot.slot_type == TypeSlot.KEY:
                self.id = slot.name
                break
        for slot in pattern.slots:
            if slot.slot_type == TypeSlot.COUNTER:
                self.counter_list.append(slot.name)

    def add_beta_node(self, beta_node):
        no_exist = True
        for beta in self.__children:
            if beta.name == beta_node.name:
                no_exist = False
                break
        if no_exist:
            self.__children.append(beta_node)

    def retract(self, fact):
        # Actualiza el ID del fact
        if not fact.id:
            fact.update_id(self.id)
        new_alpha_memory = []
        for fct in self.alpha_memory:
            if not fct.id == fact.id:
                new_alpha_memory.append(fct)
        self.alpha_memory = new_alpha_memory
        db = Adm().getDBConnection()
        db["work_memory"].delete_one({"id": fact.id})
        
    def evaluate(self, fact, propagate_flag):
        if fact.template == self.pattern:
            # Actualiza el ID del fact
            if not fact.id:
                fact.update_id(self.id)
            # Actualiza el objeto
            updatedList = []
            for i in range(0, len(self.alpha_memory)):
                cur_fact = self.alpha_memory[i]
                if cur_fact.id == fact.id:
                    for key, item in fact.obj.items():
                        if key in self.counter_list:
                            cur_fact.obj[key] = cur_fact.obj[key] + item
                        else:
                            cur_fact.obj[key] = item
                    updatedList.append((i, cur_fact))
                    break
            # Actualiza la memoria
            db = Adm().getDBConnection()
            if len(updatedList) > 0:
                for up in updatedList:
                    self.alpha_memory.pop(up[0])
                    self.alpha_memory.append(up[1])
                    db["work_memory"].delete_one({"id": up[1].id})
                    db["work_memory"].insert_one(up[1].to_dict())    
            else:
                self.alpha_memory.append(fact)
                db["work_memory"].insert_one(fact.to_dict())
            # Propaga
            if propagate_flag:
                for child in self.__children:
                    #if not child.fire:
                    #print("=========================>",self.pattern, child.name)
                    child.evaluate()

    def load_fact(self, fact):
        self.alpha_memory.append(fact)
