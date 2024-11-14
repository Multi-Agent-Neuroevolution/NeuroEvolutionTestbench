# This is the enviroment file
import numpy as np


class Obstacle(shape):
    def __init__(self, pos, type, hasCollision, color, interactible, isGoal):
        super().__init__(type, 0, 0, 0, pos)
        self.hasCollision = hasCollision
        self.color = color
        self.interactible = interactible
        self.isGoal = isGoal  # used to determine if the agent has reached the goal for simulations where the task is to reach a goal. Not used for predator-prey

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

    def update_surroundings(self, agent):
        # add any objects and agents around the agent in a radius of 10 units
        pass

    def run(self):
        self.state = self.movement_handler.create_state(self.agents)
        while True:
            actions = self.generate_random_actions()
            self.update(agent)
