# This file is going to be the main file in the simulation
# It will contain the main loop for the simulation
# it will also handle the creation of the agents and the environment
import numpy as np
import matplotlib.pyplot as plt
from agent import Agent
from enviroment import Environment
from enviroment import Obstacle


def main():
    # Create the environment
    env = Environment("PRED_PREY")
    # Create the agents
    agents = []
    objects = []
    objects.append(Obstacle(
        np.array([50, 50]),  # Center of the circle/rectangle
        "food",
        True,  # hasCollision
        "green",
        True,  # interactible
        False,  # isGoal
        "circle",  # shape
        1,     # radius
        0,     # width (0 for circle)
        0      # height (0 for circle)
    ))
    objects.append(Obstacle(
        np.array([20, 20]),  # Center of the rectangle
        "door",
        True,  # hasCollision
        "red",  # color
        True,  # interactible
        False,  # isGoal
        "rectangle",
        0,     # radius (0 for rectangle)
        2,    # width
        10     # height
    ))

    for i in range(50):
        # positon is a numpy array of 2 elements
        pos = np.array([np.random.rand() * 100, np.random.rand() * 100])
        agents.append(Agent(i, "NEAT", "PRED_PREY", pos))

    # Add the agents to the environment
    env.add_agents(agents)
    # Add the obstacles to the environment
    env.add_obstacles(objects)
    # Run the simulation
    env.run()


if __name__ == "__main__":
    main()
