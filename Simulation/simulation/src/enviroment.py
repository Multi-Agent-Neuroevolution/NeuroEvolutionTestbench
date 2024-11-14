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
        self.obstacles = []  # list of obstacles in the environment
        # used to determine the type of environment, such as predator-prey, goal-reaching, etc.
        self.type = ""

    def add_agents(self, agents):
        self.agents = agents

    def update_surroundings(self, agent):
        # add any objects and agents around the agent in a radius of 10 units
        for obj in self.obstacles:
            if np.linalg.norm(agent.pos - obj.pos) < 10:
                agent.state.objs.append(obj)
        for other_agent in self.agents:
            if np.linalg.norm(agent.pos - other_agent.pos) < 10:
                agent.state.objs.append(other_agent)

    def run(self):
        self.state = self.movement_handler.create_state(self.agents)
        while True:
            for agent in self.agents:
                update_surroundings(agent)
                agent.update_action()
                agent.get_collisions()
                agent.solve_collisions()
