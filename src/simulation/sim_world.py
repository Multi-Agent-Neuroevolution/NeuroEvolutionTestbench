import random
import neat
import numpy as np
import matplotlib.pyplot as plt
from agent import Agent
from predator_prey import Predator, Prey
from enviroment import Environment, Obstacle
import multiprocessing

import logging
logger = logging.getLogger(__name__)


def create_simulation(simulation_type="PRED_PREY", config_path=None, steps=1000, bounds=[-200, 200, -200, 200]):
    # Create the environment with optimal number of workers
    num_cores = multiprocessing.cpu_count()
    env = Environment(simulation_type, steps, bounds)
    env.max_workers = max(1, num_cores - 1)

    # Load NEAT configuration
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
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
    logger.info(f"Starting simulation with {config.pop_size} agents...")
    logger.info(
        f"Using {env.max_workers} Logical CPU cores for parallel processing")
    return env, population, config, len(population.population.items())


def mutate(genome, config, env, population_size):
    # Create separate lists for predators and prey
    predators = [agent for agent in env.agents if isinstance(agent, Predator)]
    preys = [agent for agent in env.agents if isinstance(agent, Prey)]

    for agent in predators + preys:
        if agent.neat_genome:
            # scale the fitness of the agent using like tanh (0-100)
            agent.fitness = np.tanh(agent.fitness) * 100
            # Sync agent fitness with genome fitness
            agent.neat_genome.fitness = agent.fitness
    avg_pred_fitness = np.mean(
        [predator.fitness for predator in predators])
    avg_prey_fitness = np.mean([prey.fitness for prey in preys])
    # save to csv file
    with open('./Data/fitness.csv', 'a') as f:
        f.write(f"{avg_pred_fitness},{avg_prey_fitness}\n")

    # Sort and retain the top 10% based on fitness
    top_predators = sorted(predators, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(predators) * 0.1))]
    top_preys = sorted(preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(preys) * 0.1))]

    # Function to breed and mutate agents
    def breed_and_mutate(parents, is_predator, num_offspring):
        new_agents = []
        for _ in range(num_offspring):
            # Select two random parents
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)

            # Create a child genome by crossover
            child_id = random.randint(0, 100000)  # Generate a unique ID
            child_genome = neat.DefaultGenome(child_id)
            child_genome.configure_crossover(
                parent1.neat_genome, parent2.neat_genome, config)

            # Mutate the child's genome
            child_genome.mutate(config.genome_config)

            # Create a new agent based on the child genome
            pos = (random.randint(0, 100), random.randint(
                0, 100))  # Random position
            if is_predator:
                new_agent = Predator(
                    child_id, "NEAT", "PRED_PREY", pos, child_genome, config)
            else:
                new_agent = Prey(child_id, "NEAT", "PRED_PREY",
                                 pos, child_genome, config)
            new_agents.append(new_agent)
        return new_agents

    # Number of offspring to create for predators and prey
    num_pred_offspring = int(population_size/2 - len(top_predators))
    num_prey_offspring = int(population_size/2 - len(top_preys))

    # Breed and mutate predators and prey
    new_predators = breed_and_mutate(
        top_predators, is_predator=True, num_offspring=num_pred_offspring)
    new_preys = breed_and_mutate(
        top_preys, is_predator=False, num_offspring=num_prey_offspring)

    # Replace the old population with the new one
    env.overwrite_agents(top_predators + top_preys + new_predators + new_preys)


def main():
    try:
        # Configuration
        SIMULATION_TYPE = "PRED_PREY"
        CONFIG_PATH = "./Config/balls.conf"  # Path to your NEAT config file
        STEPS = 200
        EPOCHS = 10
        BOUNDS = [-200, 200, -200, 200]

        # Create simulation
        env, population, config, populationSize = create_simulation(
            simulation_type=SIMULATION_TYPE, config_path=CONFIG_PATH, steps=STEPS, bounds=BOUNDS)

        # Run the simulation
        for i in range(EPOCHS):
            env.run()
            mutate(population, config, env, populationSize)
            env.reset()
            print(f"Epoch {i+1} completed")
            logger.info(f"Epoch {i+1} completed")

    except KeyboardInterrupt:
        logger.info("\nSimulation terminated by user")
    except Exception as e:
        logger.info(f"Error during simulation: {str(e)}")
        raise


if __name__ == "__main__":
    logging.basicConfig(filename='./Logs/sim.log', level=logging.INFO)
    logger.info('started')
    main()
