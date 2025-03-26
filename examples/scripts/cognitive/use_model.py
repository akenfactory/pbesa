# -*- coding: utf-8 -*-
"""
----------------------------------------------------------
------------------------- PBESA --------------------------
----------------------------------------------------------

@autor AKEN
@version 4.0.0
@date 12/08/24

Example of a simple agent that receives an event and
responds to it. The agent is created, started, an event
is sent to it, and the agent responds to the event.
"""

# --------------------------------------------------------
# Define resources
# --------------------------------------------------------

import time
import traceback
import numpy as np
from pbesa.mas import Adm
from pbesa.cognitive import Model
from pbesa.kernel.agent import Agent
from pbesa.kernel.agent import Action
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Sequential

# --------------------------------------------------------
# Define Action
# --------------------------------------------------------

class XORAction(Action):
    """ An action is a response to the occurrence of an event """

    def execute(self, data:any) -> any:
        """ 
        Response.
        @param data Event data 
        """
        # Get the data
        X = data['X']
        # Evaluate the loaded model
        self.agent.evaluate_model(data)
        # Make predictions with the loaded model
        predictions = self.agent.predict(X)
        print('Predictions:')
        for i, pred in enumerate(predictions):
            print(f'Input: {X[i]} - Predicted Output: {pred[0]:.4f}')

# --------------------------------------------------------
# Define Agent
# --------------------------------------------------------

class XORAgent(Agent, Model):
    """ Through a class the concept of agent is defined """
    
    def setup(self) -> None:
        """
        Method that allows defining the status, structure 
        and resources of the agent
        """
        # Defines the behavior of the agent. An agent can 
        # have one or many behaviors
        self.add_behavior('calculate')
        # Assign an action to the behavior
        self.bind_action('calculate', 'xor', XORAction())

    def shutdown(self) -> None:
        """ Method to free up the resources taken by the agent """
        pass

    def load_model(self, model_config:dict) -> None:
        """ Load model method
        :param model_config: dict
        """ 
        self.model = load_model(model_config['path'])
        print('Model loaded from model/xor_model.h5')

    def train_model(self, model_config:dict, data:any) -> any:
        """ Train model method
        :param model_config: model_config
        :param data: data
        :return: any
        """
        # Get the data
        X = data['X']
        y = data['y']
        # Create a neural network model
        model = Sequential([
            Dense(model_config['hidden_layers'], input_dim=model_config['input_dim'], activation=model_config['activation']),
            Dense(model_config['hidden_layers'], activation=model_config['activation']),
            Dense(model_config['output_layer'], activation=model_config['output_activation'])
        ])
        # Compile the model
        model.compile(optimizer=model_config['optimizer'], loss=model_config['loss'], metrics=model_config['metrics'])
        # Train the model
        model.fit(X, y, epochs=model_config['epochs'], verbose=model_config['verbose'])
        # Evaluate the model
        loss, accuracy = model.evaluate(X, y)
        print(f'Loss: {loss:.4f}, Accuracy: {accuracy:.4f}')
        # Save the model to the 'model/' directory
        model_save_path = model_config['path']
        model.save(model_save_path)
        print(f'Model saved to {model_save_path}')
        return True

    def evaluate_model(self, data:any) -> any:
        """ Evaluate model method
        :param data: data
        :return: any
        """
        # Get the data
        X = data['X']
        y = data['y']
        # Evaluate the loaded model
        loss, accuracy = self.model.evaluate(X, y)
        print(f'Loss: {loss:.4f}, Accuracy: {accuracy:.4f}')
        return True

    def fit_model(self, model_config:dict, data:any) -> any:
        """ Fit model method
        :param model_config: model_config
        :param data: data
        :return: any
        """
        return False

    def predict(self, data:any) -> any:
        """ Predict method
        :param data: data
        :return: any
        """
        return self.model.predict(data)

# --------------------------------------------------------
# Main
# --------------------------------------------------------

# The main function is the entry point of the program
if __name__ == "__main__":
    try:
        # Initialize the container
        mas = Adm()
        mas.start()

        # Data for the XOR problem
        data = {
            "X": np.array([[0, 0], [0, 1], [1, 0], [1, 1]]),
            "y": np.array([[0], [1], [1], [0]])
        }

        # Model configuration
        model_config = {
            'path': 'model/xor_model.h5',
            'hidden_layers': 8,
            'activation': 'relu',
            'output_activation': 'sigmoid',
            'input_dim': 2,
            'optimizer': 'adam',
            'output_layer': 1,
            'loss': 'binary_crossentropy',
            'metrics': ['accuracy'],
            'epochs': 1000,
            'verbose': 0
        }

        # Create the agent
        agent_id = 'Jarvis'
        ag = XORAgent(agent_id)
        ag.train_model(model_config, data)
        ag.load_model(model_config)
        ag.start()

        # Send the event to the agent
        print('Sending event to agent')
        mas.send_event(agent_id, 'xor', data)
        print('Event sent')

        # Wait for the agent to process the event
        time.sleep(1)

        # Remove the agent from the system
        mas.kill_agent(ag)

        # Destroy the Agent Container
        mas.destroy()
    except:
        traceback.print_exc()