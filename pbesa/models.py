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
from openai import AzureOpenAI
from abc import ABC, abstractmethod
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

import time
from openai import AzureOpenAI, RateLimitError, APIStatusError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    wait_fixed
)

# --------------------------------------------------------
# Define classes
# --------------------------------------------------------

class AIService(ABC):
    """Abstract class for AI services."""

    def __init__(self) -> None:
        self.model:any = None
        self.model_conf:dict = None
        
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

    def setup(self, config: dict) -> None:        
        self.model_conf:dict = config
        self.model:any = ChatCompletionsClient(
            endpoint=config['AZURE_INFERENCE_SDK_ENDPOINT'], 
            credential=AzureKeyCredential(config['AZURE_INFERENCE_SDK_KEY'])
        )

    def generate(self, work_memory) -> str:
        response = self.model.complete(
            messages= work_memory,
            model =self.model_conf['DEPLOYMENT_NAME'],
            max_tokens=self.model_conf['MAX_TOKENS']
        )
        return response.choices[0].message.content

# Función auxiliar para determinar la espera basada en el error
def wait_strategy_for_rate_limit(retry_state):
    """
    Determina la estrategia de espera.
    Si es un RateLimitError y hay un header 'Retry-After', lo usa.
    De lo contrario, usa un backoff exponencial.
    """
    exception = retry_state.outcome.exception()
    if isinstance(exception, (RateLimitError, APIStatusError)):
        if hasattr(exception, 'response') and exception.response:
            headers = exception.response.headers
            retry_after_seconds = headers.get("Retry-After")
            if retry_after_seconds:
                try:
                    wait_time = int(retry_after_seconds)
                    print(f"Rate limit: Respetando header Retry-After: esperando {wait_time} segundos.")
                    return wait_fixed(wait_time)(retry_state) # Usa wait_fixed para el tiempo específico
                except ValueError:
                    print(f"Rate limit: Retry-After header no es un entero ({retry_after_seconds}). Usando backoff exponencial.")
            else: # No hay Retry-After, usar backoff exponencial
                print("Rate limit: No se encontró header Retry-After. Usando backoff exponencial.")
        else: # No hay objeto response, usar backoff exponencial
            print("Rate limit: No se encontró objeto response en la excepción. Usando backoff exponencial.")
    
    # Fallback a backoff exponencial para otros casos o si Retry-After falla
    return wait_exponential(multiplier=1, min=4, max=60)(retry_state)

class AzureOpenAIInference(AIService):

    def __init__(self) -> None:
        super().__init__()

    def setup(self, config: dict) -> None:        
        self.model_conf:dict = config
        self.model:any = AzureOpenAI(
            api_version=config['API_VERSION'],
            azure_endpoint=config['AZURE_INFERENCE_SDK_ENDPOINT'],
            api_key=config['AZURE_INFERENCE_SDK_KEY'],
        )
        self.current_time = time.time()
        self.total_tokens = 0

    def _log_attempt_number(self, retry_state):
        """Función para registrar el número de intento."""
        print(f"Intento {retry_state.attempt_number} fallido. Reintentando...")

    # Usamos retry_if_exception_type para especificar qué excepciones deben activar un reintento.
    # wait_strategy_for_rate_limit determinará dinámicamente el tiempo de espera.
    @retry(
        retry=retry_if_exception_type((RateLimitError, APIStatusError)), # Reintentar en estos errores
        wait=wait_strategy_for_rate_limit, # Estrategia de espera personalizada
        stop=stop_after_attempt(5), # Número máximo de intentos (además del original)
        before_sleep=_log_attempt_number # Función a llamar antes de esperar/dormir
    )
    def generate(self, work_memory, max_tokens=4096, temperature=0, top_p=0.9) -> str:
        print(f"Generando completion para el modelo: {self.model_conf['DEPLOYMENT_NAME']}")
        try:

            # Espera 10 segubdos antes de la primera llamada
            print("Esperando 3 segundos antes de la primera llamada...")
            time.sleep(3)
            print("Llamada a la API de OpenAI...")
            

            response = self.model.chat.completions.create(
                messages=work_memory,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                model=self.model_conf['DEPLOYMENT_NAME'],
            )

            # --- Agrega estas líneas para imprimir el uso de tokens ---
            if hasattr(response, 'usage') and response.usage is not None:
                print("\n--- Uso de Tokens ---")
                print(f"Tokens enviados (prompt): {response.usage.prompt_tokens}")
                print(f"Tokens recibidos (completion): {response.usage.completion_tokens}")
                print(f"Tokens totales: {response.usage.total_tokens}")
                self.total_tokens += response.usage.total_tokens
                current_t = time.time()
                elapsed_time = current_t - self.current_time
                print(f"Tiempo transcurrido para la generación: {elapsed_time:.2f} segundos")
                # En minutos
                elapsed_time_minutes = elapsed_time / 60
                print(f"Tiempo transcurrido para la generación: {elapsed_time_minutes:.2f} minutos")
                print(f"Total de tokens generados hasta ahora: {self.total_tokens}")
                

                if elapsed_time >= 60:
                    print("Reiniciando el contador de tiempo y tokens...")
                    self.total_tokens = 0

                print("---------------------\n")
            else:
                 print("\n--- Uso de Tokens no disponible en la respuesta ---")
            # -------------------------------------------------------

            

            return response.choices[0].message.content
        except RateLimitError as e:
            # Capturada específicamente para poder inspeccionarla si es necesario,
            # pero tenacity se encargará del reintento si esta función la vuelve a lanzar.
            print(f"Error de Límite de Tasa detectado (RateLimitError): {e.message}")
            # Aquí podríamos añadir lógica específica si el error persiste después de los reintentos de tenacity
            # o si queremos hacer algo antes de que tenacity lo maneje (aunque `before_sleep` es mejor para eso)
            raise # Re-lanzar para que tenacity la maneje
        except APIStatusError as e:
            # Similar a RateLimitError, pero más general para errores de API con código de estado.
            # La lógica de reintento de tenacity ya verifica el tipo, pero podemos ser explícitos.
            print(f"Error de API detectado (APIStatusError): Código {e.status_code}, Mensaje: {e.message}")
            if e.status_code == 429:
                # Ya cubierto por retry_if_exception_type y wait_strategy_for_rate_limit
                pass # Tenacity lo manejará
            else:
                # Si es otro APIStatusError que no queremos reintentar con esta política,
                # podríamos manejarlo aquí o dejar que se propague si no está en retry_if_exception_type.
                print(f"Error de API no relacionado con límite de tasa: {e.status_code}")
            raise # Re-lanzar para que tenacity (si aplica) o el llamador lo maneje
        except Exception as e:
            print(f"Ocurrió un error inesperado durante la generación: {e}")
            raise # Re-lanzar otras excepciones

# --- Ejemplo de Uso ---
if __name__ == '__main__':
    # Simula una configuración
    mock_config = {
        'API_VERSION': '2024-02-01', # Reemplaza con tu API version real
        'AZURE_INFERENCE_SDK_ENDPOINT': 'TU_ENDPOINT_AZURE_OPENAI', # Reemplaza
        'AZURE_INFERENCE_SDK_KEY': 'TU_API_KEY', # Reemplaza
        'DEPLOYMENT_NAME': 'gpt-4o' # O tu nombre de despliegue
    }

    # Reemplaza con tu endpoint y key reales para probar.
    # ¡CUIDADO! Las siguientes líneas HARÁN LLAMADAS REALES si descomentas y configuras.
    # Por ahora, para evitar llamadas reales en este ejemplo, el cliente no se usará activamente
    # a menos que descomentes las líneas de llamada.

    # client = LLMClient(mock_config)
    # sample_work_memory = [{"role": "user", "content": "Hola, ¿cómo estás?"}]

    # try:
    #     # Para probar el RateLimitError, necesitarías hacer muchas llamadas muy rápido
    #     # o simular que la API devuelve un RateLimitError.
    #     # Por ejemplo, podrías mockear `client.model.chat.completions.create`
    #     # para que lance un RateLimitError la primera vez.
    #     print("Intentando generar contenido...")
    #     # response_content = client.generate(sample_work_memory)
    #     # print("\nRespuesta del modelo:")
    #     # print(response_content)
    #     print("\nEjemplo de simulación (sin llamada real):")
    #     print("Si esto fuera una llamada real y ocurriera un error 429,")
    #     print("verías los mensajes de reintento de tenacity.")
    
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