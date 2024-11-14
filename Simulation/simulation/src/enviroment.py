# This is the enviroment file
import numpy as np


class shape:
    def __init__(self, type, radius, width, height):
        self.type = ""
        self.radius = radius
        self.width = width
        self.height = height


class Obstacle:
    def __init__(self, pos, shape, hasCollision, color):
        self.pos = pos  # Position of the obstacle center
        self.hasCollision = False
        self.shape = None
        self.color = None
        self.interactible = None
        self.isGoal = False  # used to determine if the agent has reached the goal for simulations where the task is to reach a goal. Not used for predator-prey

    def check_collision(self, agent):
        pass

    # using things like shape, pos, color, etc. to build the obstacle
    def build_obstacle(self):
        pass

    def interact(self, agent):
        pass


class Environment:
    def __init__(self):
        self.agents = []
        self.bounds = (-100, 100, -100, 100)
        self.obstacles = []
        # used to determine the type of environment, such as predator-prey, goal-reaching, etc.
        self.type = ""

    def add_agents(self, agents):
        self.agents = agents

    def run(self):
        self.state = self.movement_handler.create_state(self.agents)
        while True:
            actions = self.generate_random_actions()
            self.update(agent)
