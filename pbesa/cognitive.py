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

import re
import traceback
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod
from pbesa.models import AIFoundry, AzureInference, GPTService, ServiceProvider
from pbesa.social.dialog import DialogState, imprimir_grafo, recorrer_interacciones, extraer_diccionario_nodos, ActionNode, DeclarativeNode#, TerminalNode
from pbesa.social.prompts import CLASSIFICATION_PROMPT, DERIVE_PROMPT
# --------------------------------------------------------
# Define DTOs
# --------------------------------------------------------

class InteraccionDTO(BaseModel):
    tipo: str
    texto: str
    actor: str
    equipo: Optional[str] = None
    herramienta: Optional[str] = None
    interacciones: List["InteraccionDTO"] = []

def interaccion_serializer(interaccion):
    if isinstance(interaccion, list):
        return [interaccion_serializer(i) for i in interaccion]
    return {
        "tipo": interaccion["tipo"],
        "texto": interaccion["texto"],
        "actor": interaccion["actor"],
        "equipo": interaccion["equipo"] if "equipo" in interaccion else None,
        "herramienta": interaccion["herramienta"] if "herramienta" in interaccion else None,
        "interacciones": [interaccion_serializer(i) for i in interaccion["interacciones"]] if "interacciones" in interaccion else []
    }

class Role():
    id: str
    name: str
    description: str
    state: str
    knowledge_base: str
    objective: str
    arquetype: str
    example: str
    tool: str
    interactions: List[InteraccionDTO]

    def __init__(
        self, id:str, 
        name:str, 
        description:str, 
        state:str, 
        knowledge_base:str, 
        objective:str,
        arquetype:str,
        tool:str,
        example:str,
        interactions:List[InteraccionDTO] = []
        ) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.state = state
        self.knowledge_base = knowledge_base
        self.objective = objective
        self.arquetype = arquetype
        self.example = example
        self.tool = tool
        self.interactions = interactions

class AgentMetadata():
    id: str
    name: str
    description: str
    state: str
    role: Role

    def __init__(self, id:str, name:str, description:str, state:str, role:Role) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.state = state
        self.role = role

# --------------------------------------------------------
# Define common functions
# --------------------------------------------------------

def define_service_provider(provider, ai_service=None) -> None:
        # Define provider
        service = None
        service_provider = ServiceProvider()
        if "GPT" in provider:
            service = GPTService()
            service_provider.register("GPT", service)
        elif "AI_FOUNDRY" in provider:
            service = AIFoundry()
            service_provider.register("AI_FOUNDRY", service)
        elif "CUSTOM_ML" in provider:
            service = ai_service()
            service_provider.register("CUSTOM_ML", service)
        elif "AZURE_INFERENCE" in provider:
            service = AzureInference()
            service_provider.register("AZURE_INFERENCE", service)
        return service_provider, service

# --------------------------------------------------------
# Define Model component
# --------------------------------------------------------

class Model(ABC):
    """ Model class """

    def __init__(self) -> None:
        """ Constructor method """
        self.model:any = None
    
    def get_model(self) -> any:
        """ Get model method 
        :return: model
        """
        return self.model
    
    @abstractmethod
    def load_model(self, config:dict) -> None:
        """ Load model method
        :param config: config
        """ 
        pass

    @abstractmethod
    def train_model(self, model_config:dict, data:any) -> any:
        """ Train model method
        :param model_config: model_config
        :param data: data
        :return: any
        """
        pass

    @abstractmethod
    def evaluate_model(self, data:any) -> any:
        """ Validate model method
        :param data: data
        :return: any
        """
        pass

    @abstractmethod
    def fit_model(self, model_config:dict, data:any) -> any:
        """ Fit model method
        :param model_config: model_config
        :param data: data
        :return: any
        """
        pass

    @abstractmethod
    def predict(self, data:any) -> any:
        """ Predict method
        :param data: data
        :return: any
        """
        pass

# --------------------------------------------------------
# Define Generative component
# --------------------------------------------------------

class Generative(ABC):
    """ Generative class """

    def __init__(self) -> None:
        """ Constructor method """
        self.model:any = None
    
    def get_model(self) -> any:
        """ Get model method 
        :return: model
        """
        return self.model
    
    def set_model(self, model:any) -> None:
        """ Set model method
        :param model: model
        """ 
        self.model = model

    def generate(self, data:any, config:dict) -> any:
        """ Generate method
        :param data: data
        :param config: config
        :return: any
        """
        pass

# --------------------------------------------------------
# Define Augmented Generation component
# --------------------------------------------------------

class AugmentedGeneration(ABC):
    """ Augmented Generation """

    def __init__(self) -> None:
        """ Constructor method """
        self.model:any = None
        self.model_conf:dict = None
        self.__work_memory:list = []
        # Define role
        self.__role = None
        # Define the provider
        self.__service_provider = None
        # Define AI service
        self.__ai_service = None
        # Set tools
        self.__def_tool_dict = self.def_tool_dict()
        
    def setup_world(self):
        """ Set up model method """
        # Define role
        self.__work_memory.append({"role": "user", "content": self.__role.objective})
        self.__work_memory.append({"role": "user", "content": self.__role.arquetype})
        self.__work_memory.append({"role": "user", "content": self.__role.example})
    
    def load_metadata(self, agent_metadata:AgentMetadata) -> None:
        """ Load metadata method
        :param agent_metadata: agent_metadata
        """
        self.__agent_metadata = agent_metadata
        self.__role = agent_metadata.role
        self.setup_world()
        
    def get_model(self) -> any:
        """ Get model method 
        :return: model
        """
        return self.model
    
    def load_model(self, provider, config, ai_service=None) -> None:
        self.__service_provider, service = define_service_provider(provider, ai_service)
        service.setup(config)
        self.__ai_service = service
    
    def update_world_model(self, fact:str) -> None:
        """ Update world model method
        :param fact: fact
        :return: str
        """
        self.__work_memory.append({"role": "user", "content": fact})

    def reset(self) -> None:
        """ Reset method """
        self.__work_memory = []
        # Set up model
        self.set_up_model()

    def derive(self, query) -> str:
        """ Generate method
        :return: str
        """
        try:
            content = self.retrieval(query)
            prompt = DERIVE_PROMPT % (content, query)
            instantane_memory = self.__work_memory.copy()
            instantane_memory.append({"role": "user", "content": prompt})
            text = self.__ai_service.generate(instantane_memory)
            print("Pensamiento:", text)
            if self.__def_tool_dict:
                tool = self.__def_tool_dict.get(self.__role.tool)
                if tool:
                    text = tool(text)
                else:
                    text = "No se ha encontrado la herramienta"
            return text
        except Exception as e:
            traceback.print_exc()
            return "Lo lamento, no puedo responder en este momento"

    def get_role(self) -> Role:
        """ Get role method
        :return: Role
        """
        return self.__role
    
    @abstractmethod
    def retrieval(self, query) -> str:
        """ Set retrieval method
        :param query: query
        :return: str
        """
        pass

    @abstractmethod
    def def_tool_dict(self) -> dict | None:
        """ Set tool array method
        :return: dict
        """
        pass

# --------------------------------------------------------
# Define Rational component
# --------------------------------------------------------

class Rational(ABC):
    """ Rational class """

    def __init__(self) -> None:
        """ Constructor method """
        self.model:any = None
        self.__work_memory:list = []
    
    def get_model(self) -> any:
        """ Get model method 
        :return: model
        """
        return self.model
    
    def set_model(self, model:any) -> None:
        """ Set model method
        :param model: model
        """ 
        self.model = model
    
    def derive(self, data:any, config:dict) -> any:
        """ Generate method
        :param data: data
        :param config: config
        :return: any
        """
        pass

# --------------------------------------------------------
# Define Production component
# --------------------------------------------------------

class Production(ABC):
    """ Rational class """

    def __init__(self) -> None:
        """ Constructor method """
        self.model:any = None
        self.model_conf:dict = None
        self.__work_memory:list = []
        # Define role
        role = self.define_role() 
        self.__role = role.strip() if role else "Undefined"
        # Define rule set
        self.__rule_set = self.define_rule_set()
        # Define example
        self.__example = self.define_example()
        # Define model adapter
        self.__model_adapter = None
        # Set up model
        self.set_up_model()

    def set_up_model(self):
        """ Set up model method """
        # Define role
        self.__work_memory.append({"role": "system", "content": self.__role})
        # Iterate over the rule set
        self.__work_memory.append({"role": "system", "content": "Sigue estrictamente las siguientes reglas:"})
        for rule in self.__rule_set:
            self.__work_memory.append({"role": "system", "content": rule})
        self.__work_memory.append({"role": "system", "content": "Ejemplo:"})
        # Define example
        self.__work_memory.append({"role": "system", "content": self.__example})
        
    def get_model(self) -> any:
        """ Get model method 
        :return: model
        """
        return self.model
    
    def load_model(self, model:any, model_conf:dict) -> None:
        """ Set model method
        :param model: model
        :param model_conf: Configuration
        """
        self.model = model
        self.model_conf = model_conf
        #self.__model_adapter = OpenAIAdapter(self.model, self.model_conf, self.__work_memory)

    def get_rule_set(self) -> list:
        """ Get rule set method
        :return: list
        """
        return self.__rule_set
    
    def update_world_model(self, fact:str) -> None:
        """ Update world model method
        :param fact: fact
        :return: str
        """
        self.__work_memory.append({"role": "user", "content": fact})

    def reset(self) -> None:
        """ Reset method """
        self.__work_memory = []
        # Set up model
        self.set_up_model()

    def derive(self) -> str:
        """ Generate method
        :return: str
        """
        return self.__model_adapter.generate()

    @abstractmethod
    def define_role(self) -> str:
        """ Set role set method """
        pass

    @abstractmethod
    def define_rule_set(self) -> tuple:
        """ Set rule set method """
        pass

    @abstractmethod
    def define_example(self) -> str:
        """ Set example set method """
        pass

# --------------------------------------------------------
# Define Dialog component
# --------------------------------------------------------

class Dialog(ABC):
    """ Dialog """

    def __init__(self) -> None:
        """ Constructor method """
        self.model:any = None
        self.model_conf:dict = None
        self.__work_memory:list = []
        self.__meta_work_memory:list = []
        # Define role
        self.__agent_metadata = "Undefined"
        # Define role
        self.__role: Role = None
        # Define DFA
        self.__dfa = None
        #dfa = self.define_dfa()
        #self.__dfa = dfa if dfa else "Undefined"
        # Set dialog state
        self.__dialog_state = DialogState.START
        # Define the provider
        self.__service_provider = None
        # Define AI service
        self.__ai_service = None
        # Define deep
        self.__deep_count = 0
        self.__deep_limit = 3

    def setup_world(self):
        """ Set up model method """
        # Define role
        self.__work_memory.append({"role": "user", "content": self.__role.objective})
        self.__work_memory.append({"role": "user", "content": self.__role.arquetype})
        self.__work_memory.append({"role": "user", "content": self.__role.example})
        
    def get_model(self) -> any:
        """ Get model method 
        :return: model
        """
        return self.model
    
    def get_role(self) -> Role:
        """ Get role method
        :return: Role
        """
        return self.__role
    
    def set_dialog_state(self, dialog_state) -> None:
        """ Set dialog state method
        :param dialog_state: dialog_state
        """
        self.__dialog_state = dialog_state
    
    def get_dialog_state(self) -> DialogState:
        """ Get dialog state method
        :return: DialogState
        """
        return self.__dialog_state
    
    def load_metadata(self, agent_metadata:AgentMetadata) -> None:
        """ Load metadata method
        :param agent_metadata: agent_metadata
        """
        self.__agent_metadata = agent_metadata
        self.__role = agent_metadata.role
        self.setup_world()
        interations = agent_metadata.role.interactions
        grafo = recorrer_interacciones(interations)
        print("")
        # Si el grafo es una lista de nodos, lo imprimimos cada uno
        if isinstance(grafo, list):
            for nodo in grafo:
                imprimir_grafo(nodo)
        else:
            imprimir_grafo(grafo)
        print("")
        # Ejemplo de uso:
        self.__dfa = extraer_diccionario_nodos(grafo)
        # Mostrar el diccionario
        for clave, valor in self.__dfa.items():
            print(f"{clave}: {valor.text}")
        print("")
        iniciadores = []
        for item in interations:
            for clave, valor in self.__dfa.items():
                if valor.text == item['texto']:
                    iniciadores.append(valor)
        print("Iniciadores:")
        for iniciador in iniciadores:
            print(iniciador.text)
        print("")
        # Set dialog state
        self.__dfa['start'] = iniciadores

    def load_model(self, provider, config, ai_service=None) -> None:
        self.__service_provider, service = define_service_provider(provider, ai_service)
        service.setup(config)
        self.__ai_service = service
    
    def update_world_model(self, fact:str) -> None:
        """ Update world model method
        :param fact: fact
        :return: str
        """
        self.__work_memory.append({"role": "user", "content": fact})

    def reset(self) -> None:
        """ Reset method """
        self.__work_memory = []
        # Set up model
        self.set_up_model()

    def team_inquiry(self, team, data, operation, session_flag) -> str:
        canales = self.state['canales']
        canal = canales.get(team)
        dto = None
        if operation:
            dto = {
                "data": {
                    'text': data,
                    'operation': operation
                },
            }
        else:
            if session_flag:
                pass
                #session_id = self.state['session_id']
                #print("=> session_flag -> " + session_id)
                #dto = {
                #    "data": {
                #        'text': data,
                #        'session_id': session_id
                #    },
                #}
            else:
                dto = {
                    "data": {
                        'text': data
                    },
                }
        response = canal.post(team.lower(), dto)
        if response['status']:
            return response['message']['response']
        return "Lo lamento, no puedo responder en este momento"
    
    def get_text(self, inputs) -> str:
        matches = re.findall(r'<\|im_start\|>(user|assistant)\n(.*?)<\|im_end\|>', inputs, re.DOTALL)
        if matches:
            messages = []
            for speaker, text in matches:
                messages.append({
                    "Assistant": speaker.capitalize(),
                    "User": text.strip()
                })
            if len(messages) > 0:
                return messages[-1]["Assistant"]
            else:
                return messages[-1]["User"]
        return inputs

    def transition(self, owner, dialog_state, query, team_source=False) -> str:
        text = ""
        node = self.__dfa[dialog_state]
        if not isinstance(node, list):
            node = node.children
        options = ""
        cont = 1
        for item in node:
            options += f"{cont}) {item.text}\n"
            cont += 1
        prompt = CLASSIFICATION_PROMPT % (query, options)
        print("Query:", query, "\n", "Options:", options)
        self.__meta_work_memory.append({"role": "user", "content": prompt})
        text = self.__ai_service.generate(self.__meta_work_memory)
        self.__meta_work_memory = []
        print("Pensamiento:", text)

        select_node = None
        for option in range(1, cont):
            if str(option) in text:
                select_node = node[option-1]
                break
        if not select_node:
            print("=> No se seleccionó ninguna opción")
            print("=> Node:", node)
            print("=> len node:", len(node))
            if node and len(node)> 0: 
                select_node = node[0]
                print(select_node.text)
            text = "Lo lamento, no puedo responder en este momento"
            print("???> text:", text)
            text = self.get_text(text)
            return owner, DialogState.START, text, owner
        
        if team_source:
            self.__work_memory.append({"role": "user", "content": select_node.text})
        else:
            self.__work_memory.append({"role": "user", "content": query})
            self.__work_memory.append({"role": "user", "content": select_node.text})  

        new_owner, new_dialog_state, text, team = self.do_transition(owner, select_node.children[0], query)
        text = self.get_text(text)
        return new_owner, new_dialog_state, text, team

    def do_transition(self, owner, node, query) -> str:
        """ Generate method
        :return: str
        """          
        if isinstance(node, DeclarativeNode):
            print("-> node:", node.text)
            self.__work_memory.append({"role": "user", "content": node.text})
        elif isinstance(node, ActionNode):

            #------------------------------
            # Accion
            #------------------------------

            print("-> node action:", node.action)
            if node.tool and not node.tool == "Ninguno":
                print("-> node tool:", node.tool)
                self.__work_memory.append({"role": "user", "content": node.text})            
                res = self.__ai_service.generate(self.__work_memory)

                # Check if res is empty
                if not res or res == "":
                    res = "Lo lamento, no puedo responder en este momento"
                    return owner, DialogState.START, res, owner

                print("-> node tool: envia", res)

                text = self.team_inquiry(node.team, res, node.tool, False)   
            else:

                #------------------------------
                # Lllamada
                #------------------------------

                print("-> node team:", node.team)
                # Verifica si el nodo es termianl ya que significa
                # que el dialogo cambia de agente
                if node.is_terminal:
                    print("-> node team -> es terminal -> " + node.text)
                    self.__work_memory.append({"role": "user", "content": node.text})
                    res = self.__ai_service.generate(self.__work_memory)
                    res = self.get_text(res)
                    self.__work_memory.append({"role": "system", "content": res})

                    # Check if res is empty
                    if not res or res == "":
                        res = "Lo lamento, no puedo responder en este momento"
                        return owner, DialogState.START, res, owner

                    print("-> node team -> envia:", res)
                    #text = self.team_inquiry(node.team, res, None, True)
                    return node.team, DialogState.START, res, node.team
                else:
                    print("-> node team -> continua")
                    self.__work_memory.append({"role": "user", "content": node.text})
                    print("-> node team -> envia:", query)
                    text = self.team_inquiry(node.team, query, node.tool, False)

            self.__deep_count += 1
            if self.__deep_count < self.__deep_limit:
                return self.transition(owner, node.performative, text, True)
            else:
                self.__deep_count = 0
                return "Web", DialogState.START, "Lo lamento me he perdido, ¿podrías repetir la pregunta?"
        else:
            print("!!!!!!!!!!!!!!!!!!!!!!!> Otro tipo de nodo:", node.text)

        res = self.__ai_service.generate(self.__work_memory)
        res = self.get_text(res)
        self.__work_memory.append({"role": "system", "content": res})

        # Check if res is empty
        if not res or res == "":
            res = "Lo lamento, no puedo responder en este momento"
            return owner, DialogState.START, res, owner

        print("=> Pensamiento DEEP:", res)

        new_dialog_state = node.performative
        if not node.is_terminal:
            print("=> new_owner:", owner, "new_dialog_state:", new_dialog_state)
            return owner, new_dialog_state, res, owner
        
        print(f"Tipe node: {type(node)}")

        print("$$$> new_owner:", owner, "new_dialog_state:", new_dialog_state)
        return owner, new_dialog_state, res, owner
