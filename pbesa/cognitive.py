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
import uuid
import json
import pickle
import logging
import traceback
from .mas import Adm
from pydantic import BaseModel
from typing import List, Optional
from abc import ABC, abstractmethod
from pbesa.models import AIFoundry, AzureInference, AzureOpenAIInference, GPTService, ServiceProvider
from pbesa.social.dialog import (
    DialogState, imprimir_grafo, recorrer_interacciones, extraer_diccionario_nodos, 
    ActionNode, DeclarativeNode, GotoNode)
from .celulas import (celula_casos, celula_consultas, celula_saludos, celula_datos_identificables,
                      celula_generar_documento, celula_expertos, celula_pertinencia, celula_extraccion,
                      celula_evaluador, celula_respuesta, celula_conversador, celula_parafraseo)
from pbesa.social.prompts import ANALIZER_PROMPT, CLASSIFICATION_PROMPT, DERIVE_PROMPT, RECOVERY_PROMPT, ADAPT_PROMPT, SINTETIZER_PROMPT

# --------------------------------------------------------
# Define DTOs
# --------------------------------------------------------

class InteraccionDTO(BaseModel):
    id: str
    tipo: str
    texto: str
    actor: str
    isExpanded: Optional[bool] = None
    equipo: Optional[str] = None
    herramienta: Optional[str] = None
    interacciones: List["InteraccionDTO"] = []

def interaccion_serializer(interaccion):
    if isinstance(interaccion, list):
        return [interaccion_serializer(i) for i in interaccion]
    return {
        "id": interaccion["id"] if "id" in interaccion and interaccion["id"] else str(uuid.uuid4()),
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

def define_service_provider(provider, ai_service=None, substitudes = False) -> None:
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
        elif "AZURE_OPEN_AI_INFERENCE" in provider:
            substitude_1 = None 
            substitude_2 = None
            if substitudes:
                substitude_1 = AzureInference()
                substitude_2 = AzureInference()
            service = AzureOpenAIInference(substitude_1, substitude_2)
            service_provider.register("AZURE_OPEN_AI_INFERENCE", service)
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
        # system_prompt
        self.__system_prompt = None
        
    def setup_world(self):
        """ Set up model method """
        # Define role
        self.__system_prompt = "Instrucciones:\n"
        self.__system_prompt += self.__role.description
        self.__system_prompt += self.__role.objective
        self.__system_prompt += "Requisitos:\n"
        self.__system_prompt +=  self.__role.arquetype
        if self.__role.example:
            self.__system_prompt += "Ejemplos:\n"
            self.__system_prompt += self.__role.example
        
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
    
    def load_model(self, provider, config, ai_service=None, substitudes = False) -> None:
        self.__service_provider, service = define_service_provider(provider, ai_service, substitudes)
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

    def command_derive(self, command, query, max_tkns=2000) -> str | None:
        try:
            if command == "DATA_TYPE":
                return celula_datos_identificables.derive(self.__ai_service, query)
            elif command == "GENERATE_DOCUMENT":
                return celula_generar_documento.derive(self.__ai_service, query["template"], query["text"])
            elif command == "EXPERTS":
                retrieval = self.retrieval(query)
                return celula_expertos.derive(self.__ai_service, query, retrieval, max_tkns)
            return None
        except Exception as e:
            traceback.print_exc()
            return None
    
    def get_text(self, mensaje) -> str:
        if mensaje:
            mensaje_limpio = mensaje.replace("<|im_start|>user<|im_sep|>", "").replace("<|im_start|>system<|im_sep|>", "") \
                .replace("<|im_start|>", "").replace("<|im_sep|>", "").replace("<|im_end|>", "") \
                .replace("[Usuario]: ", "").replace("[Sistema]: ", "") \
                .replace("<|user|>", "").replace("<|system|>", "")
            return mensaje_limpio.strip()
        else:
            return ""
        
    def custom_derive(self, instructions, prompt) -> str:
        """ Generate method
        :return: str
        """
        try:
            instantane_memory = self.__work_memory.copy()
            instantane_memory.append({"role": "system", "content": instructions})
            instantane_memory.append({"role": "user", "content": prompt})
            text = self.__ai_service.generate(instantane_memory)
            text = self.get_text(text)
            logging.info(f"Thought: {text}")
            return text
        except Exception as e:
            traceback.print_exc()
            logging.info(f"------------RESET---------------")
            self.reset()
            return "Lo lamento, no puedo responder en este momento"
        
    def derive(self, query, max_tokens=4096, temperature=0, top_p=0.9) -> str:
        """ Generate method
        :return: str
        """
        try:
            content = self.retrieval(query)
            prompt = self.__system_prompt + (DERIVE_PROMPT % content)
            prompt += f"""
            Texto: "%s"

            Respuesta:            
            """ % query
            self.__work_memory.append({"role": "user", "content": prompt})
            logging.info("")
            logging.info("\n%s", json.dumps(self.__work_memory, indent=4))
            logging.info("")
            text = self.__ai_service.generate(self.__work_memory, max_tokens, temperature, top_p)
            text = self.get_text(text)
            logging.info(f"Thought: {text}")
            self.__work_memory = []
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
    
    def get_tool_dict(self):
        """ Get tool dict method
        :return: dict
        """
        return self.__def_tool_dict
    
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
# Define Agent Tool component
# --------------------------------------------------------

class AgentTool(ABC):
    """ Agent Tool class """

    def __init__(self, agent) -> None:
        """ Constructor method """
        self.agent = agent

    @abstractmethod
    def tool(self, request: dict) -> None:
        """ Tool method
        :param request: request
        :return: None
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
        self.__system_work_memory:list = []
        self.__evaluate_work_memory:list = []
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
        self.__deep_limit = 9
        # Define knowledge
        self.knowledge = None
        self.special_knowledge = None
        # Define point recovery
        self.__recovery = {
            "owner": "Web",
            "team": "Web",
            "performative": DialogState.START,
            "counter": 0
        }
        # Define recovery message
        self.RECOVERY_MSG = "Puede darme más detalles o reformular. O si desea puede recibir asistencia humana vía correo electrónico al ministerio@minjsuticia.gov.co"
        # Define vertices list
        self.__vertices = []
        # Define visited nodes
        self.__visited_nodes = 0
        # Define alter work memory
        self.__attemps = 1
        self.__analaizer_work_memory:list = []
        self.__sintetizer_work_memory:list = []
        # Define production rules
        self.definitions = None
        self.rules = None
        self.__q_attemps = 0

    def setup_world(self):
        """ Set up model method """
        # Define role
        instrucciones = f"Instrucciones:\n{self.__role.description}\n Tu tarea: {self.__role.objective}\n"
        requisitos = f"Requisitos:\n{self.__role.arquetype}\n"
        ejemplo = f"Ejemplo:\n{self.__role.example}\n"
        if self.knowledge:
            conocimiento = f"Conocimiento:\n{self.knowledge}\n"
        continuar = "Ahora, evalúa el siguiente caso:\n"
        prompt = instrucciones
        prompt += requisitos
        prompt += ejemplo
        if self.knowledge:
            prompt += conocimiento
        else:
            logging.warning(f"No se ha definido conocimiento para el agente: {self.id}")
        prompt += continuar
        self.__system_work_memory.append({"role": "system", "content": prompt})
        
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
        #filename = f'{self.__role.name}_grafo.pkl'
        #with open(filename, 'wb') as f:
        #    pickle.dump(grafo, f)

    def load_model(self, provider, config, ai_service=None, substitudes = False) -> None:
        self.__service_provider, service = define_service_provider(provider, ai_service, substitudes)
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
        # Reset visited nodes
        self.__visited_nodes = 0
        self.__vertices = []

    def notify(self, session_id, text):
        try:
            canales = self.state['canales']
            canal = canales.get("Webhook")
            #session_id = self.state['session_id']
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
            logging.error(f"Error: {e}")
    
    def update_conversation(self, session_manager, id_conversacion, res):
        conversation = session_manager.get_conversation(id_conversacion)
        if conversation:
            conversation['team-response'] = res
            session_manager.update_conversation(id_conversacion, conversation)
        else:
            logging.error(f"Error al actualizar la conversación: {id_conversacion}")

    def team_inquiry(self, session, team, data, operation, session_flag) -> str:
        try:
            dto = None
            canales = self.state['canales']
            canal = canales.get(team)
            session_manager = self.state['session_manager']
            if session_flag:
                # Actualiza la sesion
                session_manager.update_session(session['session_id'], {
                    'team': team,
                    'owner': team,
                    'performative': DialogState.START,
                })
                # Construye el mensaje
                dto = {
                    "data": {
                        'text': data,
                        'session_id': session['session_id'],
                    },
                }
                # Evia mensaje a los agentes remotos
                logging.info('>>>> Call remote agent: team.\n')
                response = canal.post(team.lower(), dto, timeout=300)
                if response and not response['status']:
                    logging.error(f'No se pudo establecer la comunicación con el agente remoto')
                    self.update_conversation(session_manager, session['id_conversacion'], None)
                    return None
                logging.info(f'>>>> Response: {response}')
                res = response['message']['response']
                self.update_conversation(session_manager, session['id_conversacion'], res)
                return res
            else:
                if operation and not operation == "Ninguno":
                    dto = {
                        "data": {
                            'text': data,
                            'operation': operation,
                            'id_conversacion': session['id_conversacion'],
                            'session_id': session['session_id'],
                        },
                    }
                else:
                    dto = {
                        "data": {
                            'text': data
                        },
                    }
                response = canal.post(team.lower(), dto, timeout=300)
                if response['status']:
                    logging.info(f'>>>> Response: {response}')
                    res = response['message']['response']
                    self.update_conversation(session_manager, session['id_conversacion'], res)
                    return res
                else:
                    self.update_conversation(session_manager, session['id_conversacion'], None)
                    logging.error(f'No se pudo establecer la comunicación con el agente remoto')
                    return None
            logging.info("END: team_inquiry")
        except Exception as e:
            logging.error(f"Error al consultar al equipo: {team}")
            traceback.print_exc()
            return None

    def get_text(self, mensaje) -> str:
        if mensaje:
            mensaje_limpio = mensaje.replace("<|im_start|>user<|im_sep|>", "").replace("<|im_start|>system<|im_sep|>", "") \
                .replace("<|im_start|>", "").replace("<|im_sep|>", "").replace("<|im_end|>", "") \
                .replace("[Usuario]: ", "").replace("[Sistema]: ", "") \
                .replace("<|user|>", "").replace("<|system|>", "") \
                .replace("<|assistant|>", "").replace("<|bot|>", "") \
                .replace("assistant", "")
            return mensaje_limpio.strip()
        else:
            return ""
    
    def recovery(self, session_id, query):
        try:
            logging.info("\n\n\n")
            logging.info(f"------------RECOVERY---------------")
            logging.info("\n\n\n")    
            self.__work_memory = self.__system_work_memory.copy()
            prompt = RECOVERY_PROMPT % query
            temp_work_memory = [{"role": "system", "content": prompt}]
            res = self.__ai_service.generate(temp_work_memory, max_tokens=500)
            res = self.get_text(res)
            if res and not res == "":
                return self.__recovery['owner'], self.__recovery['performative'], res, self.__recovery['team']
            else:
                logging.info(f"------------RESET---------------")
                logging.info(f"Recovery from: {self.__recovery['performative']}")
                self.reset()
                self.notify(session_id, "STOP") 
                return "Web", DialogState.START, self.RECOVERY_MSG, "Web"
        except Exception as e:
            logging.error(f"Error en la recuperación: {e}")
            msg = "Lo lamento, no puedo responder en este momento."
            return "Web", DialogState.START, msg, "Web"
        
    def stage_one_classification(self, session_id, messages, attemps, query):
        """ Stage one classification """
        res = ""
        #evaluating = True
        dicriminador = None
        logging.info(f"------------Flujo de excepcion---------------")
        self.notify(session_id, "identificando intención...")        
        logging.info(f"Intento: {attemps}") 
        
            
        self.__analaizer_work_memory:list = [{"role": "system", "content": ANALIZER_PROMPT}]
        
        
        if attemps > 1:
            saludo = "NO_SALUDO"

            self.__sintetizer_work_memory:list = [{"role": "system", "content": SINTETIZER_PROMPT}]

            cont = 0
            for message in messages:
                if message['user']:
                    self.__analaizer_work_memory.append({"role": "user", "content": message['text']})
                    
                    if cont == 0:
                        msg = f"""
                        Texto: 
                        "%s"

                        Respuesta:
                        """ % message['text']
                    else:
                        msg = message['text']

                    self.__sintetizer_work_memory.append({"role": "user", "content": msg})
                else:
                    self.__analaizer_work_memory.append({"role": "assistant", "content": message['text']})
                    self.__sintetizer_work_memory.append({"role": "assistant", "content": message['text']})

            #self.__analaizer_work_memory.append({"role": "user", "content": query})
            #self.__sintetizer_work_memory.append({"role": "user", "content": query})
        
            # Desde la seegunda iteeraccion de la
            # conversacion, se utiliza el sintentizador
            logging.info("\n\n\n--------------SINTETIZER------------------")
            logging.info("\n%s", json.dumps(self.__sintetizer_work_memory, indent=4))
            logging.info("\n\n\n")
            query = self.__ai_service.generate(self.__sintetizer_work_memory, max_tokens=50)
            res = self.get_text(query)
            query = res
            logging.info(f"[Stage-1][Sintetizer][Thought]: {query}")
        else:
            saludo = celula_saludos.derive(self.__ai_service, query, max_tkns=10)

            user_prompt = f"""
            user: {query}Texto: 
            "%s"

            Respuesta:        
            """
            self.__analaizer_work_memory.append({"role": "user", "content": user_prompt})
            

        #----------------------------------
        # Verifica si es una consulta o un caso
        caso = celula_casos.derive(self.__ai_service, query, max_tkns=10)
        consulta = celula_consultas.derive(self.__ai_service, query, max_tkns=10)
        # Verifica si es un saludo, consulta o caso

        #es_saludo = ("SALUDO" in saludo) and ("NO_PREGUNTA" in consulta) and ("NO_QUEJA_DEMANDA" in caso) and not ("NO_SALUDO" in saludo)    
        #es_consulta = ("PREGUNTA_O_SOLICITUD" in consulta) and ("NO_QUEJA_DEMANDA" in caso) and ("NO_SALUDO" in saludo) and not ("NO_PREGUNTA" in consulta)
        #es_caso = ("QUEJA_DEMANDA" in caso) and ("NO_PREGUNTA" in consulta) and ("NO_SALUDO" in saludo) and not ("NO_QUEJA_DEMANDA" in caso)
        
        es_saludo = ("SALUDO" in saludo) and not ("NO_SALUDO" in saludo)    
        es_consulta = ("PREGUNTA_O_SOLICITUD" in consulta) and not ("NO_PREGUNTA" in consulta)
        es_caso = ("QUEJA_DEMANDA" in caso) and not ("NO_QUEJA_DEMANDA" in caso)
        
        logging.info("\n------------------- Clase --------------------------")
        logging.info(f"[Stage-1]: Saludo({saludo}), Consulta({consulta}), Caso({caso})")                    
        logging.info(f"[Stage-1]: Es saludo({es_saludo}), Es consulta({es_consulta}), Es caso({es_caso})")
        logging.info("\n-----------------------------------------------------")

        eva = 0
        ambiguedad = False
        eva = 1 if es_saludo else 0
        eva += 1 if es_consulta else 0
        eva += 1 if es_caso else 0
        
        msg = "No puedo ayudarle con su consulta. Dado que no está relacionada con los servicios que presta Justifacil."

        # Verifica los casos
        if eva > 0 and eva < 3:
            logging.info("[Stage-1]: Discriminador encontrado")
            
            # Casos identificables
            if es_saludo and not es_consulta and not es_caso:
                dicriminador = "saluda"
            elif es_consulta and not es_saludo and not es_caso:
                dicriminador = "consulta"
                per_res = celula_pertinencia.derive(self.__ai_service, query, max_tkns=10)
                if per_res and not per_res == "":
                    if "ABSURDO" in per_res:
                        dicriminador = None
                        res = msg
            elif es_caso and not es_saludo and not es_consulta:
                dicriminador = "caso"
                per_res = celula_pertinencia.derive(self.__ai_service, query, max_tkns=10)
                if per_res and not per_res == "":
                    if "ABSURDO" in per_res:
                        dicriminador = None
                        res = msg

            # Casos ambiguos con saludo
            elif es_saludo and es_consulta and not es_caso:
                dicriminador = "consulta"
                per_res = celula_pertinencia.derive(self.__ai_service, query, max_tkns=10)
                if per_res and not per_res == "":
                    if "ABSURDO" in per_res:
                        dicriminador = None
                        res = msg
            elif es_saludo and es_caso and not es_consulta:
                dicriminador = "caso"
                per_res = celula_pertinencia.derive(self.__ai_service, query, max_tkns=10)
                if per_res and not per_res == "":
                    if "ABSURDO" in per_res:
                        dicriminador = None
                        res = msg

            # Casos ambiguos con consulta y caso
            elif es_consulta and es_caso and not es_saludo:
                res = "¿Desea que le ayude con una consulta o una demanda?"
            else:
                ambiguedad = True
                per_res = celula_pertinencia.derive(self.__ai_service, query, max_tkns=10)
                if per_res and not per_res == "":
                    if "ABSURDO" in per_res:
                        dicriminador = None
                        res = msg
                        ambiguedad = False

            if dicriminador:
                self.notify(session_id, f"primera fase se identifica: {dicriminador}.")
                res = query
        else:
            ambiguedad = True

        if ambiguedad:    
            logging.info("[Stage-1]: Respuesta con ambiguedad")
            self.notify(session_id, "identificando ambiguedad...")
            logging.info("\n\n\n--------------ANALIZER------------------")
            logging.info("\n%s", json.dumps(self.__analaizer_work_memory, indent=4))
            logging.info("------------------------------------------\n\n\n")
            res = self.__ai_service.generate(self.__analaizer_work_memory, max_tokens=50)
            logging.info(f"[Stage-1][Thought]: {res}")
            self.__analaizer_work_memory.append({"role": "assistant", "content": res})                
            self.__sintetizer_work_memory.append({"role": "assistant", "content": res})
        #----------------------------------

        return dicriminador, res

    def get_node(self, performative):
        """ Get node method
        :param performative: performative
        :return: Node
        """
        if performative in self.__dfa:
            return self.__dfa[performative]
        else:
            logging.error(f"Performativa {performative} no encontrada en el DFA")
            return None
        
    def transition(self, session, owner, dialog_state, query, team_source=False) -> str:
        try:
            res = ""
            logging.info(f"TOPTQ: {owner} - {dialog_state} - {team_source} - {query}")
            # Actualiza la memoria de trabajo
            if len(self.__work_memory) == 0:
                self.__work_memory = self.__system_work_memory.copy()
            # Punto de restauración
            counter = (self.__recovery['counter'] + 1) if self.__recovery['performative'] == dialog_state else self.__recovery['counter']
            self.__recovery = {
                "owner": owner,
                "team": owner,
                "performative": dialog_state,
                "counter": counter
            }
            logging.info(f"Recovery attemps: {self.__recovery['counter']}")
            # Verifica si se ha alcanzado el límite de recuperación
            if self.__recovery['counter'] <= 33 and self.__visited_nodes <= 33:                    
                select_node = None
                #------------------------------
                # Flujode de excepcion
                #------------------------------
                if owner == "Web" and dialog_state == DialogState.START:
                    logging.info(f"TOPTQ: {owner} - {dialog_state} - {team_source} - {query}")
                    session_manager = self.state['session_manager']        
                    conversation = session_manager.get_conversation(session['id_conversacion'])
                    attemps = conversation.get('attemps', 1)            
                    dicriminador, res = self.stage_one_classification(session['session_id'], conversation['messages'], attemps, query)
                    conversation['attemps'] = attemps + 1
                    session_manager.update_conversation(session['id_conversacion'], conversation)
                    logging.info(f"Discriminador: {dicriminador}")
                    # Limpia la memoria de trabajo
                    # Para que el agente la utilice en
                    # Otra conversacion
                    self.__analaizer_work_memory:list = []
                    self.__sintetizer_work_memory:list = []
                    if not dicriminador:
                        # Una nueva iteración de analisis
                        logging.info(f"------------RESET---------------")
                        logging.info(f"Recovery from: {self.__recovery['performative']}")
                        self.reset()
                        self.notify(session['session_id'], "STOP") 
                        return "Web", DialogState.START, res, "Web"
                    query = res                
                    #--------------------------
                    # Obtiene los hijos del 
                    # nodo
                    children = None
                    node = self.__dfa[dialog_state]
                    if not isinstance(node, list):
                        children = node.children
                    else:
                        # Es una lista de nodos
                        children = node
                    #--------------------------
                    # Flujo de selección                
                    if children and len(children)> 1:
                        logging.info(f"--> Más de una opción.")
                        options = ""
                        cont = 1
                        for item in children:
                            if dicriminador in item.text:
                                select_node = item
                                break
                else:                    
                    #------------------------------
                    # Fulo normal
                    #------------------------------    
                    logging.info("Flujo normal")    
                    self.notify(session['session_id'], "identificando concepto...")
                    #----------------------
                    # Verifica que exista 
                    # la performativa
                    if not dialog_state in self.__dfa:
                        self.notify(session['session_id'], "concepto no encontrado")
                        return self.recovery(session['session_id'], query)
                    # Performativa encontrada
                    children = None
                    self.notify(session['session_id'], "concepto encontrado")
                    #----------------------
                    # Obtiene los hijos del
                    #  nodo
                    node = self.__dfa[dialog_state]
                    if not isinstance(node, list):
                        children = node.children
                    else:
                        # Es una lista de nodos
                        children = node
                    #----------------------
                    # Flujo de selección
                    select_node = None
                    if children and len(children)> 1:
                        logging.info(f"--> Más de una opción.")
                        options = ""
                        cont = 1
                        for item in children:
                            options += f"{cont}) {item.text}\n"
                            cont += 1
                        prompt = CLASSIFICATION_PROMPT % options
                        logging.info(f"Query: {query},\n Options:\n{options}")
                        self.__meta_work_memory.append({"role": "system", "content": prompt})
                        user_prompt = f"""
                        Texto: "%s"

                        Respuesta:
                        """ % query
                        self.__meta_work_memory.append({"role": "user", "content": user_prompt})
                        res = self.__ai_service.generate(self.__meta_work_memory, max_tokens=10)
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
                        logging.info("???> Es un nodo terminal o iniciador")
                        logging.warning(f"???> Es un nodo terminal o iniciador: {node}")
                        logging.warning(f"???> Es un nodo terminal o iniciador: {node}")
                        return self.recovery(session['session_id'], query)
                
                # Verifica si el nodo fue seleccionado
                if not select_node:
                    logging.warning(f"???> No se seleccionó ningún nodo")
                    logging.info(f"------------RESET---------------")
                    self.notify(session['session_id'], "STOP")
                    self.reset()
                    return "Web", DialogState.START, self.RECOVERY_MSG, "Web"

                #--------------------------
                # Verifica si es un nodo
                # que ya fue recorrido
                if select_node.performative in self.__vertices:
                    logging.info(f"-> nodo ya recorrido: {select_node.text}")
                    self.__visited_nodes += 1
                else:
                    logging.info(f"-> nodo no recorrido: {select_node.text}")
                    self.__visited_nodes = 0
                    # Maraca el nodo como visitado
                    self.__vertices.append(select_node.performative)
                #---------------------------
                # Verifica si el nodo es un
                # nodo de salto
                if isinstance(select_node, GotoNode):
                    logging.info(f"-> node de salto: {select_node.text}")
                    performative = select_node.text.replace("Salta a:", "").strip()
                    select_node = self.__dfa[performative]
                    logging.info(f"-> Salto: {select_node.text}, performativa: {select_node.performative}")
                #---------------------------
                # Efectua transicion
                if select_node:
                    res = select_node.text
                    if select_node.children and len(select_node.children) > 0:
                        res = select_node.children[0].text
                        node = select_node.children[0]
                    else:
                        logging.info(f"-> El nodo de transición es terminal: {select_node.text}")
                        res = select_node.text
                        node = select_node
                else:
                    logging.info(f"-> !!!!!!!!!!!!!! Concepto no encontrado !!!!!!!!!!!!!!")
                    if isinstance(node, list) and len(node) > 0:
                        node = node[0]
                    else:
                        logging.info(f"-> !!!!!!!!!!!!!! Concepto no encontrado ????????????????")
                        return self.recovery(session['session_id'], query)
                logging.info(f"Flujo normal: {res}")
                #---------------------------
                # Verifica si el nuevo nodo 
                # es un nodo de salto
                if isinstance(node, GotoNode):
                    logging.info(f"-> node de salto: {node.text}")
                    performative = node.text.replace("Salta a:", "").strip()
                    node = self.__dfa[performative]
                    logging.info(f"-> Salto: {node.text}, performativa: {node.performative}")
                #---------------------------
                # Actualiza la memoria de 
                # trabajo
                if team_source:
                    pass
                    #self.__work_memory.append({"role": "system", "content": res})
                    #logging.info(f"-> Team source Actualiza WM assistant: {res}")
                else:
                    self.__work_memory.append({"role": "user", "content": query})
                    #self.__work_memory.append({"role": "user", "content": res})
                    logging.info(f"-> User source Actualiza WM user: {query}")
                    #logging.info(f"-> Actualiza r-WM: {res}")
                #---------------------------
                # Efectua inferencia
                new_owner, new_dialog_state, res, team = self.do_transition(session, owner, node, query)
                if res and not res == "ERROR" and isinstance(res, str):
                    res = self.get_text(res)
                self.__work_memory = self.__system_work_memory.copy()
                return new_owner, new_dialog_state, res, team
            else:
                logging.info(f"------------RESET---------------")
                self.notify(session['session_id'], "STOP")
                self.reset()
                return "Web", DialogState.START, self.RECOVERY_MSG, "Web"
            logging.info("END: do_transition")
        except Exception as e:
            traceback.print_exc()
            logging.info(f"------------RESET---------------")
            self.reset()
            self.notify(session['session_id'], "STOP")
            return owner, DialogState.START, "Lo lamento, no puedo responder en este momento", owner

    def chek_user_interaction(self, children):
        """ Check user interaction method
        :param children: children
        :param query: query
        :return: bool
        """
        if children and len(children) > 0:    
            for item in children:
                if item.actor == "Des. Usuario" or item.actor == "Salto":
                    return True
        return False

    def do_transition(self, session, owner, node, query) -> str:
        """ Generate method
        :return: str
        """
        try:
            if isinstance(node, ActionNode):
                self.notify(session['session_id'], "realizando acción...")
                #------------------------------
                # Accion
                #------------------------------
                logging.info(f"[Node]:[Action]: {node.action}")
                if node.tool and not node.tool == "Ninguno":
                    self.notify(session['session_id'], "aplicando herramienta...")
                    logging.info(f"[Node]:[Action]:[Tool]: {node.tool}")
                    res = query
                    if "consulta" in node.text.lower():
                        logging.info(f"[Node]:[Action]:[Tool]:[Consulta]: {query}")
                    else:
                        logging.info("[Node]:[Action]:[Tool]:[Inferencia]:")
                        logging.info("-----")
                        logging.info("\n%s", json.dumps(self.__work_memory, indent=4))
                        logging.info("-----")         
                        res = self.__ai_service.generate(self.__work_memory, max_tokens=100)
                        logging.info(f"[Node]:[Action]:[Tool]:[Thought]: {res}")
                        res = self.get_text(res)
                    # Check if res is empty
                    if not res or res == "":
                        self.notify(session['session_id'], "no pude hacer uso de la herramienta")
                        return self.recovery(session['session_id'], query)
                    logging.info(f"[Node]:[Action]:[Tool]:[Envia]: {res}")
                    res = self.team_inquiry(session, node.team, res, node.tool, False)
                    logging.info(f"[Node]:[Action]:[Tool]:[Respuesta]: {res}")
                    if res and not res == "ERROR" and not isinstance(res, str):
                        logging.info("[Node]:[Action]:[Tool]: COMMANDO")
                        self.reset()
                        self.notify(session['session_id'], "STOP")
                        return "Web", DialogState.START, res, "Web"
                    logging.info("[Node]:[Action]:[Tool]: CONTINUA-INFERENCIA")
                else:
                    self.notify(session['session_id'], "realizando llamada...")
                    #------------------------------
                    # Lllamada
                    #------------------------------
                    logging.info(f"[Node]:[Action]:[Call]: {node.team}")
                    # Verifica si el nodo es termianl ya que significa
                    # que el dialogo cambia de agente
                    if node.is_terminal:
                        logging.info(f"[Node]:[Action]:[Call]:[Terminal]: {node.text}")
                        self.__work_memory.append({"role": "system", "content": node.text})                        
                        res = query
                        if "consulta" in node.text.lower():
                            logging.info(f"[Node]:[Action]:[Call]:[Terminal]:[Consulta] {query}")
                            if "especialistas" in node.text.lower():
                                self.notify(session['session_id'], "consultando especialistas...")
                                session_manager = self.state['session_manager']
                                conversation = session_manager.get_conversation(session['id_conversacion'])
                                if 'team-response' in conversation:
                                    res = conversation['team-response']
                                else:
                                    res = "Lo lamento, no puedo responder en este momento"
                                    logging.info("[Node]:[Action]:[Call]:[Terminal]:[Consulta]: No hay respuesta de equipo")
                                logging.info("[Node]:[Action]:[Call]:[Terminal]:[Consulta]: Especialistas")                            
                        else:
                            logging.info("[Node]:[Action]:[Call]:[Terminal]:[Inferencia]:")
                            logging.info("-----")
                            logging.info("\n%s", json.dumps(self.__work_memory, indent=4))
                            logging.info("-----")
                            res = self.__ai_service.generate(self.__work_memory, max_tokens=1000)
                            res = self.get_text(res)
                            self.__work_memory.append({"role": "assistant", "content": res})
                            logging.info(f"[Node]:[Action]:[Call]:[Terminal]:[Thought]: {res}")
                            # Check if res is empty
                            if not res or res == "":
                                return self.recovery(session['session_id'], query)
                        #------------------
                        # Envia la 
                        # respuesta 
                        # al equipo
                        #------------------
                        logging.info(f"[Node]:[Action]:[Call]:[Terminal]:[Envia]: {res}")
                        res = self.team_inquiry(session, node.team, res, None, True)
                        logging.info(f"[Node]:[Action]:[Call]:[Terminal]:[Respuesta]: {res}")
                        if res and not res == "ERROR" and not res == "":
                            logging.info(f"------------RESET---------------")
                            self.reset()
                            self.notify(session['session_id'], "STOP")
                            return node.team, DialogState.START, res, node.team
                        else:
                            return self.recovery(session['session_id'], query)
                    else:
                        logging.info(f"[Node]:[Action]:[Call]:[Continua]: {node.text}")
                        self.__work_memory.append({"role": "system", "content": node.text})   
                        res = query
                        if "consulta" in node.text.lower():
                            logging.info(f"[Node]:[Action]:[Call]:[Continua]:[Consulta] {query}")
                            if "expertos" in node.text.lower():
                                self.notify(session['session_id'], "consultando expertos...")
                                session_manager = self.state['session_manager']
                                conversation = session_manager.get_conversation(session['id_conversacion'])
                                conversation['case'] = query
                                session_manager.update_conversation(session['id_conversacion'], conversation)
                                logging.info("[Node]:[Action]:[Call]:[Continua]:[Consulta]: Caso almacenado")
                        else:
                            logging.info("[Node]:[Action]:[Call]:[Continua]:[Inferencia]:")
                            logging.info("-----")
                            logging.info("\n%s", json.dumps(self.__work_memory, indent=4))
                            logging.info("-----")
                            res = self.get_text(res)
                            self.__work_memory.append({"role": "assistant", "content": res})
                            logging.info(f"[Node]:[Action]:[Call]:[Continua]:[Thought]: {res}")
                            # Check if res is empty
                            if not res or res == "":
                                return self.recovery(session['session_id'], query)
                        logging.info(f"[Node]:[Action]:[Call]:[Continua]:[Envia]: {res}")                        
                        res = self.team_inquiry(session, node.team, res, node.tool, False)
                        logging.info(f"[Node]:[Action]:[Call]:[Continua]:[Respuesta]: {res}")
                        logging.info("[Node]:[Action]:[Call]:[Continua]: CONTINUA-INFERENCIA")

                # Adiciona el texto al work memory
                if res and not res == "ERROR" and not res == "":
                    logging.info(f"-> Adicion WM node team -> text: {res}")
                    self.__work_memory.append({"role": "assistant", "content": res})
                else:
                    return self.recovery(session['session_id'], query)
                logging.info("#########> Procesa respuesta del equipo en profundidad")
                # Verifica si se alcanzó el límite de profundidad
                self.__deep_count += 1
                if self.__deep_count < self.__deep_limit:
                    self.notify(session['session_id'], "efectuando inferencia en profundidad")
                    return self.transition(session, owner, node.performative, res, True)
                else:
                    self.notify(session['session_id'], f"se alcanzó el límite de profundidad: {self.__deep_count}")
                    self.__deep_count = 0
                    logging.info("-> node team -> deep limit")
                    logging.info(f"------------RESET---------------")
                    self.notify(session['session_id'], "STOP")
                    self.reset()
                    return "Web", DialogState.START, self.RECOVERY_MSG, "Web"
            else:
                self.notify(session['session_id'], "efectuando inferencia...")
                logging.info(f"[Inferencia]:[node]: {node.text}")

                if "Evaluar: produccion-" in node.text:
                    data = {"text": ""}
                    for item in reversed(self.__work_memory):
                        if item['role'] == 'user':
                            data['text'] = item['content']
                            break
                    self.notify(session['session_id'], f"continuando díalogo paso a usuario")                    
                    res = self.evaluate(session, data['text'])                    
                    if 'Lo lamento' in res:
                        logging.info(f"------------RESET---------------")
                        self.reset()
                        self.notify(session['session_id'], "STOP")
                        return "Web", DialogState.START, res, "Web"                    
                    return owner, node.performative, res, owner

                self.__work_memory.append({"role": "system", "content": node.text})
                logging.info(f"=> !!!!: {query}")
                logging.info("-----")
                logging.info("\n%s", json.dumps(self.__work_memory, indent=4))
                logging.info("-----")
                res = self.__ai_service.generate(self.__work_memory, max_tokens=1000)
                res = self.get_text(res)
                logging.info(f"[Inferencia]:[Thought]:[DEEP]: {res}")
                # Check if res is empty
                if not res or res == "" or res == "ERROR":
                    return self.recovery(session['session_id'], query)
                self.__work_memory.append({"role": "assistant", "content": res})                
                new_dialog_state = node.performative
                if not node.is_terminal:
                    # Verifica recursion
                    if not self.chek_user_interaction(node.children):
                        if self.__visited_nodes > 3:
                            self.__visited_nodes = 0
                            logging.info(f"[Inferencia]:[Recursion]: Deep limit")
                            #return self.recovery(session['session_id'], "Lo lamento, no puedo responder en este momento")
                            logging.info(f"------------RESET---------------")
                            self.reset()
                            self.notify(session['session_id'], "STOP")
                            res = "Lo lamento, no puedo responder en este momento. Intentelo más tarde desde el inicio."
                            return "Web", DialogState.START, res, "Web"
                        logging.info(f"[Inferencia]:[Recursion]:[Performativa]: {node.performative}")
                        self.notify(session['session_id'], "efectuando inferencia en profundidad")
                        #return self.do_transition(session, owner, node, query)
                        return self.transition(session, owner, new_dialog_state, res, True)
                    self.notify(session['session_id'], f"continuando díalogo paso a usuario")
                    return owner, new_dialog_state, res, owner
                self.notify(session['session_id'], f"finalizando díalogo de inferencia")
                logging.info(f"Tipe node: {type(node)}")
                logging.info(f"$$$> new_owner: {owner} new_dialog_state: {new_dialog_state}")
                #logging.info(f"------------RESET---------------")
                #self.reset()      
                self.notify(session['session_id'], "STOP")
                return "Web", DialogState.START, res, "Web"
            logging.info("END: do_transition")
        except Exception as e:
            traceback.print_exc()
            logging.info(f"------------RESET---------------")
            self.reset()
            self.notify(session['session_id'], "STOP")
            return owner, DialogState.START, "Lo lamento, no puedo responder en este momento", owner

    def set_knowledge(self, knowledge) -> str:
        """ Set knowledge method
        :param query: query
        :return: str
        """
        self.knowledge = knowledge
    
    def set_special_knowledge(self, knowledge) -> str:
        """ Set knowledge method
        :param query: query
        :return: str
        """
        self.special_knowledge = knowledge

    def set_production_knowledge(self, definitions, rules) -> str:
        """ Set knowledge method
        :param query: query
        :return: str
        """
        self.definitions = definitions
        self.rules = rules

    def adapt(self, data, profile) -> any:
        """ Adapt method
        :param data: data
        :return: str
        """
        try:
            logging.info(f"Adaptando respuesta: {data}")
            # Get text
            text = ""
            if isinstance(data, str):
                text = data
            elif isinstance(data, dict):
                if 'command' in data:
                    logging.info(f"Es un comando.")
                    return data
                text = data['dto']['text'] if data and 'dto' in data and data['dto']['text'] is not None else ''
            else:
                raise ValueError("Respuesta mal formada")
            # Adapt the data
            tmp_work_memory = []
            prompt  = ADAPT_PROMPT % profile
            tmp_work_memory.append({"role": "system", "content": prompt})
            user_propmt = f"""
            Texto: "%s"

            Respuesta:
            """
            tmp_work_memory.append({"role": "user", "content": user_propmt % text})
            res = self.__ai_service.generate(tmp_work_memory)
            res = self.get_text(res)
            logging.info(f"Respuesta adaptada: {res}")
            if not res or res == "":
                res = text
                logging.warning(f"No se pudo adaptar la respuesta.")
            return res
        except Exception as e:
            logging.error(f"Error al adaptar el dato: {data}")
            logging.error(e)
            return None

    def command_derive(self, command, query, max_tkns=2000) -> str | None:
        # data_extraction_cel
        if command == "IDENTIFICAR_VALORES":
            return celula_datos_identificables.derive(self.__ai_service, query, max_tkns=max_tkns)
        if command == "EXTRAER_DATOS":
            return celula_extraccion.derive(self.__ai_service, query, max_tkns=max_tkns)
        if command == "VERIFICAR_CONSULTA":
            return celula_consultas.derive(self.__ai_service, query, max_tkns=10)
        if command == "EVALUAR_CONSULTA":
            return celula_parafraseo.derive(self.__ai_service, self.special_knowledge, query, max_tkns=max_tkns)
        return None
    
    def parse_conversation(self) -> str:
        res = ""
        if self.__evaluate_work_memory and len(self.__evaluate_work_memory) > 0:
            for item in self.__evaluate_work_memory:
                if item['role'] == 'user':
                    res += f"usuario:\n{item['content']}\n"
                elif item['role'] == 'assistant':
                    res += f"asistente:\n{item['content']}\n"
        else:
            logging.warning("No hay memoria de trabajo para parsear la conversación.")
        return res.strip()

    def evaluate(self, session, query) -> str:
        try:
            self.__evaluate_work_memory.append({"role": "user", "content": query})            
            # Evalua la conversación
            logging.info(f"Evaluando consulta: {query}")
            self.notify(session, "evaluando consulta...")
            for _ in range(3):
                logging.info(f"Intento de evaluación: {_+1}")
                conversacion = self.parse_conversation()
                result = celula_evaluador.derive(self.__ai_service, self.definitions, self.rules, conversacion, max_tkns=10)
                if result and not result == "":                           
                    if "APLICA" in result:
                        self.notify(session, "aplicando consulta...")
                        self.__evaluate_work_memory = []
                        return "Considero que el caso aplica. ¿Desea continuar con el trámite? Responda Sí o No."
                    elif "RECHAZO" in result:
                        self.notify(session, "rechazando consulta...")
                        res_rechazo = celula_respuesta.derive(self.__ai_service, self.definitions, self.rules, conversacion, max_tkns=164)
                        if res_rechazo and not res_rechazo == "":
                            if "SIN_COMENTARIOS" in res_rechazo:
                                continue
                            self.__evaluate_work_memory = []
                            return res_rechazo
                        self.__evaluate_work_memory = []
                        return "Considero que el caso no aplica. ¿Desea continuar con el trámite? Responda Sí o No."
                    elif "PREGUNTAR" in result:
                        self.__q_attemps += 1
                        if self.__q_attemps > 3:
                            logging.error("Se alcanzó el límite de intentos de pregunta.")
                            self.__q_attemps = 0
                            self.__evaluate_work_memory = []
                            return "Considero que el caso no aplica. ¿Desea continuar con el trámite? Responda Sí o No."
                        self.notify(session, "preguntando al usuario...")
                        conversacion = self.parse_conversation()
                        res = celula_conversador.derive(self.__ai_service, self.definitions, self.rules, conversacion, max_tkns=200)
                        if not res and res == "":                            
                            res = "Lo lamento, no puedo responder en este momento."
                        res = res.replace("*", " ").strip()
                        if 'Formulación de la pregunta' in res:
                            res = res.split('Formulación de la pregunta: ')[1].strip()
                        elif 'Chain of Thought' in res:
                            self.__q_attemps = 0
                            return "Considero que el caso no aplica. ¿Desea continuar con el trámite? Responda Sí o No."
                        self.__evaluate_work_memory.append({"role": "assistant", "content": res})
                        return res
                    else:
                        logging.warning(f"Resultado inesperado: {result}")
                        self.__evaluate_work_memory = []
                        return "Lo lamento, no puedo responder en este momento."
                else:
                    logging.warning(f"Resultado de evaluación vacío o nulo: {result}")
                    if _ < 2:
                        logging.info("Reintentando evaluación...")
                        continue
                    else:
                        self.__evaluate_work_memory = []
                        logging.error("No se pudo evaluar la consulta después de 3 intentos.")
                        return "Lo lamento, no puedo responder en este momento."
            self.__evaluate_work_memory = []
            return "Lo lamento, no puedo responder en este momento."
        except Exception as e:
            logging.error(f"Error al evaluar la consulta: {query}")
            logging.error(e)
            return "Lo lamento, no puedo responder en este momento."
        
# --------------------------------------------------------
# Define Special Dispatch
# --------------------------------------------------------

class SpecialDispatch():
    """ Special dispatch """

    def __init__(self) -> None:
        """ Constructor method """
        self.model:any = None
        self.model_conf:dict = None
        self.__meta_work_memory:list = []
        # Define AI service
        self.__ai_service = None
        self.knowledge = None
        # Define options dictionary
        self.__options_dict = {}
        # Reference of ADM
        self.adm = Adm()

    def load_model(self, provider, config, ai_service=None, substitudes = False) -> None:
        self.__service_provider, service = define_service_provider(provider, ai_service, substitudes)
        service.setup(config)
        self.__ai_service = service
        # Setup options dictionary
        agent_list = self.get_agent_list()
        # Get the agent asocciated with the data.
        for agent_id in agent_list:
            agent = self.adm.get_agent(agent_id)
            # Check if the agent is instance of Dialog
            if isinstance(agent, Dialog):
                # Get the role
                role = agent.get_role()
                self.__options_dict[agent_id] = role.description
        # Log
        #logging.info(f"Agentes disponibles: {self.__options_dict.keys()}")
    
    def get_text(self, mensaje) -> str:
        if mensaje:
            mensaje_limpio = mensaje.replace("<|im_start|>user<|im_sep|>", "").replace("<|im_start|>system<|im_sep|>", "") \
                .replace("<|im_start|>", "").replace("<|im_sep|>", "").replace("<|im_end|>", "") \
                .replace("[Usuario]: ", "").replace("[Sistema]: ", "") \
                .replace("<|user|>", "").replace("<|system|>", "")
            return mensaje_limpio.strip()
        else:
            return ""
    
    @abstractmethod
    def retrieval(self, query) -> str:
        """ Set retrieval method
        :param query: query
        :return: str
        """
        pass
    
    @abstractmethod
    def kusto_connection(self):
        pass

    @abstractmethod
    def kusto_open(self) -> bool:
        pass

    def special_dispatch(self, data: any) -> None:
        """ 
        Response.
        @param data Event data 
        """
        response = None
        if data and not data['dto']['session']['team'] == "Funcionalidades":
            logging.info("Despachando por descripcion...")
            options = ""
            cont = 1
            agent_options = {}
            for agent, item in self.__options_dict.items():
                agent_options[cont] = agent
                options += f"{cont}) {item}\n"
                cont += 1
            query = data['dto']['text'] if data and 'dto' in data and data['dto']['text'] is not None else ''
            prompt = CLASSIFICATION_PROMPT % options
            logging.info(f"Query: {query},\n Options:\n{options}")
            self.__meta_work_memory.append({"role": "system", "content": prompt})
            

            user_prompt = f"""
            Texto: "%s"

            Respuesta:
            """ % query
            self.__meta_work_memory.append({"role": "user", "content": user_prompt})
            
            res = self.__ai_service.generate(self.__meta_work_memory, max_tokens=10)
            logging.info(f"Thought: {res}")
            self.__meta_work_memory = []
            res = self.get_text(res)
            select_agent = None
            compare = re.findall(r'\d+', res)
            print(f"Compare: {compare}")
            if len(compare) > 0:
                compare = compare[0]
            else:
                compare = res
            compare = compare.strip()
            print(f"Compare: {compare}")
            for option in range(1, cont+1):
                print(f"Option: {option} - Compare: {compare}")
                if str(option) == compare:                
                    select_agent = agent_options[option]
                    logging.info(f"Descripcion del agente seleccionado: {select_agent}")
                    break
            if not select_agent:
                logging.info("=> No se seleccionó ningun agente")
            return select_agent, response
        else:
            logging.info("Despachando por descripcion...")
            options = ""
            cont = 1

            selection_options = {}

            agent_options = {}
            for agent, item in self.__options_dict.items():
                agent_options[cont] = agent
                options += f"{cont}) {item}\n"
                cont += 1
                selection_options[agent] = 0

            query = data['dto']['text'] if data and 'dto' in data and data['dto']['text'] is not None else ''
            prompt = CLASSIFICATION_PROMPT % options
            logging.info(f"Query: {query},\n Options:\n{options}")
            self.__meta_work_memory.append({"role": "system", "content": prompt})
            

            user_prompt = f"""
            Texto: "%s"

            Respuesta:
            """ % query
            self.__meta_work_memory.append({"role": "user", "content": user_prompt})

            self.kusto_open()

            attemps = 1
            exit = False
            while attemps <= 3 and not exit:
                logging.info(f"Intento de selección de agente: {attemps}")

                res = self.__ai_service.generate(self.__meta_work_memory, max_tokens=10)
                logging.info(f"Thought: {res}")
                
                res = self.get_text(res)
                select_agent = None
                compare = re.findall(r'\d+', res)
                print(f"Compare: {compare}")
                if len(compare) > 0:
                    compare = compare[0]
                else:
                    compare = res
                compare = compare.strip()
                print(f"Compare: {compare}")
                for option in range(1, cont+1):
                    print(f"Option: {option} - Compare: {compare}")
                    if str(option) == compare:                
                        select_agent = agent_options[option]
                        logging.info(f"Descripcion del agente seleccionado: {select_agent}")
                        break
                if not select_agent:
                    logging.info("=> No se seleccionó ningun agente")

                major_id, response, score = self.retrieval(query)
                major_id_split = major_id.split("_")
                major_id = major_id_split[0] if len(major_id_split) > 0 else major_id
                major_id_split = major_id.split("-")
                major_id = major_id_split[0] if len(major_id_split) > 0 else major_id

                compare_llm = 0
                compare_index = 0
                idex_result = None

                # Check if the selected agent is in the retrieval response
                if major_id and major_id in select_agent:
                    logging.info(f"Se seleccionó el agente: {select_agent} con score: {score}")
                    exit = True
                    continue
                else:
                    for ag in selection_options:
                        if select_agent and select_agent in ag:
                            selection_options[ag] += 1
                            compare_llm += 1 
                        if major_id and major_id in ag:
                            selection_options[ag] += 1
                            compare_index += 1
                            idex_result = ag

                attemps += 1

            if attemps > 3:
                logging.info("No se pudo seleccionar un agente, identificando el agente con mayor score...")
                
                if compare_llm == compare_index:
                    logging.warning("Dando prioridad al resultado del indice")
                    select_agent = idex_result
                else:
                    logging.info("Evaluando los scores de los agentes...")
                    major_id = ""
                    max_score = 0
                    for ag, score in selection_options.items():
                        if score > max_score:
                            max_score = score
                            major_id = ag
                    if major_id:
                        select_agent = major_id
                        logging.info(f"Se seleccionó el agente: {select_agent} con score: {max_score}") 

            self.kusto_close()
            self.__meta_work_memory = []
            return select_agent, response
