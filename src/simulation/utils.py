"""utils.py holds various utility classes and functions for the simulation."""
import numpy as np
import logging
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