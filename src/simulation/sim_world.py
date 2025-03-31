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
    print("END:\tCreated {} predators and {} preys".format(pred_pop, prey_pop))

    # Initializes the environment, whether the simulation will be run with multiple models or not
    print("START:\tInitializing environment...")
    if multi_model:
        pred_pop_no_neat = int(pred_pop * model_split)
        prey_pop_no_neat = int(prey_pop * model_split)
    else:
        pred_pop_no_neat = prey_pop_no_neat = 0
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


def mutate(genome, config, env, population_size, pred_pop, prey_pop, eliteism=0.1, pred_pop_no_neat=0, prey_pop_no_neat=0):
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
        :max(1, int(len(predators) * eliteism))]
    top_preys = sorted(preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(preys) * eliteism))]

    # Sort and retain no neat population
    top_predators_no_neat = sorted(predators, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(predators) * eliteism)) + pred_pop_no_neat]
    top_preys_no_neat = sorted(preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(preys) * eliteism)) + prey_pop_no_neat]

    # Number of offspring to create for predators and prey
    num_pred_offspring = int(pred_pop - len(top_predators))
    num_prey_offspring = int(prey_pop - len(top_preys))
    num_pred_offspring_no_neat = int(
        pred_pop_no_neat - len(top_predators_no_neat))
    num_prey_offspring_no_neat = int(
        prey_pop_no_neat - len(top_preys_no_neat))

    # Breed and mutate predators and prey
    new_predators = breed_and_mutate(config, top_predators, num_offspring=num_pred_offspring,
                                     bounds=constants.PRED_SPAWN_BOUNDS)
    new_preys = breed_and_mutate(config, top_preys,  num_offspring=num_prey_offspring,
                                 bounds=constants.PREy_SPAWN_BOUNDS)
    if prey_pop_no_neat > 0:
        new_no_neat_preys = breed_and_mutate(config, top_preys_no_neat,  num_offspring=num_prey_offspring_no_neat,
                                             bounds=constants.PREY_SPAWN_BOUNDS)
    if pred_pop_no_neat > 0:
        new_no_neat_preds = breed_and_mutate(config, top_predators_no_neat, num_offspring=num_pred_offspring_no_neat,
                                             bounds=constants.PRED_SPAWN_BOUNDS)

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
        for i in range(constants.EPOCHS):
            env.run()
            # TO DO: this can probably be moved to environment.py
            mutate(population, config, env, populationSize, pred_pop,
                   prey_pop, prey_pop_no_neat, pred_pop_no_neat)
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
