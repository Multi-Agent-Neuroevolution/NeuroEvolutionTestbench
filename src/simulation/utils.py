import numpy as np
import logging

logger = logging.getLogger(__name__)

# Class used for creating obstacles in the environment
class Shape:
    def __init__(self, shape, radius, width, height, pos):
        self.shape = shape
        self.radius = radius
        self.width = width
        self.height = height
        self.pos = pos

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