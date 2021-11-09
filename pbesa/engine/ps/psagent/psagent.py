from .rule import Antecedent
from ..betha_node import BethaNode
from ..alpha_node import AlphaNode
from ..rete import Rete
from abc import abstractmethod
from .run_agenda_action import RunAgendaAction
from .add_fact_agenda_action import AddFactAgendaAction
from .assert_fact_action import AssertFactAction
from .retract_fact_action import RetractFactAction
from .update_fact_action import UpdateFactAction
from ....kernel.agent.Agent import Agent

class PSAgent(Agent):
    
    def __init__(self, agentID):
        self.__rules = []
        self.engine = Rete()
        self.__templates = []
        self.__periodic_action = None
        super().__init__(agentID)

    def add_template(self, template):
        self.__templates.append(template)

    def add_rule(self, rule):
        self.__rules.append(rule)

    @abstractmethod
    def def_templates(self):
        pass

    @abstractmethod
    def def_constructs(self):
        pass

    @abstractmethod
    def set_periocic_action(self):
        pass

    def build(self):
        for template in self.__templates:
            self.engine.add_alpha_node(AlphaNode(template))
        for rule in self.__rules:
            betha_node = BethaNode()
            betha_node.name = rule.name
            for consequent in rule.get_consequents():
                betha_node.add_consequent(consequent)
            for antecedent in rule.get_antecedents():
                betha_node.add_antecedent(antecedent)
                if isinstance(antecedent, Antecedent):
                    alpha_node = self.engine.get_alpha_node(antecedent.template)
                    alpha_node.add_beta_node(betha_node)
                    betha_node.add_alpha_node(alpha_node)

    def setUp(self):
        self.state = {
            'alive': False,
            'time': None
        }
        self.addBehavior('agenda_process')
        self.bindAction('agenda_process', 'run_agenda', RunAgendaAction())
        self.bindAction('agenda_process', 'add_fact_agenda', AddFactAgendaAction())
        self.addBehavior('process')
        self.bindAction('process', 'assert_fact', AssertFactAction())
        self.bindAction('process', 'update_fact', UpdateFactAction())
        self.bindAction('process', 'retract_fact', RetractFactAction())
        self.__periodic_action = self.set_periocic_action()
        if self.__periodic_action:
            self.addBehavior('periodic_process')
            self.bindAction('periodic_process', 'periodic', self.__periodic_action)
        # Build RETE
        self.def_templates()
        self.def_constructs()
        self.build()
        # Load data RETE
        self.engine.load_agenda()
        self.engine.load_work_memory()

    def shutdown(self):
        pass
