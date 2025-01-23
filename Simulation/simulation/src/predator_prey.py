import neat
import numpy as np
from agent import Agent

import logging
logger = logging.getLogger(__name__)

class Predator(Agent):
    def __init__(self, id, pos, neat_genome, config):
        super().__init__(id, "NEAT", "PRED_PREY", pos)
        self.energy = 100

    def update_action(self):
        get_inputs(self)
        action = self.brain.activate(self.inputs)
        self.pos += np.array(action[:2])  # Update position

        # Energy loss for moving
        self.energy -= 1
        if self.energy <= 0:
            self.alive = False


class Prey(Agent):
    def __init__(self, id, pos, neat_genome, config):
        super().__init__(id, "NEAT", "PRED_PREY", pos)

    def update_action(self):
        get_inputs(self)
        action = self.brain.activate(self.inputs)
        action = self.brain.activate(inputs)
        self.pos += np.array(action[:2])
