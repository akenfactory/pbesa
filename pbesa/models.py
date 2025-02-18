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

import traceback
from abc import ABC, abstractmethod
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# --------------------------------------------------------
# Define classes
# --------------------------------------------------------

class AIService(ABC):
    """Abstract class for AI services."""

    def __init__(self) -> None:
        self.model:any = None
        self.model_conf:dict = None
        self.__work_memory:list = []

    @abstractmethod
    def setup(self, config: dict) -> None:
        """Method to setup the AI service."""
        raise NotImplementedError("Method 'setup' must be implemented.")

    @abstractmethod
    def generate(self) -> str:
        """Method to generate a response based on user input."""
        raise NotImplementedError("Method 'setup' must be implemented.")

class GPTService(AIService):

    def __init__(self) -> None:
        super().__init__()

    def setup(self, config: dict, work_memory) -> None:
        self.model:any = config['model']
        self.model_conf:dict = config
        self.__work_memory:list = work_memory

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
                        print("OpenAI response not completed")
                        return None
                    #self.log.info("OpenAI response completed", extra={'log_data': {'gpt_response': response}})
                    print("OpenAI response completed")
                    self.__work_memory.append({"role": "assistant", "content": res})
                    return res
                except:
                    #self.log.warning("OpenAI response not completed", extra={'log_data': {'gpt_response': response}})
                    print("OpenAI response not completed")
                    return None
            else:
                #self.log.warning("OpenAI response not completed", extra={'log_data': {'gpt_response': response}})
                print("OpenAI response not completed")
                return None
        except Exception as e:
            trace_err = traceback.format_exc()
            err = str(e) + " - " + trace_err
            print(err)
            return None

class AIFoundry(AIService):

    def setup(self, config: dict) -> None:        
        self.model_conf:dict = config
        self.__work_memory:list = config['work_memory']
        project = AIProjectClient.from_connection_string(
            conn_str=config['project_connection_string'], credential=DefaultAzureCredential()
        )
        self.model:any = project.inference.get_chat_completions_client()

    def generate(self) -> str:
        response = self.model.complete(
            model=self.model_conf['model'],
            messages=self.__work_memory,
        )
        return response.choices[0].message.content

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