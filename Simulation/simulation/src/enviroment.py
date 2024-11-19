# This is the enviroment file
import numpy as np
import matplotlib.pyplot as plt
from utils import shape


class Obstacle(shape):
    def __init__(self, pos, type, hasCollision, color, interactible, isGoal, shape, radius, width, height):
        super().__init__(shape, radius, width, height, pos)
        self.hasCollision = hasCollision
        self.color = color
        self.interactible = interactible
        # used to determine the type of obstacle, such as food, door, etc.
        self.type = type
        # used to determine if the agent has reached the goal for simulations where the task is to reach a goal. Not used for predator-prey
        self.isGoal = isGoal

    def interact(self, agent):
        if self.interactible:
            if self.type == "food":
                agent.state.fitness += 1  # True American units
            elif self.type == "door":
                self.hasCollision = not self.hasCollision


class Environment:
    def __init__(self, type):
        self.agents = []
        self.bounds = (0, 100, 0, 100)
        self.obstacles = []  # list of obstacles in the environment
        # used to determine the type of environment, such as predator-prey, goal-reaching, etc.
        self.type = type

    def add_agents(self, agents):
        self.agents = agents

    def add_obstacles(self, obstacles):
        self.obstacles = obstacles

    def update_surroundings(self, agent):
        # add any objects and agents around the agent in a radius of 10 units
        for obj in self.obstacles:
            if np.linalg.norm(agent.pos - obj.pos) < 10:
                agent.state.objs.append(obj)
        for other_agent in self.agents:
            if np.linalg.norm(agent.pos - other_agent.pos) < 10:
                agent.state.objs.append(other_agent)
        # remove objects that are no longer in the radius
        agent.state.objs = [
            obj for obj in agent.state.objs if np.linalg.norm(agent.pos - obj.pos) < 10]

    def check_bounds(self, agent):
        # check if the agent is within the bounds of the environment
        if agent.pos[0] < self.bounds[0]:
            agent.pos[0] = self.bounds[0]
        if agent.pos[0] > self.bounds[1]:
            agent.pos[0] = self.bounds[1]
        if agent.pos[1] < self.bounds[2]:
            agent.pos[1] = self.bounds[2]
        if agent.pos[1] > self.bounds[3]:
            agent.pos[1] = self.bounds[3]

    def view(self, real_time=False):
        # Close any existing figures to prevent memory buildup
        plt.close('all')

        # Render the environment using matplotlib
        fig, ax = plt.subplots()
        ax.set_xlim(self.bounds[0], self.bounds[1])
        ax.set_ylim(self.bounds[2], self.bounds[3])
        ax.set_facecolor('darkgray')  # Set background color to dark gray

        for obj in self.obstacles:
            if obj.shape == "circle":
                ax.add_artist(plt.Circle(obj.pos, obj.radius, color="green"))
            elif obj.shape == "rectangle":
                # Adjust rectangle drawing to use center point
                ax.add_artist(plt.Rectangle(
                    (obj.pos[0] - obj.width/2, obj.pos[1] -
                     obj.height/2),  # Bottom-left corner
                    obj.width,
                    obj.height,
                    color="red"
                ))

        for agent in self.agents:
            ax.add_artist(plt.Circle(
                agent.pos, agent.radius, color="blue"))
            # draw transparent circle around agent to show radius of objects it can see
            ax.add_artist(plt.Circle(
                agent.pos, 10, color="blue", alpha=0.1))
            # draw line from agent to anything within its obj list
            for obj in agent.state.objs:
                ax.plot([agent.pos[0], obj.pos[0]], [
                        agent.pos[1], obj.pos[1]], color="black")

        if real_time:
            plt.ion()  # Turn on interactive mode
            plt.draw()
            plt.pause(0.1)  # Short pause to update
            plt.close(fig)  # Explicitly close the figure
            plt.close('all')  # Close any additional figures
        else:
            plt.show()

    def run(self):
        while True:
            for agent in self.agents:
                self.update_surroundings(agent)
                agent.update_action()
                agent.get_collisions()
                agent.solve_collision()
                self.check_bounds(agent)
            self.view(real_time=True)
