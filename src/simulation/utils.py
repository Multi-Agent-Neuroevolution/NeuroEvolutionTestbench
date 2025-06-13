"""utils.py holds various utility classes and functions for the simulation."""
import numpy as np
import logging
import neat
from collections import defaultdict

logger = logging.getLogger(__name__)


class Metrics:
    def __init__(self):
        self._metrics = defaultdict(float)

    def update(self, metric_name, val):
        self._metrics[metric_name] = val

    def increment(self, metric_name, val):
        self._metrics[metric_name] += val

    def decrement(self, metric_name, val):
        self._metrics[metric_name] -= val

    def get(self, metric_name):
        return self._metrics[metric_name]

    def get_all(self):
        return dict(self._metrics)

    def reset(self):
        self._metrics.clear()

# Class used for creating obstacles in the environment


class Shape:
    def __init__(self, shape, radius, width, height, pos, collidable):
        self.shape = shape
        self.radius = radius
        self.width = width
        self.height = height
        self.pos = pos
        self.collidable = collidable

# Used to determine the state of the agent, and what is happening around it. Updated every tick


class State:
    def __init__(self):
        self.vel = 0
        # list of obstacles/agents around the agent. Each object may or may not have collision.
        self.objs = []
        # list of objects close enought for the agent to interact with
        self.interactables = []
        self.collisions = []
        # These are pre-allocated for performance reasons
        self.pos_array = np.zeros(2)
        self.direction = np.zeros(2)


class FitnessHelper:
    def __init__(self):
        self.avg_fitness = 0.0
        self.min_fitness = float('inf')
        self.max_fitness = float('-inf')
        self.std_dev_fitness = 0.0
        self.percent_alive = 0.0
        self.num_alive = 0

    def calculate_hyperneat_stats(agents, population_size):
        """Calculate the hyperneat stats for the given agents."""
        fitness_helper = FitnessHelper()
        fitness_helper.avg_fitness_rel = np.mean(
            [agent.fitness for agent in agents])
        fitness_helper.min_fitness = np.min(
            [agent.fitness for agent in agents])
        fitness_helper.max_fitness = np.max(
            [agent.fitness for agent in agents])
        fitness_helper.std_dev_fitness = np.std(
            [agent.fitness for agent in agents])
        fitness_helper.percent_alive = len(
            [agent for agent in agents if agent.alive]) / population_size
        fitness_helper.num_alive = len(
            [agent for agent in agents if agent.alive])
        return fitness_helper


def build_configs(config_path):
    """Build the configs for the simulation.
    returns a dictionary of configs."""
    # Create a copy of the config for each agent subtype
    defConfig = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    predStdConfig = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    predNeatConfig = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    predHyprConfig = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    preyStdConfig = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    preyNeatConfig = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    preyHyprConfig = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    cppn_config = {
        'hidden_dims': [32, 32],  # two hidden layers of 32 neurons
        'mutate_std': 0.05        # std deviation for Gaussian weight mutations
    }

    predStdConfig.genome_config.__dict__['conn_add_prob'] = 0
    predStdConfig.genome_config.__dict__['conn_delete_prob'] = 0
    predStdConfig.genome_config.__dict__['node_add_prob'] = 0
    predStdConfig.genome_config.__dict__['node_delete_prob'] = 0
    preyStdConfig.genome_config.__dict__['conn_add_prob'] = 0
    preyStdConfig.genome_config.__dict__['conn_delete_prob'] = 0
    preyStdConfig.genome_config.__dict__['node_add_prob'] = 0
    preyStdConfig.genome_config.__dict__['node_delete_prob'] = 0

    return {
        'defConfig': defConfig,
        'predStdConfig': predStdConfig,
        'predNeatConfig': predNeatConfig,
        'predHyprConfig': predHyprConfig,
        'preyStdConfig': preyStdConfig,
        'preyNeatConfig': preyNeatConfig,
        'preyHyprConfig': preyHyprConfig,
        'cppn_config': cppn_config
    }
