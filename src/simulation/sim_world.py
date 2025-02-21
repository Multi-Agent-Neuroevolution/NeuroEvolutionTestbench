"""sim_world.py is where the simulation is created, ran and reran. It is the main file for the simulation."""
import neat
import numpy as np
import matplotlib.pyplot as plt
from evolution_utils import breed_and_mutate
from agents import Predator, Prey
from environment import Environment
import multiprocessing
import logging
import logs
import constants

# Initialize logger
logger = logging.getLogger(__name__)

# Definition for handling the creation of the simulation environment


def create_simulation(simulation_type="PRED_PREY", config_path=None, steps=1000, bounds=[-200, 200, -200, 200], pred_percent=0.25, food_amount=10, prey_spawn_bounds=[50, 150, 50, 150], pred_spawn_bounds=[-150, -50, -150, -50], food_respawn_rate=0.1):
    # Create the environment with optimal number of workers
    num_cores = multiprocessing.cpu_count()
    env = Environment(simulation_type, steps, bounds, food_respawn_rate)
    env.max_workers = max(1, num_cores - 1)

    # Variables to be sent to the environment initialization function
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    population = neat.Population(config)
    pred_pop = int(len(population.population.items())*pred_percent)
    print(pred_pop)
    print(len(population.population.items()))
    prey_pop = len(population.population.items()) - pred_pop
    print(prey_pop)
    env.initialize_environment(
        config=config,
        population=population,
        pred_pop=pred_pop,
        prey_pop=prey_pop,
        pred_spawn_bounds=pred_spawn_bounds,
        prey_spawn_bounds=prey_spawn_bounds,
        food_amount=food_amount
    )

    # Update logger with simulation start info and max CPU cores being used
    logger.info(f"Starting simulation with {config.pop_size} agents...")
    logger.info(
        f"Using {env.max_workers} Logical CPU cores for parallel processing")

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
    top_predators = sorted(predators, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(predators) * 0.1))]
    top_preys = sorted(preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(preys) * 0.1))]

    # Number of offspring to create for predators and prey
    num_pred_offspring = int(pred_pop - len(top_predators))
    num_prey_offspring = int(prey_pop - len(top_preys))

    # Breed and mutate predators and prey
    new_predators = breed_and_mutate(
        config, top_predators, is_predator=True, num_offspring=num_pred_offspring)
    new_preys = breed_and_mutate(
        config, top_preys, is_predator=False, num_offspring=num_prey_offspring)

    # Replace the old population with the new one
    env.overwrite_agents(top_predators + top_preys + new_predators + new_preys)

# Main function, configures simulation then runs through epochs


def main():
    try:
        # Creates simulation environment
        env, population, config, populationSize, pred_pop, prey_pop = create_simulation(
            simulation_type=constants.SIMULATION_TYPE,
            config_path=constants.CONFIG_PATH,
            steps=constants.STEPS,
            bounds=constants.BOUNDS,
            pred_percent=constants.PRED_PERCENT,
            food_amount=constants.FOOD_AMOUNT,
            prey_spawn_bounds=constants.PREY_SPAWN_BOUNDS,
            pred_spawn_bounds=constants.PRED_SPAWN_BOUNDS,
            food_respawn_rate=constants.FOOD_RESPAWN_RATE
        )

        # Create log for the average network size
        logs.log_avg_network_size(env.agents)

        # Run simulation, looping according to the number of epochs specified
        for i in range(constants.EPOCHS):
            env.run()
            # TO DO: this can probably be moved to environment.py
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
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

    # Setup handlers for different log files
    info_handler = logging.FileHandler('./Logs/sim.log')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # # Comment this out when debugging log is unnecessary
    # debug_handler = logging.FileHandler('./Logs/debug.log')
    # debug_handler.setLevel(logging.DEBUG)
    # debug_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    # Set to lowest level you want to capture
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(info_handler)
    # root_logger.addHandler(debug_handler) # Comment this out when debugging log is unnecessary

    logger.info('started')
    main()
