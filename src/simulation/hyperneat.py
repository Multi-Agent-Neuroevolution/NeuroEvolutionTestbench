import neat
import random
import numpy as np
from agents import Predator, Prey


class Hyper_model(self):
    """
    HyperNEAT model for the simulation.
    """

    def __init__(self, hyperConfig, model_type, model_config):
        """
        Initializes the HyperNEAT model.
        Args:
            - HyperConfig: The configuration for the HyperNEAT model.
            - model_type: The type of the model (e.g., predator or prey).
            - model_config: The configuration for the model to be changed.
        """
        self.hyperConfig = hyperConfig
        self.model_type = model_type
        self.model_config = model_config
        self.hypermodels = None  # List of hyperNEAT models
        pass

    def create_models(self, configPath):
        """
        Creates the HyperNEAT model.
        """
        self.hyperConfig = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            configPath
        )
        self.hypermodels = neat.Population(self.hyperConfig)

        pass

    def generate_hyperneat_offspring(survivors,
                                     num_offspring,
                                     bounds,
                                     substrate_schema):
        """
        Generates offspring from the hyperNEAT model.
        """
        pass

    def breed(self):
        """
        Breeds/trains the hyperNEAT model.
        """
        pass
