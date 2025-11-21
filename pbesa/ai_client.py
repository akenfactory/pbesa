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

# --------------------------------------------------------
# Importa las librerías necesarias
# --------------------------------------------------------

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
    
    def invoke(self, input, config=None, **kwargs):
        """
        Sobrescribe invoke para capturar parámetros adicionales y pasarlos a _generate.
        """
        # Extraer parámetros de kwargs que son específicos del LLM
        llm_kwargs = {}
        if config and isinstance(config, dict):
            configurable = config.get('configurable', {})
            for key in ['max_tokens', 'temperature', 'top_p']:
                if key in configurable and key not in llm_kwargs:
                    llm_kwargs[key] = configurable[key]
        
        # Almacenar temporalmente los parámetros para que _generate los pueda leer
        if llm_kwargs:
            self._temp_invoke_params = llm_kwargs.copy()
        else:
            self._temp_invoke_params = None
        
        # Llamar al invoke del padre pero pasando los parámetros del LLM en config
        if llm_kwargs:
            # Crear un nuevo config con los parámetros del LLM
            if config is None:
                config = {}
            if 'configurable' not in config:
                config['configurable'] = {}
            config['configurable'].update(llm_kwargs)        
        try:
            return super().invoke(input, config=config, **kwargs)
        finally:
            # Limpiar los parámetros temporales después de la invocación
            self._temp_invoke_params = None

    def _generate(self, messages, stop=None, **kwargs):
        try:
            # Verificar que el modelo esté disponible
            if self.model is None:
                # Recrear el modelo si es necesario
                api_version = self.model_conf["API_VERSION"]
                self.model = AzureOpenAI(
                    api_version=api_version,
                    azure_endpoint=self.model_conf['AZURE_OPEN_AI_INFERENCE_SDK_ENDPOINT'],
                    api_key=self.model_conf['AZURE_INFERENCE_SDK_KEY'],
                )
            
            # Obtener parámetros desde kwargs, invocation_params o usar valores por defecto
            invocation_params = self._temp_invoke_params or {}
            
            # Usar valores por defecto si no se encuentran
            max_tokens = (
                invocation_params.get('max_tokens') or 
                1000
            )
            temperature = (
                invocation_params.get('temperature') or 
                1.0
            )
            top_p = (
                invocation_params.get('top_p') or 
                1.0
            )
            
            # Efectua la peticion al modelo
            resp = self.model.chat.completions.create(
                messages=[{"role": "user" if m.type == "human" else "system", "content": m.content} for m in messages],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                model=self.model_conf['DEPLOYMENT_NAME']
            )

            # Procesa la respuesta
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
