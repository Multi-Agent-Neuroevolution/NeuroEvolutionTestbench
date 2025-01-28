import neat
import numpy as np
from agent import Agent

import logging
logger = logging.getLogger(__name__)

class Predator(Agent):
    def __init__(self, id, algorithm_name, relationship_name, pos, neat_genome, neat_config):
        super().__init__(id, "NEAT", "PRED_PREY", pos, neat_genome, neat_config)
        self.energy = 100

    def update_action(self):
        self.get_inputs()
        action = self.brain.activate(self.inputs)
        self.pos += np.array(action[:2])  # Update position
          
        # Energy loss for moving
        self.energy -= 0.005
        if self.energy <= 0:
            self.alive = False


class Prey(Agent):
    def __init__(self, id, algorithm_name, relationship_name, pos, neat_genome, neat_config):
        super().__init__(id, "NEAT", "PRED_PREY", pos, neat_genome, neat_config)

    def update_action(self):
        self.get_inputs()
        action = self.brain.activate(self.inputs)
        self.pos += np.array(action[:2])
