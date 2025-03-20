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
import logging
import traceback
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod
from pbesa.models import AIFoundry, AzureInference, GPTService, ServiceProvider
from pbesa.social.dialog import DialogState, imprimir_grafo, recorrer_interacciones, extraer_diccionario_nodos, ActionNode, DeclarativeNode#, TerminalNode
from pbesa.social.prompts import CLASSIFICATION_PROMPT, DERIVE_PROMPT, RECOVERY_PROMPT
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
        self.setup_world()

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
            logging.info(f"Thought: {text}")
            if self.__def_tool_dict:
                tool = self.__def_tool_dict.get(self.__role.tool)
                if tool:
                    text = tool(text)
                else:
                    text = "No se ha encontrado la herramienta"
            return text
        except Exception as e:
            traceback.print_exc()

            logging.info(f"------------RESET---------------")
            self.reset()

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
        # Define knowledge
        self.knowledge = None
        # Define point recovery
        self.__recovery = {
            "owner": "Web",
            "team": "Web",
            "performative": DialogState.START,
            "counter": 0
        }
        # Define recovery message
        self.RECOVERY_MSG = "Lo lamento, puedes darme más detalles o reformular"

    def setup_world(self):
        """ Set up model method """
        # Define role
        instrucciones = f"Instrucciones:\n{self.__role.description}\n Tu tarea: {self.__role.objective}\n"
        requisitos = f"Requisitos:\n{self.__role.arquetype}\n"
        ejemplo = f"Ejemplo:\n{self.__role.example}\n"
        if self.knowledge:
            conocimiento = f"Conocimiento:\n{self.knowledge}\n"
        continuar = "Ahora, evalúa el siguiente caso:\n"
        self.__work_memory.append({"role": "user", "content": instrucciones})
        self.__work_memory.append({"role": "user", "content": requisitos})
        self.__work_memory.append({"role": "user", "content": ejemplo})
        if self.knowledge:
            self.__work_memory.append({"role": "user", "content": conocimiento})
        self.__work_memory.append({"role": "user", "content": continuar})
        
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
        logging.debug("")
        # Si el grafo es una lista de nodos, lo imprimimos cada uno
        if isinstance(grafo, list):
            for nodo in grafo:
                imprimir_grafo(nodo)
        else:
            imprimir_grafo(grafo)
        logging.debug("")
        # Ejemplo de uso:
        self.__dfa = extraer_diccionario_nodos(grafo)
        # Mostrar el diccionario
        for clave, valor in self.__dfa.items():
            logging.debug(f"{clave}: {valor.text}")
        logging.debug("")
        iniciadores = []
        for item in interations:
            for clave, valor in self.__dfa.items():
                if valor.text == item['texto']:
                    iniciadores.append(valor)
        logging.debug("Iniciadores:")
        for iniciador in iniciadores:
            logging.debug(iniciador.text)
        logging.debug("")
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
        self.setup_world()
        # Reset dialog state
        self.__recovery = {
            "owner": "Web",
            "team": "Web",
            "performative": DialogState.START,
            "counter": 0
        }

    def notify(self, text):
        try:
            canales = self.state['canales']
            canal = canales.get("Webhook")
            session_id = self.state['session_id']
            dto = {
                "session_id": session_id,
                "text": text[0:100]
            }
            response = canal.post("notify", dto)
            if response['status']:
                logging.info(f"Notificación enviada: {text}")
            else:
                logging.warning(f"Notificación no enviada: {text}")
        except Exception as e:
            logging.error(f"Error al enviar notificación: {text}")
            logging.erro(f"Error: {e}")

    def team_inquiry(self, team, data, operation, session_flag) -> str:
        try:
            dto = None
            canales = self.state['canales']
            canal = canales.get(team)
            if session_flag:
                dto = {
                    "data": {
                        'text': data,
                        'session_id': self.state['session_id'],
                    },
                }
                # Evia mensaje a los agentes remotos
                logging.info('>>>> Call remote agent: team.\n')
                response = canal.post(team.lower(), dto)
                if response and not response['status']:
                    logging.error(f'No se pudo establecer la comunicación con el agente remoto')
                    return None
                logging.info(f'>>>> Response: {response}')
                return response['message']['response']
            else:
                if operation:
                    dto = {
                        "data": {
                            'text': data,
                            'operation': operation
                        },
                    }
                else:
                    dto = {
                        "data": {
                            'text': data
                        },
                    }
                response = canal.post(team.lower(), dto)
                if response['status']:
                    return response['message']['response']
                else:
                    return None
            logging.info("END: team_inquiry")
        except Exception as e:
            logging.error(f"Error al consultar al equipo: {team}")
            return None

    def get_text(self, mensaje) -> str:
        if mensaje:
            mensaje_limpio = mensaje.replace("<|im_start|>user<|im_sep|>", "").replace("<|im_start|>system<|im_sep|>", "")
            mensaje_limpio = mensaje_limpio.replace("<|im_start|>", "").replace("<|im_sep|>", "").replace("<|im_end|>", "")
            mensaje_limpio = mensaje_limpio.replace("[Usuario]: ", "").replace("[Sistema]: ", "")
            return mensaje_limpio.strip()
        else:
            return ""
    
    def recovery(self, query):
        try:
            prompt = RECOVERY_PROMPT % query
            temp_work_memory = [{"role": "user", "content": prompt}]
            res = self.__ai_service.generate(temp_work_memory)
            res = self.get_text(res)
            if res and not res == "":
                return self.__recovery['owner'], self.__recovery['performative'], res, self.__recovery['team']
            else:
                logging.info(f"------------RESET---------------")
                logging.info(f"Recovery from: {self.__recovery['performative']}")
                self.reset()
                self.notify("STOP") 
                return "Web", DialogState.START, self.RECOVERY_MSG, "Web"
        except Exception as e:
            return self.RECOVERY_MSG

    def transition(self, owner, dialog_state, query, team_source=False) -> str:
        try:
            res = ""
            logging.info(f"TOPTQ: {owner} - {dialog_state} - {team_source} - {query}")
            # Punto de restauración
            counter = (self.__recovery['counter'] + 1) if self.__recovery['performative'] == dialog_state else self.__recovery['counter']
            self.__recovery = {
                "owner": owner,
                "team": owner,
                "performative": dialog_state,
                "counter": counter
            }
            logging.info(f"Recovery attemps: {self.__recovery["counter"]}")
            # Verifica si se ha alcanzado el límite de recuperación
            if self.__recovery['counter'] <= 3:
                self.notify("identificando la performativa...")
                # Verifica que exista la performativa
                if not dialog_state in self.__dfa:
                    self.notify("performativa no encontrada")
                    return self.recovery(query)
                # Performativa encontrada
                children = None
                self.notify("performativa encontrada")
                node = self.__dfa[dialog_state]
                if not isinstance(node, list):
                    children = node.children
                else:
                    children = node
                # Flujo de selección
                select_node = None
                self.notify("flujo de seleccion...")
                if children and len(children)> 1:
                    logging.info(f"--> Más de una opción.")
                    options = ""
                    cont = 1
                    for item in children:
                        options += f"{cont}) {item.text}\n"
                        cont += 1
                    prompt = CLASSIFICATION_PROMPT % (query, options)
                    logging.info(f"Query: {query},\n Options:\n{options}")
                    self.__meta_work_memory.append({"role": "user", "content": prompt})
                    res = self.__ai_service.generate(self.__meta_work_memory)
                    logging.info(f"Thought: {res}")
                    self.__meta_work_memory = []
                    res = self.get_text(res)
                    for option in range(1, cont):
                        if str(option) in res:
                            select_node = children[option-1]
                            logging.info(f"Select node: {select_node.text}")
                            break
                    if not select_node:
                        logging.info("=> No se seleccionó ninguna opción")
                        select_node = children[0]
                        logging.info(f"=> Selecciona el primer nodo: {select_node.text}")               
                elif children and len(children) == 1:
                    logging.info(f"--> Una opción.")
                    select_node = children[0]
                else:
                    logging.info(f"???????????????????> text: {res} es terminal")    
                # Nuevo nodo
                if select_node:
                    res = select_node.text
                    node = select_node.children[0]
                # Nodo seleccionado
                logging.info(f"Flujo normal: {res}")
                self.notify(res)
                if team_source:
                    self.__work_memory.append({"role": "user", "content": res})
                else:
                    self.__work_memory.append({"role": "user", "content": query})
                    self.__work_memory.append({"role": "user", "content": res})
                # Efectua inferencia  
                new_owner, new_dialog_state, res, team = self.do_transition(owner, node, query)
                res = self.get_text(res)
                return new_owner, new_dialog_state, res, team
            else:
                logging.info(f"------------RESET---------------")
                self.notify("STOP")
                self.reset()
                return "Web", DialogState.START, self.RECOVERY_MSG, "Web"
            logging.info("END: do_transition")
        except Exception as e:
            traceback.print_exc()
            logging.info(f"------------RESET---------------")
            self.reset()
            self.notify("STOP")
            return owner, DialogState.START, "Lo lamento, no puedo responder en este momento", owner

    def do_transition(self, owner, node, query) -> str:
        """ Generate method
        :return: str
        """
        try:
            if isinstance(node, ActionNode):
                self.notify("realizando acción...")
                #------------------------------
                # Accion
                #------------------------------
                logging.info(f"-> node action: {node.action}")
                if node.tool and not node.tool == "Ninguno":
                    self.notify("aplicando herramienta...")
                    logging.info(f"-> node tool: {node.tool}")
                    self.__work_memory.append({"role": "user", "content": node.text})
                    logging.info("-----")
                    logging.info("\n%s", json.dumps(self.__work_memory, indent=4))
                    logging.info("-----")         
                    res = self.__ai_service.generate(self.__work_memory)
                    logging.info(f"-> node tool: {res}")
                    res = self.get_text(res)
                    # Check if res is empty
                    if not res or res == "":
                        self.notify("no pude hacer uso de la herramienta")
                        return self.recovery(query)
                    logging.info(f"-> node tool: envia -> {res}")
                    res = self.team_inquiry(node.team, res, node.tool, False)   
                else:
                    self.notify("realizando llamada...")
                    #------------------------------
                    # Lllamada
                    #------------------------------
                    logging.info(f"-> node team: {node.team}")
                    # Verifica si el nodo es termianl ya que significa
                    # que el dialogo cambia de agente
                    if node.is_terminal:
                        logging.info(f"-> node team -> es terminal -> {node.text}")
                        self.__work_memory.append({"role": "user", "content": node.text})
                        logging.info("-----")
                        logging.info("\n%s", json.dumps(self.__work_memory, indent=4))
                        logging.info("-----")
                        res = self.__ai_service.generate(self.__work_memory)
                        res = self.get_text(res)
                        self.__work_memory.append({"role": "system", "content": res})
                        # Check if res is empty
                        if not res or res == "":
                            self.notify(f"no pude contactar al agente: {node.team}")
                            return self.recovery(query)                    
                        self.notify(f"le envio al agente {node.team}: {res}")
                        logging.info(f"-> node team -> envia: {res}")
                        res = self.team_inquiry(node.team, res, None, True)
                        if res and not res == "ERROR" and not res == "":
                            logging.info(f"------------RESET---------------")
                            self.reset()
                            self.notify("STOP")
                            return node.team, DialogState.START, res, node.team
                        else:
                            return self.recovery(query)
                    else:
                        logging.info("-> node team -> continua")
                        self.__work_memory.append({"role": "user", "content": node.text})
                        logging.info(f"-> node team -> envia: {query}")
                        res = self.team_inquiry(node.team, query, node.tool, False)
                        self.notify(f"continuando con díalogo")
                # Adiciona el texto al work memory
                if res and not res == "ERROR" and not res == "":
                    logging.info(f"-> Adicion WM node team -> text: {res}")
                    self.__work_memory.append({"role": "system", "content": res})
                else:
                    return self.recovery(query)
                logging.info("#########> Procesa respuesta del equipo en profundidad")
                # Verifica si se alcanzó el límite de profundidad
                self.__deep_count += 1
                if self.__deep_count < self.__deep_limit:
                    self.notify("efectuando inferencia en profundidad")
                    return self.transition(owner, node.performative, res, True)
                else:
                    self.notify(f"se alcanzó el límite de profundidad: {self.__deep_count}")
                    self.__deep_count = 0
                    logging.info("-> node team -> deep limit")
                    logging.info(f"------------RESET---------------")
                    self.notify("STOP")
                    self.reset()
                    return "Web", DialogState.START, self.RECOVERY_MSG, "Web"
            else:
                self.notify("efectuando inferencia...")
                logging.info(f"D -> node: {node.text}")
                self.__work_memory.append({"role": "user", "content": node.text})
                logging.info(f"=> !!!!: {query}")
                logging.info("-----")
                logging.info("\n%s", json.dumps(self.__work_memory, indent=4))
                logging.info("-----")
                res = self.__ai_service.generate(self.__work_memory)
                res = self.get_text(res)
                self.__work_memory.append({"role": "system", "content": res})
                # Check if res is empty
                if not res or res == "":
                    return self.recovery(query)
                logging.info(f"=> Thought DEEP: {res}")
                self.notify(f"Realizando inferencia: {res}")
                new_dialog_state = node.performative
                if not node.is_terminal:
                    self.notify(f"continuando díalogo de inferencia")
                    return owner, new_dialog_state, res, owner
                self.notify(f"finalizando díalogo de inferencia")
                logging.info(f"Tipe node: {type(node)}")
                logging.info(f"$$$> new_owner: {owner} new_dialog_state: {new_dialog_state}")
                self.notify("STOP")
                return owner, new_dialog_state, res, owner
            logging.info("END: do_transition")
        except Exception as e:
            traceback.print_exc()
            logging.info(f"------------RESET---------------")
            self.reset()
            self.notify("STOP")
            return owner, DialogState.START, "Lo lamento, no puedo responder en este momento", owner

    def set_knowledge(self, knowledge) -> str:
        """ Set knowledge method
        :param query: query
        :return: str
        """
        self.knowledge = knowledge