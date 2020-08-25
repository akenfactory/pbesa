## An artificial intelligence platform for the implementation of multi-agent systems based on python 3 and the BESA model
Actually, Agents and MultiAgent Systems (MAS) are one of the most prominent and attractive technologies in Engineering and
Computer Science. Agent and MAS technologies, methods, and theories are currently contributing to many diverse domains
such as information retrieval, user interface design, robotics, computer games, education and training, smart environments, social simulation, management projects, e-business, knowledge management, virtual reality.

An Agent is an entity that includes mechanisms to receive perceptions from its environment and modify it. The work of an agent is to decide or to infer which is the most adequate action to achieve a specific goal. An agent has several resources and skills, and frequently it can communicate with other agents. The correct action is selected using a function mapping that can be expressed in different ways, ranging from simple condition-action rules to complex
inference mechanisms. In some cases the mapping function can be given, in agents with mayor autonomy this function can be directly learned by the agent.

The capabilities of an isolated agent are limited to its resources and abilities. When objectives get more complex, the mapping function to select the best action is less efficient, because the complexity of this function is increased. Thus, it is more efficient to build several agents, where each agent contributes to achieve the general goal. A MAS can be defined as a collection of agents that cooperate to achieve a goal.

# BESA
The abstract model of BESA is based in three fundamental concepts: a modular behaviororiented agent architecture, an event-driven control approach implementing a select like mechanism, and a social-based support for cooperation between agents.

### Behavior-Oriented
When building agents, one of the critical problems to solve is the complexity; as the agent is intended to be more rational and autonomous, the elements involved became more complex. In order to deal with this growing problem,
different modular architectures have been proposed. The fundamental idea is to break down a complex entity into a set of small simpler ones.

### Event-Driven
In the BESA model, an agent is seen as it is immersed in an environment populated of events. An event can be interpreted as a signal allowing to perceive that something interesting for an agent has occurred, and can include
information about what has happened. What is really relevant is not the information, but the fact that the agent receives an stimulus and must react to produce a response.

### Social-Based
In order to analyze and design a MAS, the use of a social based model allows to study the system
as an organization of interacting entities. Ferber has proposed a set of essential functions and dimensions to analyze an organization of agents; such approach has the advantage of identifying in a structured way the relations of the entities
composing the system, as well as the connections with other systems.

See full paper: [BESA PAPER](https://pdfs.semanticscholar.org/5836/027c6c07b124ac86d3343aa56b43b52779e6.pdf)

# Install PBESA
pip install pbesa

# Get started
To create a MAS with PBESA, you need to follow 3 simple steps:

### Step 1 - Create a PBESA container:
```
from pbesa.kernel.system.Adm import Adm
mas = Adm()
mas.start()
```
### Step 2 - Create an action:
```
from pbesa.kernel.agent.Action import Action
class ResponseAction(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data):
        """ Response """
        print(data)
```
### Step 3 - Create an agent:
- Define Agent
```
from pbesa.kernel.agent.Agent import Agent
class ResponseAgent(Agent):
    """ Through a class the concept of agent is defined """

    def __init__(self, dbConfig):
        """ This method is required for the operation of the agent """
        super().__init__(dbConfig)
    
    def setUp(self, arg):
        """
        The agent ID, state and behaviors are defined
        """
        settings = {
            'id': arg['id'],
            'state': {
                'status': arg['status'],
            },
            'behaviors': [
                {'name': 'Dialog', 'events':[
                    {'performative': 'hello', 'action': ResponseAction()}
                ]}
            ]
        }
```
- Start agent
```
conf = {
    'id': agID,
    'status': 'ACTIVE'
}
ag = ResponseAgent(conf)
ag.start()
```
### Step 4 - Run MAS:
```
data = "Hello World"
mas.sendEvent('Jarvis', 'hello', data)
```
