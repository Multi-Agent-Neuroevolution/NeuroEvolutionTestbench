import random
import neat
import numpy as np
import matplotlib.pyplot as plt
from agent import Agent
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

    # Create agents
    agents = []
    objects = []

    # ADRIAN: this formatting scares me : (
    # Add food
    for i in range(food_amount):
        objects.append(Obstacle(
            np.array([np.random.uniform(bounds[0], bounds[1]),
                      # Center of the rectangle
                      np.random.uniform(bounds[2], bounds[3])]),
            "food",
            False,  # hasCollision
            "green",  # color
            True,  # interactible
            False,  # isGoal
            "circle",
            1,     # radius (0 for rectangle)
            0,    # width
            0     # height
        ))
    objects.append(Obstacle(
        np.array([0, 0]),  # Center of the rectangle
        "obstacle",
        True,  # hasCollision
        "red",  # color
        False,  # interactible
        False,  # isGoal
        "rectangle",
        0,     # radius (0 for rectangle)
        100,    # width
        45     # height
    ))
    # Create agents with genomes
    for i in range(pred_pop):
        pos = np.array([np.random.uniform(pred_spawn_bounds[0], pred_spawn_bounds[1]),
                        np.random.uniform(pred_spawn_bounds[2], pred_spawn_bounds[3])])
        genome = population.population[i+1]
        agent = Predator(i, "NEAT", "PRED_PREY", pos, genome, config)
        agents.append(agent)
    for i in range(prey_pop):
        pos = np.array([np.random.uniform(prey_spawn_bounds[0], prey_spawn_bounds[1]),
                        np.random.uniform(prey_spawn_bounds[2], prey_spawn_bounds[3])])
        genome = population.population[i + pred_pop]
        agent = Prey(i + pred_pop, "NEAT",
                     "PRED_PREY", pos, genome, config)
        agents.append(agent)

    # Add agents and obstacles to environment
    env.add_agents(agents)
    env.add_obstacles(objects)

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
    logs.log_avg_network_size(env.agents)
    logs.log_agent_alive(env.agents)

    # Sort and retain the top 10% based on fitness
    top_predators = sorted(predators, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(predators) * 0.1))]
    top_preys = sorted(preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(preys) * 0.1))]

    # ADRIAN: I'm not touching this but does this def have to be nested?
    # Function to breed and mutate agents
    def breed_and_mutate(parents, is_predator, num_offspring):
        new_agents = []
        if len(parents) == 0:
            # generate new parents randomly
            for _ in range(num_offspring):
                # Create a child genome by crossover
                child_id = random.randint(0, 100000)
                child_genome = neat.DefaultGenome(child_id)
                child_genome.configure_new(config.genome_config)
                pos = (random.randint(0, 100), random.randint(
                    0, 100))  # Random position
                if is_predator:
                    new_agent = Predator(
                        child_id, "NEAT", "PRED_PREY", pos, child_genome, config)
                else:
                    new_agent = Prey(child_id, "NEAT",
                                     "PRED_PREY", pos, child_genome, config)
                new_agents.append(new_agent)
        else:
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
                    new_agent = Prey(child_id, "NEAT",
                                     "PRED_PREY", pos, child_genome, config)
                new_agents.append(new_agent)

        return new_agents

    # Number of offspring to create for predators and prey
    num_pred_offspring = int(pred_pop - len(top_predators))
    num_prey_offspring = int(prey_pop - len(top_preys))

    # Breed and mutate predators and prey
    new_predators = breed_and_mutate(
        top_predators, is_predator=True, num_offspring=num_pred_offspring)
    new_preys = breed_and_mutate(
        top_preys, is_predator=False, num_offspring=num_prey_offspring)

    # Replace the old population with the new one
    env.overwrite_agents(top_predators + top_preys + new_predators + new_preys)

# Main function, configures simulation then runs through epochs


def main():
    try:
        # delete logs and previous genomes
        logs.delete_logs()
        # Configuration constants (parameters)
        SIMULATION_TYPE = "PRED_PREY"
        CONFIG_PATH = "./Config/balls.conf"  # Path to your NEAT config file
        STEPS = 1500
        EPOCHS = 400
        BOUNDS = [-200, 200, -200, 200]
        PREY_SPAWN_BOUNDS = [-150, 150, 50, 150]
        PRED_SPAWN_BOUNDS = [-150, 150, -150, -50]
        RATIO = 0.75
        FOODAMOUNT = 500
        FOOD_RESPAWN_RATE = 0.1
        pred_percent = 1 - RATIO

        # Creates simulation environment
        env, population, config, populationSize, pred_pop, prey_pop = create_simulation(
            simulation_type=SIMULATION_TYPE, config_path=CONFIG_PATH, steps=STEPS, bounds=BOUNDS, pred_percent=pred_percent, food_amount=FOODAMOUNT, prey_spawn_bounds=PREY_SPAWN_BOUNDS, pred_spawn_bounds=PRED_SPAWN_BOUNDS, food_respawn_rate=FOOD_RESPAWN_RATE)

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
