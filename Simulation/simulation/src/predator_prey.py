import neat
import numpy as np
from agent import Agent


class Predator(Agent):
    def __init__(self, id, pos, neat_genome, config):
        super().__init__(id, "NEAT", "PRED_PREY", pos)
        self.neat_genome = neat_genome
        self.brain = neat.nn.FeedForwardNetwork.create(neat_genome, config)
        self.energy = 100

    def update_action(self):
        inputs = [...]  # Gather inputs like nearby prey positions
        action = self.brain.activate(inputs)
        self.pos += np.array(action[:2])  # Update position

        # Energy loss for moving
        self.energy -= 1
        if self.energy <= 0:
            self.alive = False


class Prey(Agent):
    def __init__(self, id, pos, neat_genome, config):
        super().__init__(id, "NEAT", "PRED_PREY", pos)
        self.neat_genome = neat_genome
        self.brain = neat.nn.FeedForwardNetwork.create(neat_genome, config)

    def update_action(self):
        inputs = [...]  # Gather inputs like nearby predator positions
        action = self.brain.activate(inputs)
        self.pos += np.array(action[:2])
