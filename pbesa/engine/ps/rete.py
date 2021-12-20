from .psagent.fact import Fact
from ...kernel.system.Adm import Adm
from .exceptions import PSException

class Rete():

    __agenda = []
    __new_agenda = []
    __alpha_dict = {}

    def add_alpha_node(self, alpha_node):
        self.__alpha_dict[alpha_node.pattern] = alpha_node;
    
    def get_alpha_node(self, pattern):
        return self.__alpha_dict[pattern]

    def assert_fact(self, fact):        
        self.__alpha_dict[fact.template].evaluate(fact, True)

    def update_fact(self, fact):        
        self.__alpha_dict[fact.template].evaluate(fact, False)

    def retract_fact(self, fact):        
        self.__alpha_dict[fact.template].retract(fact)

    def load_fact(self, fact):        
        self.__alpha_dict[fact.template].load_fact(fact)

    def add_fact_agenda(self, fact):
        alpha_node = self.__alpha_dict[fact.template]
        # Actualiza el ID del fact
        if not fact.id:
            fact.update_id(alpha_node.id)        
        # Actualiza el objeto
        updatedList = []
        for i in range(0, len(self.__agenda)):
            cur_fact = self.__agenda[i]
            if cur_fact.id == fact.id:
                for key, item in fact.obj.items():
                    cur_fact.obj[key] = item
                updatedList.append((i, cur_fact))
                break
        # Actualiza la agenda
        db = Adm().getDBConnection()
        if len(updatedList) > 0:
            for up in updatedList:
                self.__agenda.pop(up[0])
                self.__agenda.append(up[1])
                db["agenda"].delete_one({"id": up[1].id})
                db["agenda"].insert_one(up[1].to_dict())    
        else:
            self.__agenda.append(fact)
            db["agenda"].insert_one(fact.to_dict())

    def run_agenda(self):
        # Propaga los hechos
        for fact in self.__agenda:
            self.assert_fact(fact)
        # Reinicia la agenda
        db = Adm().getDBConnection()
        db["agenda"].delete_many({})
        self.__agenda = []
        
    def load_agenda(self):
        db = Adm().getDBConnection()
        if db:
            fact_list = db["agenda"].find({})
            for document in fact_list:
                fact = Fact(document['template'], document['obj'])
                fact.id = document['id']
                self.add_fact_agenda(fact)
        else:
            raise PSException('[Fatal, load_agenda]: Production system requires mondodb database.')

    def load_work_memory(self):
        db = Adm().getDBConnection()
        if db:
            fact_list = db["work_memory"].find({})
            for document in fact_list:
                fact = Fact(document['template'], document['obj'])
                fact.id = document['id']
                self.load_fact(fact)
        else:
            raise PSException('[Fatal, load_work_memory]: Production system requires mondodb database.')
