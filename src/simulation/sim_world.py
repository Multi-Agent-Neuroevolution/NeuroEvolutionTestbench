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
import time

# Initialize logger
logger = logging.getLogger(__name__)


def create_simulation(simulation_type="PRED_PREY", config_path=None, steps=1000, bounds=[-200, 200, -200, 200], pred_percent=0.25, food_amount=10, prey_spawn_bounds=[50, 150, 50, 150], pred_spawn_bounds=[-150, -50, -150, -50], food_respawn_rate=0.1, multi_model=False, model_split=0.5):
    """Creates the simulation environment and initializes the NEAT population.

    Args:
        simulation_type (str): Type of simulation to run.
        config_path (str): Path to the NEAT configuration file.
        steps (int): Number of steps to run the simulation.
        bounds (list): Bounds for the simulation environment.
        pred_percent (float): Percentage of predators in the population.
        food_amount (int): Amount of food in the environment.
        prey_spawn_bounds (list): Spawn bounds for prey.
        pred_spawn_bounds (list): Spawn bounds for predators.
        food_respawn_rate (float): Rate at which food respawns.
        multi_model (bool): Whether to use multiple models.
        model_split (float): Percentage of agents using the NEAT model.

    Returns:
        env (Environment): The simulation environment.
        population (neat.Population): The NEAT population.
        config (neat.Config): The NEAT configuration.
        populationSize (int): Size of the population.
        pred_pop (int): Number of predators in the population.
        prey_pop (int): Number of prey in the population.
        pred_pop_no_neat (int): Number of predators not using NEAT.
        prey_pop_no_neat (int): Number of prey not using NEAT.
    """
    # Create the environment with optimal number of workers
    num_cores = multiprocessing.cpu_count()
    env = Environment(simulation_type, steps, bounds, food_respawn_rate)
    env.max_workers = max(1, num_cores - 1)
    print(f"INFO:\tUsing {env.max_workers} workers for parallel processing")

    # Loads config data to be used in simulation
    print("START:\tCreating NEAT config...")
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    print("END:\tCreated NEAT config")

    # Generates all relevant agent populations
    print("START:\tCreating NEAT population...")
    population = neat.Population(config)
    pred_pop = int(len(population.population.items())*pred_percent)
    prey_pop = len(population.population.items()) - pred_pop
    if multi_model:
        pred_pop_no_neat = int(pred_pop * model_split)
        prey_pop_no_neat = int(prey_pop * model_split)
    else:
        pred_pop_no_neat = prey_pop_no_neat = 0
    print("END:\tCreated NEAT population")
    print(f"INFO:\tPredator population: {pred_pop}")
    print(f"INFO:\tPrey population: {prey_pop}")
    print(f"INFO:\tPredator population no neat: {pred_pop_no_neat}")
    print(f"INFO:\tPrey population no neat: {prey_pop_no_neat}")

    # Initializes the environment, whether the simulation will be run with multiple models or not
    print("START:\tInitializing environment...")

    env.initialize_environment(
        config=config,
        population=population,
        pred_pop=pred_pop,
        prey_pop=prey_pop,
        prey_pop_no_neat=prey_pop_no_neat,
        pred_pop_no_neat=pred_pop_no_neat,
        pred_spawn_bounds=pred_spawn_bounds,
        prey_spawn_bounds=prey_spawn_bounds,
        food_amount=food_amount
    )
    print("END:\tEnvironment initialized")

    # Initializes the logger
    print("INFO:\tStarting Logger...")
    logger.info(f"Starting simulation with {config.pop_size} agents...")
    logger.info(
        f"Using {env.max_workers} Logical CPU cores for parallel processing")

    return env, population, config, len(population.population.items()), pred_pop, prey_pop, pred_pop_no_neat, prey_pop_no_neat


def mutate(genome, config, env, population_size, pred_pop, prey_pop, pred_pop_no_neat, prey_pop_no_neat, pred_spawn_bounds,  prey_spawn_bounds, eliteism=0.1, crossover_rate=0.7, torunament_size=3):
    # Create separate lists for predators and prey
    predators = [agent for agent in env.agents if isinstance(
        agent, Predator) and agent.neat == True]
    preys = [agent for agent in env.agents if isinstance(
        agent, Prey) and agent.neat == True]
    no_neat_predators = [agent for agent in env.agents if isinstance(
        agent, Predator) and agent.neat == False]
    no_neat_preys = [agent for agent in env.agents if isinstance(
        agent, Prey) and agent.neat == False]
    logs.avg_agent_fitness(predators, preys, no_neat_predators, no_neat_preys)
    for agent in env.agents:
        if agent.neat_genome:
            agent.neat_genome.fitness = agent.fitness

    # Sort and retain the top 10% based on fitness
    top_predators = sorted(predators, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(pred_pop * eliteism))]
    top_preys = sorted(preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(prey_pop * eliteism))]
    top_predators_no_neat = sorted(no_neat_predators, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(pred_pop_no_neat * eliteism))]
    top_preys_no_neat = sorted(no_neat_preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(prey_pop_no_neat * eliteism))]

    # Number of offspring to create for predators and prey
    num_pred_offspring = int(pred_pop - len(top_predators))
    num_prey_offspring = int(prey_pop - len(top_preys))
    num_pred_offspring_no_neat = int(
        pred_pop_no_neat - len(top_predators_no_neat))
    num_prey_offspring_no_neat = int(
        prey_pop_no_neat - len(top_preys_no_neat))

    # Breed and mutate predators and prey
    new_predators = breed_and_mutate(config, top_predators, num_offspring=num_pred_offspring, multi_model=False,
                                     bounds=pred_spawn_bounds, crossover_rate=crossover_rate, torunament_size=torunament_size)
    new_preys = breed_and_mutate(config, top_preys,  num_offspring=num_prey_offspring, multi_model=False,
                                 bounds=prey_spawn_bounds, crossover_rate=crossover_rate, torunament_size=torunament_size)

    if prey_pop_no_neat > 0 and pred_pop_no_neat > 0:
        new_no_neat_preys = breed_and_mutate(config, top_preys_no_neat,  num_offspring=num_prey_offspring_no_neat, multi_model=True,
                                             bounds=prey_spawn_bounds, crossover_rate=crossover_rate, torunament_size=torunament_size)
        new_no_neat_preds = breed_and_mutate(config, top_predators_no_neat, num_offspring=num_pred_offspring_no_neat, multi_model=True,
                                             bounds=pred_spawn_bounds, crossover_rate=crossover_rate, torunament_size=torunament_size)

    # Replace the old population with the new one
    env.add_agents(top_predators + top_preys + new_predators + new_preys +
                   new_no_neat_preys + new_no_neat_preds + top_predators_no_neat + top_preys_no_neat)

# Main function, configures simulation then runs through epochs


def main():
    try:
        # scale bounds
        constants.BOUNDS = [
            bound * constants.SCALE_FACTOR for bound in constants.BOUNDS]
        constants.PREY_SPAWN_BOUNDS = [bound * constants.SCALE_FACTOR
                                       for bound in constants.PREY_SPAWN_BOUNDS]
        constants.PRED_SPAWN_BOUNDS = [
            bound * constants.SCALE_FACTOR for bound in constants.PRED_SPAWN_BOUNDS]

        # Creates simulation environment
        print("START:\tCreating simulation environment...")
        env, population, config, populationSize, pred_pop, prey_pop, pred_pop_no_neat, prey_pop_no_neat = create_simulation(
            simulation_type=constants.SIMULATION_TYPE,
            config_path=constants.CONFIG_PATH,
            steps=constants.STEPS,
            bounds=constants.BOUNDS,
            pred_percent=constants.PRED_PERCENT,
            food_amount=constants.FOOD_AMOUNT,
            prey_spawn_bounds=constants.PREY_SPAWN_BOUNDS,
            pred_spawn_bounds=constants.PRED_SPAWN_BOUNDS,
            food_respawn_rate=constants.FOOD_RESPAWN_RATE,
            multi_model=constants.MULTI_MODEL,
            model_split=constants.MODEL_SPLIT
        )
        print("END:\tSimulation environment created")

        # Create log for the average network size
        logs.log_avg_network_size(env.agents)

        # Run simulation, looping according to the number of epochs specified
        eliteism = constants.CUT_OFF  # Percentage of agents that will be used for breeding
        crossover_rate = constants.CROSS_OVER_RATE  # Crossover rate for breeding
        torunament_size = constants.TOURNAMENT_SIZE  # Tournament size for selection
        prey_spawn_bounds = constants.PREY_SPAWN_BOUNDS  # Spawn bounds for prey
        pred_spawn_bounds = constants.PRED_SPAWN_BOUNDS  # Spawn bounds for predators
        logs.save_initial_genomes_json(env.agents)
        for i in range(constants.EPOCHS):
            start_time = time.time()  # Start timing the epoch
            env.run()
            if i > constants.EPOCHS / 2 and constants.SWAP_BOUNDS:
                mutate(population, config, env, populationSize, pred_pop,
                       prey_pop, prey_pop_no_neat, pred_pop_no_neat, eliteism,
                       crossover_rate=crossover_rate,
                       torunament_size=torunament_size,
                       pred_spawn_bounds=prey_spawn_bounds,
                       prey_spawn_bounds=pred_spawn_bounds)
            else:
                mutate(population, config, env, populationSize, pred_pop,
                       prey_pop, prey_pop_no_neat, pred_pop_no_neat, eliteism,
                       crossover_rate=crossover_rate,
                       torunament_size=torunament_size,
                       pred_spawn_bounds=pred_spawn_bounds,
                       prey_spawn_bounds=prey_spawn_bounds)
            env.reset()
            end_time = time.time()  # End timing the epoch

            epoch_duration = end_time - start_time
            remaining_epochs = constants.EPOCHS - (i + 1)
            estimated_time_remaining = remaining_epochs * epoch_duration

            print(
                f"Epoch {i+1} completed, {constants.EPOCHS - i - 1} epochs remaining")
            estimated_time_remaining_hours = estimated_time_remaining / 3600
            epoch_duration_hours = epoch_duration / 3600
            print(
                f"Estimated time remaining: {estimated_time_remaining_hours:.2f} hours")
            logger.info(
                f"Epoch {i+1} completed in {epoch_duration_hours:.2f} hours")
            logger.info(
                f"Estimated time remaining: {estimated_time_remaining_hours:.2f} hours")

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
    info_handler = logging.FileHandler('./Logs/sim.log', mode='w')
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
