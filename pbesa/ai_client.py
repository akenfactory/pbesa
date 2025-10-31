# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor Aken
@version 1.0.0
@date 07/01/25
@description Cliente de integración con servicios de inteligencia artificial

"""

# Importa las librerías necesarias

from log import get_logger
from openai import AzureOpenAI
from pbesa.models import AzureInference
from langchain_core.messages import AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult

# --------------------------------------------------------
# Define variables and constants
# --------------------------------------------------------

# Inicializa el logging
logging = get_logger()

class AzureInferenceChat(BaseChatModel, AzureInference):
    """
    Clase que implementa un cliente de chat para Azure Inference usando LangChain.
    
    Esta clase permite pasar parámetros dinámicos (max_tokens, temperature, top_p) 
    en las invocaciones mediante diferentes métodos:
    
    1. Usando bind() para crear una instancia con parámetros fijos:
       llm = AzureInferenceChat()
       llm_bound = llm.bind(max_tokens=2000, temperature=0.7)
       chain = prompt | llm_bound
       response = chain.invoke({"user_message": "Hola"})
    
    2. Pasando parámetros directamente en invoke() (si el modelo lo soporta):
       response = chain.invoke({"user_message": "Hola"}, max_tokens=2000, temperature=0.7)
    
    3. Usando config en invoke():
       response = chain.invoke(
           {"user_message": "Hola"},
           config={"configurable": {"temperature": 0.7, "max_tokens": 1000}}
       )
    
    4. Usando safe_llm_invoke() con parámetros:                                                                                                                                                                                                                                                                                                                         
       from business.dialog_engine.agents import safe_llm_invoke
       response = safe_llm_invoke(
           chain,
           {"user_message": "Hola"},
           max_tokens=2000,
           temperature=0.7,
           top_p=0.9
       )
    """
    
    model_conf:dict=None
    model:any =None

    def __init__(self, model_conf):
        super().__init__()
        self.model_conf = model_conf        
        api_version = self.model_conf["API_VERSION"]
        self.model = AzureOpenAI(
            api_version=api_version,
            azure_endpoint=self.model_conf['AZURE_OPEN_AI_INFERENCE_SDK_ENDPOINT'],
            api_key=self.model_conf['AZURE_INFERENCE_SDK_KEY'],
        )

    @property
    def _llm_type(self) -> str:
        """Identificador único del modelo para trazas/logs."""
        return "azure_inference_chat"
    
    def _generate(self, messages, stop=None, **kwargs):
        try:
            # Verificar que el modelo esté disponible
            if self.model is None:
                # Recrear el modelo si es necesario
                api_version = self.model_conf["API_VERSION"]
                self.model = AzureOpenAI(
                    api_version=api_version,
                    azure_endpoint=self.model_conf['AZURE_INFERENCE_SDK_ENDPOINT'],
                    api_key=self.model_conf['AZURE_INFERENCE_SDK_KEY'],
                )
            
            # Obtener parámetros desde kwargs, invocation_params o usar valores por defecto
            # LangChain puede pasar estos parámetros de diferentes formas:
            # 1. Como kwargs directos: invoke(..., max_tokens=1000)
            # 2. En invocation_params: parte del flujo interno de LangChain
            # 3. En el parámetro config: invoke(..., config={"configurable": {"temperature": 0.7}})
            invocation_params = kwargs.get('invocation_params', {})
            
            # Buscar parámetros en diferentes lugares (kwargs, invocation_params, config)
            # Usar valores por defecto si no se encuentran
            max_tokens = (
                kwargs.get('max_tokens') or 
                invocation_params.get('max_tokens') or 
                4096
            )
            temperature = (
                kwargs.get('temperature') or 
                invocation_params.get('temperature') or 
                1.0
            )
            top_p = (
                kwargs.get('top_p') or 
                invocation_params.get('top_p') or 
                1.0
            )
            
            resp = self.model.chat.completions.create(
                messages=[{"role": "user" if m.type == "human" else "system", "content": m.content} for m in messages],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                model=self.model_conf['DEPLOYMENT_NAME']
            )
            content = resp.choices[0].message.content
            print(f"Response: {content}")
            return ChatResult(generations=[
                ChatGeneration(message=AIMessage(content=content))
            ], llm_output={"usage": resp.usage})
        except Exception as e:
            print(f"Error en _generate: {e}")
            # En caso de error, limpiar el modelo para la próxima llamada
            self.model = None
            raise e

# ========================================================================
# EJEMPLOS DE USO - Cómo pasar parámetros en las invocaciones .invoke()
# ========================================================================
#
# Ejemplo 1: Usando safe_llm_invoke con parámetros personalizados
# ------------------------------------------------------------------------
# from business.dialog_engine.agents import safe_llm_invoke
# from business.dialog_engine.prompts import GREETING_PROMPT
# 
# llm = AzureInferenceChat()
# chain = GREETING_PROMPT | llm
# 
# # Invocación con parámetros personalizados
# response = safe_llm_invoke(
#     chain,
#     {"user_message": "Hola, ¿cómo estás?"},
#     max_tokens=2000,      # Límite de tokens en la respuesta
#     temperature=0.7,     # Creatividad (0.0 = determinista, 1.0 = creativo)
#     top_p=0.9            # Nucleus sampling
# )
# 
# Ejemplo 2: Usando bind() para crear un modelo con parámetros fijos
# ------------------------------------------------------------------------
# llm = AzureInferenceChat()
# # Crear una versión del modelo con parámetros pre-configurados
# llm_configurado = llm.bind(max_tokens=1500, temperature=0.5)
# chain = GREETING_PROMPT | llm_configurado
# response = chain.invoke({"user_message": "Hola"})
# 
# Ejemplo 3: Usando config en invoke() (para chains completos)
# ------------------------------------------------------------------------
# llm = AzureInferenceChat()
# chain = GREETING_PROMPT | llm
# response = chain.invoke(
#     {"user_message": "Hola"},
#     config={
#         "configurable": {
#             "temperature": 0.7,
#             "max_tokens": 1000,
#             "top_p": 0.95
#         }
#     }
# )
# 
# Ejemplo 4: Valores por defecto (si no se especifican parámetros)
# ------------------------------------------------------------------------
# Los valores por defecto son:
# - max_tokens: 4096
# - temperature: 1.0
# - top_p: 1.0
# 
# response = chain.invoke({"user_message": "Hola"})  # Usa valores por defecto
#
# ========================================================================
