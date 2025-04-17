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
        self.hypergenomes = None  # List of hyperNEAT genomes
        pass

    def create_model(self):
        """
        Creates the HyperNEAT model.
        """
        self.hypergenomes = neat.Population(self.hyperConfig)
        pass

    def hypermutate(self):
        """
        Mutates the hyper-parameters of the agent's model.
        Returns a dictionary of the mutated hyper-parameters.
        """
        pass

    def breed(self):
        """
        Breeds/trains the hyperNEAT model.
        """
        pass
