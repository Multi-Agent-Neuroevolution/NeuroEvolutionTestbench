import neat
import numpy as np
import matplotlib.pyplot as plt
from agent import Agent
from predator_prey import Predator, Prey
from enviroment import Environment, Obstacle
import multiprocessing

import logging
logger = logging.getLogger(__name__)

def create_simulation(num_agents=5, simulation_type="PRED_PREY", config_path=None):
    # Create the environment with optimal number of workers
    num_cores = multiprocessing.cpu_count()
    env = Environment(simulation_type)
    env.max_workers = max(1, num_cores - 1)

    # Load NEAT configuration
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Create the NEAT population
    population = neat.Population(config)

    # Create agents
    agents = []
    objects = []

    # Add obstacles
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

    # Create agents with genomes
    for i, (genome_id, genome) in enumerate(population.population.items()):
        pos = np.array([np.random.uniform(-200, 200),
                        np.random.uniform(-200, 200)])
        if i % 2 == 0:
            agents.append(
                Predator(i, "NEAT", "PRED_PREY", pos, genome, config))
        else:
            agents.append(Prey(i, "NEAT", "PRED_PREY", pos, genome, config))

    # Add agents and obstacles to environment
    env.add_agents(agents)
    env.add_obstacles(objects)

    return env, population, config


def main():
    try:
        # Configuration
        NUM_AGENTS = 4000
        SIMULATION_TYPE = "PRED_PREY"
        CONFIG_PATH = "../../Config/balls.conf"  # Path to your NEAT config file

        # Create simulation
        env, population, config = create_simulation(
            num_agents=NUM_AGENTS, simulation_type=SIMULATION_TYPE, config_path=CONFIG_PATH)

        logger.info(f"Starting simulation with {NUM_AGENTS} agents...")
        logger.info(
            f"Using {env.max_workers} Logical CPU cores for parallel processing")

        # Run the simulation
        env.run()

    except KeyboardInterrupt:
        logger.info("\nSimulation terminated by user")
    except Exception as e:
        logger.info(f"Error during simulation: {str(e)}")
        raise


if __name__ == "__main__":
    logging.basicConfig(filename='../../Logs/sim.log',level=logging.INFO)
    logger.info('started')
    main()
