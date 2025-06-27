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
from openai import AzureOpenAI
from abc import ABC, abstractmethod
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
import time
from openai import AzureOpenAI, RateLimitError, APIStatusError


# --------------------------------------------------------
# Define classes
# --------------------------------------------------------

class AIService(ABC):
    """Abstract class for AI services."""

    def __init__(self) -> None:
        self.model:any = None
        self.model_conf:dict = None
        self.substitude_1_model:any = None
        self.substitude_2_model:any = None
        
    @abstractmethod
    def setup(self, config: dict) -> None:
        """Method to setup the AI service."""
        raise NotImplementedError("Method 'setup' must be implemented.")

    @abstractmethod
    def generate(self, work_memory, max_tokens=4096, temperature=0, top_p=0.9) -> str:
        """Method to generate a response based on user input."""
        raise NotImplementedError("Method 'setup' must be implemented.")

class GPTService(AIService):

    def __init__(self) -> None:
        super().__init__()

    def setup(self, config: dict, work_memory) -> None:
        try:
            self.model:any = config['model']
            self.model_conf:dict = config
            self.__work_memory:list = work_memory
        except Exception as e:
            raise Exception("Could not setup GPTService: check the configuration.")

    def generate(self) -> str:
        """ Generate method
        :return: str
        """
        try:
            # Genera texto con OpenAI.
            self.model.api_key = self.model_conf['API_KEY']
            engine = self.model_conf['OPENAI_ENGINE']
            response = self.model.ChatCompletion.create(
                model = engine,
                messages = self.__work_memory
            )
            # Verifica si se obtuvo respuesta.
            if response['choices'][0]['finish_reason'] == 'completed' or response['choices'][0]['finish_reason'] == 'stop':
                res = response['choices'][0]['message']['content']
                try:
                    if not res or res == 'null' or res == 'N/A' or 'N/A' in res:
                        #self.log.warning("OpenAI response not completed", extra={'log_data': {'gpt_response': response}})
                        logging.info("OpenAI response not completed")
                        return None
                    #self.log.info("OpenAI response completed", extra={'log_data': {'gpt_response': response}})
                    logging.info("OpenAI response completed")
                    self.__work_memory.append({"role": "assistant", "content": res})
                    return res
                except:
                    #self.log.warning("OpenAI response not completed", extra={'log_data': {'gpt_response': response}})
                    logging.info("OpenAI response not completed")
                    return None
            else:
                #self.log.warning("OpenAI response not completed", extra={'log_data': {'gpt_response': response}})
                logging.info("OpenAI response not completed")
                return None
        except Exception as e:
            trace_err = traceback.format_exc()
            err = str(e) + " - " + trace_err
            logging.info(err)
            return None

class AIFoundry(AIService):

    def __init__(self) -> None:
        super().__init__()

    def setup(self, config: dict, work_memory) -> None:        
        self.model_conf:dict = config
        self.__work_memory:list = work_memory
        project = AIProjectClient.from_connection_string(
            conn_str=config['PROJECT_CONNECTION_STRING'], credential=DefaultAzureCredential()
        )
        self.model:any = project.inference.get_chat_completions_client()

    def generate(self) -> str:
        response = self.model.complete(
            model=self.model_conf['AIFOUNDRY_MODEL'],
            messages=self.__work_memory,
        )
        return response.choices[0].message.content

class AzureInference(AIService):

    def __init__(self) -> None:
        super().__init__()
        self.max_tokens = 2000
        self.deployment = "Llama-3.3-70B-Instruct"

    def setup(self, config: dict, substitude=None) -> None:        
        self.model_conf:dict = config
        self.model:any = ChatCompletionsClient(
            endpoint=config['AZURE_GENERAL_INFERENCE_SDK_ENDPOINT'], 
            credential=AzureKeyCredential(config['AZURE_INFERENCE_SDK_KEY'])
        )
        self.max_tokens = self.model_conf['MAX_TOKENS']
        if substitude:
            self.deployment = substitude
        else:
            self.deployment = self.model_conf['DEPLOYMENT_NAME']

    def generate(self, work_memory, max_tokens=2000, temperature=0, top_p=0.9) -> str:
        again = False
        try:
            response = self.model.complete(
                messages= work_memory,
                model= self.deployment,
                max_tokens= max_tokens
            )
            res = response.choices[0].message.content
            if not res or res == "" or res == "ERROR":
                again = True
            else:
                return res
        except Exception as e:
            # Maneja otros errores
            again = True
            trace_err = traceback.format_exc()
            err = str(e) + " - " + trace_err
            logging.info(f"Error en la respuesta de Azure: {err}")
        if again:
            if self.model_conf['SUBSTITUDE_2_DEPLOYMENT_NAME'].lower() == "llama-3.3-70b-instruct":
                logging.info("\n\n\n")
                logging.info("----------------------------------------")
                logging.info("Sustitudo atiendendo Llama-3.3-70B-Instruct")
                try:
                    logging.info("\n\n\n.............................................")
                    logging.info("\n%s", json.dumps(work_memory, indent=4))
                    logging.info("........................................\n\n\n")
                    response = self.model.complete(
                        messages= work_memory,
                        model =self.model_conf['SUBSTITUDE_2_DEPLOYMENT_NAME'],
                        max_tokens=max_tokens
                    )
                    logging.info("----------------------------------------")
                    logging.info("\n\n\n")                    
                    return response.choices[0].message.content
                except Exception as e2:
                    trace_err2 = traceback.format_exc()
                    err2 = str(e2) + " - " + trace_err2
                    logging.info(f"Error en la respuesta de Azure: {err2}")
                    logging.info("----------------------------------------")
                    logging.info("\n\n\n")                    
                    return ""
        logging.error("\n\n\n****************************************")
        logging.error("No se pudo generar una respuesta válida.")
        return ""
                    
class AzureOpenAIInference(AIService):

    def __init__(self, substitude_1_model = None, substitude_2_model  = None) -> None:
        super().__init__()
        self.substitude_1_model = substitude_1_model
        self.substitude_2_model = substitude_2_model

    def setup(self, config: dict) -> None:        
        self.model_conf:dict = config
        self.model:any = AzureOpenAI(
            api_version=config['API_VERSION'],
            azure_endpoint=config['AZURE_OPEN_AI_INFERENCE_SDK_ENDPOINT'],
            api_key=config['AZURE_INFERENCE_SDK_KEY'],
            max_retries=0
        )
        self.wait_time = 0
        self.total_tokens = 0
        self.exception_time = None
        self.main_model_enable = True
        self.current_time = time.time()
        if self.substitude_1_model is not None:
            self.substitude_1_model.setup(config, config['SUBSTITUDE_1_DEPLOYMENT_NAME'])
        if self.substitude_2_model is not None:
            self.substitude_2_model.setup(config, config['SUBSTITUDE_2_DEPLOYMENT_NAME'])
        
    def wait_strategy_for_rate_limit(self, exception):
        self.wait_time = 0
        self.main_model_enable = False
        self.exception_time = time.time()
        print(exception)
        if isinstance(exception, (RateLimitError, APIStatusError)):
            if hasattr(exception, 'response') and exception.response:
                headers = exception.response.headers
                retry_after_seconds = headers.get("Retry-After")
                if retry_after_seconds:
                    try:
                        wait_time = int(retry_after_seconds)
                        logging.info(f"Rate limit: Respetando header Retry-After: esperando {wait_time} segundos.")
                        self.wait_time = wait_time
                    except ValueError:
                        logging.info(f"Rate limit: Retry-After header no es un entero ({retry_after_seconds}). Usando backoff exponencial.")
                else: # No hay Retry-After, usar backoff exponencial
                    logging.info("Rate limit: No se encontró header Retry-After. Usando backoff exponencial.")
            else: # No hay objeto response, usar backoff exponencial
                logging.info("Rate limit: No se encontró objeto response en la excepción. Usando backoff exponencial.")
        if self.wait_time == 0:
            logging.warning("Rate limit: No se especificó Retry-After. Usando backoff exponencial.")
            # Si no se especifica Retry-After, usar backoff exponencial
            self.wait_time = 2 ** (self.wait_time // 60)
        
    def generate(self, work_memory, max_tokens=2000, temperature=0, top_p=0.9) -> str:
        again = False
        try:            
            if self.main_model_enable:
                response = self.model.chat.completions.create(
                    messages=work_memory,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    model=self.model_conf['DEPLOYMENT_NAME'],
                )
                if hasattr(response, 'usage') and response.usage is not None:
                    logging.info("\n--- Uso de Tokens ---")
                    logging.info(f"Tokens enviados (prompt): {response.usage.prompt_tokens}")
                    logging.info(f"Tokens recibidos (completion): {response.usage.completion_tokens}")
                    logging.info(f"Tokens totales: {response.usage.total_tokens}")
                    self.total_tokens += response.usage.total_tokens
                    current_t = time.time()
                    elapsed_time = current_t - self.current_time
                    logging.info(f"Tiempo transcurrido para la generación: {elapsed_time:.2f} segundos")
                    # En minutos
                    elapsed_time_minutes = elapsed_time / 60
                    logging.info(f"Tiempo transcurrido para la generación: {elapsed_time_minutes:.2f} minutos")
                    logging.info(f"Total de tokens generados hasta ahora: {self.total_tokens}")
                    # Reinicia el contador si ha pasado más de 1 minuto
                    if elapsed_time >= 60:
                        logging.info("Reiniciando el contador de tiempo y tokens...")
                        self.total_tokens = 0
                        self.current_time = time.time()
                        self.exception_time = None
                    else:
                        if self.total_tokens >= 40000:
                            logging.info("Total de tokens alcanzado (40,000). Activando el modo de excepcion.")
                            self.main_model_enable = False
                            self.wait_time = 60 - elapsed_time + 5
                            self.exception_time = time.time()
                            logging.info(f"Esperando {self.wait_time} segundos antes de reintentar.")
                    logging.info("---------------------\n")                    
                else:
                    logging.info("\n--- Uso de Tokens no disponible en la respuesta ---")
                res = response.choices[0].message.content
                if not res or res == "" or res == "ERROR":
                    again = True
                else:  
                    return response.choices[0].message.content
        except Exception as e:
            self.wait_strategy_for_rate_limit(e)
        #----------------------------------
        # Exception mode
        #----------------------------------
        if not self.main_model_enable or again:
            again = False
            # Si ha pasado más de 1 minuto desde la última excepción, reinicia el modelo principal
            current_t = time.time()
            elapsed_time = current_t - self.exception_time
            logging.info(f"Esperando {self.wait_time} segundos antes de reintentar. Transcurridos: {elapsed_time:.2f} segundos")
            if elapsed_time >= self.wait_time:
                logging.info("Reiniciando el modelo principal después de 1 minuto.")
                self.main_model_enable = True
                self.current_time = time.time()
                self.total_tokens = 0
            # Si el modelo principal está deshabilitado, intenta con los modelos de sustitución
            try:
                logging.warning("Modelo principal en espera. Intentando con el modelo de sustitución-1...")
                if self.substitude_1_model is None:
                    raise ValueError("No se ha configurado un modelo de sustitución-1.")
                return self.substitude_1_model.generate(work_memory, max_tokens=max_tokens)                
            except Exception as e:
                try:
                    logging.warning("Modelo principal en espera. Intentando con el modelo de sustitución-2...")
                    if self.substitude_2_model is None:
                        raise ValueError("No se ha configurado un modelo de sustitución-2.")
                    return self.substitude_2_model.generate(work_memory, max_tokens=max_tokens)
                except Exception as e2:
                    trace_err = traceback.format_exc()
                    err = str(e2) + " - " + trace_err
                    logging.fatal(f"Error en la respuesta de Azure: {err}")
                    raise e2
    
class ServiceProvider:
    _services = {}

    @classmethod
    def register(cls, name: str, service):
        """Register a service with a unique name."""
        cls._services[name] = service

    @classmethod
    def get(cls, name: str):
        """Retrieve a registered service."""
        service = cls._services.get(name)
        if not service:
            raise ValueError(f"Service '{name}' not found!")
        return service