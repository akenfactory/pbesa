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

    def derive(self) -> str:
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
            #self.log.error(err)
            print(err)
            return None

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