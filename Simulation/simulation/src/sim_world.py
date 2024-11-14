# This file is going to be the main file in the simulation
# It will contain the main loop for the simulation
# it will also handle the creation of the agents and the environment

from agent import Agent
from environment import Environment


def main():
    # Create the environment
    env = Environment()
    # Create the agents
    agents = []
    for i in range(10):
        agents.append(Agent(i, "NEAT", "PRED_PREY", [0, 0]))
    # Add the agents to the environment
    env.add_agents(agents)
    # Run the simulation
    env.run()


if __name__ == "__main__":
    main()
