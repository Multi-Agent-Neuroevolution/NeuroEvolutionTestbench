import random
import neat
import numpy as np
import matplotlib.pyplot as plt
from agent import Agent
from evolution_utils import breed_and_mutate
from predator_prey import Predator, Prey
from enviroment import Environment, Obstacle
import multiprocessing
import logging
import logs

# Initialize logger
logger = logging.getLogger(__name__)

# Definition for handling the creation of the simulation environment
def create_simulation(simulation_type="PRED_PREY", config_path=None, steps=1000, bounds=[-200, 200, -200, 200], pred_percent=0.25, food_amount=10, prey_spawn_bounds=[50, 150, 50, 150], pred_spawn_bounds=[-150, -50, -150, -50], food_respawn_rate=0.1):
    # Create the environment with optimal number of workers
    num_cores = multiprocessing.cpu_count()
    env = Environment(simulation_type, steps, bounds, food_respawn_rate)
    env.max_workers = max(1, num_cores - 1)

    # Load NEAT configuration from read config file
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Create the NEAT population
    population = neat.Population(config)
    pred_pop = int(len(population.population.items())*pred_percent)
    print(pred_pop)
    print(len(population.population.items()))
    prey_pop = len(population.population.items()) - pred_pop

    # Empty lists for agents and objects are initialized here
    agents = []
    objects = []

    # Add objects with format as follows: (object center, obstacle type, hasCollision, color, interactible, isGoal, shape, radius (0 for rectangles), width, height)
    # For loop is to make food-type objects limited to a certain amount (food_amount)
    for i in range(food_amount):
        objects.append(Obstacle(np.array([np.random.uniform(bounds[0], bounds[1]), np.random.uniform(bounds[2], bounds[3])]), "food", False, "green", True, False, "circle", 1, 0, 0))
    objects.append(Obstacle(np.array([0, 0]), "obstacle", True, "red", False, False, "rectangle", 0, 100, 45))
    
    # Genomes and agents are both created and paired together here, for both predator and prey populations
    for i in range(pred_pop):
        pos = np.array([np.random.uniform(pred_spawn_bounds[0], pred_spawn_bounds[1]), np.random.uniform(pred_spawn_bounds[2], pred_spawn_bounds[3])])
        genome = population.population[i + 1]
        agent = Predator(i, "NEAT", "PRED_PREY", pos, genome, config)
        agents.append(agent)
    for i in range(prey_pop):
        pos = np.array([np.random.uniform(prey_spawn_bounds[0], prey_spawn_bounds[1]), np.random.uniform(prey_spawn_bounds[2], prey_spawn_bounds[3])])
        genome = population.population[i + pred_pop]
        agent = Prey(i + pred_pop, "NEAT", "PRED_PREY", pos, genome, config)
        agents.append(agent)

    # Add agents and obstacles to environment
    env.add_agents(agents)
    env.add_obstacles(objects)

    # Update logger with simulation start info and max CPU cores being used
    logger.info(f"Starting simulation with {config.pop_size} agents...")
    logger.info(f"Using {env.max_workers} Logical CPU cores for parallel processing")

    return env, population, config, len(population.population.items()), pred_pop, prey_pop


def mutate(genome, config, env, population_size, pred_pop, prey_pop):
    # Create separate lists for predators and prey
    predators = [agent for agent in env.agents if isinstance(agent, Predator)]
    preys = [agent for agent in env.agents if isinstance(agent, Prey)]

    for agent in predators + preys:
        if agent.neat_genome:
            # scale the fitness of the agent using like tanh (0-100)
            # agent.fitness = np.tanh(agent.fitness) * 100
            # Sync agent fitness with genome fitness
            agent.neat_genome.fitness = agent.fitness
    
    # Save the average fitness of both predator and prey populations to a CSV file
    logs.avg_agent_fitness(predators, preys)

    # Sort and retain the top 10% based on fitness
    top_predators = sorted(predators, key=lambda x: x.fitness, reverse=True)[:max(1, int(len(predators) * 0.1))]
    top_preys = sorted(preys, key=lambda x: x.fitness, reverse=True)[:max(1, int(len(preys) * 0.1))]

    # Number of offspring to create for predators and prey
    num_pred_offspring = int(pred_pop - len(top_predators))
    num_prey_offspring = int(prey_pop - len(top_preys))

    # Breed and mutate predators and prey
    new_predators = breed_and_mutate(config, top_predators, is_predator=True, num_offspring=num_pred_offspring)
    new_preys = breed_and_mutate(config, top_preys, is_predator=False, num_offspring=num_prey_offspring)

    # Replace the old population with the new one
    env.overwrite_agents(top_predators + top_preys + new_predators + new_preys)

# Main function, configures simulation then runs through epochs
def main():
    try:
        # Configuration constants (parameters)
        SIMULATION_TYPE = "PRED_PREY"
        CONFIG_PATH = "./Config/balls.conf"
        STEPS = 1500
        EPOCHS = 20
        BOUNDS = [-200, 200, -200, 200]
        PREY_SPAWN_BOUNDS = [-150, 150, 50, 150]
        PRED_SPAWN_BOUNDS = [-150, 150, -150, -50]
        RATIO = 0.75
        FOODAMOUNT = 100
        FOOD_RESPAWN_RATE = 0.1
        pred_percent = 1 - RATIO

        # Creates simulation environment
        env, population, config, populationSize, pred_pop, prey_pop = create_simulation(simulation_type=SIMULATION_TYPE, config_path=CONFIG_PATH, steps=STEPS, bounds=BOUNDS, pred_percent=pred_percent, food_amount=FOODAMOUNT, prey_spawn_bounds=PREY_SPAWN_BOUNDS, pred_spawn_bounds=PRED_SPAWN_BOUNDS, food_respawn_rate=FOOD_RESPAWN_RATE)

        # Create log for the average network size
        logs.log_avg_network_size(env.agents)

        # Run simulation, looping according to the number of epochs specified
        for i in range(EPOCHS):
            env.run()
            mutate(population, config, env, populationSize, pred_pop, prey_pop)
            env.reset()
            print(f"Epoch {i+1} completed")
            logger.info(f"Epoch {i+1} completed")

        # Create logs for genome information
        logs.pickle_genomes(env.agents)
        logs.save_genomes_json(env.agents)
        logs.log_avg_network_size(env.agents)

    # Error-handling for if the user manually stops the simulation or if an error occurs
    except KeyboardInterrupt:
        logger.info("\nSimulation terminated by user")
    except Exception as e:
        logger.info(f"Error during simulation: {str(e)}")
        raise

# Initialize logger, starts simulation by calling main()
if __name__ == "__main__":
    logging.basicConfig(filename='./Logs/sim.log', level=logging.INFO)
    logger.info('started')
    main()
