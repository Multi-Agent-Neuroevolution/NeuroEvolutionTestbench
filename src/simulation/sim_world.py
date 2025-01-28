import random
import neat
import numpy as np
import matplotlib.pyplot as plt
from agent import Agent
from predator_prey import Predator, Prey
from enviroment import Environment, Obstacle
import multiprocessing
import pickle
import json
import logging

logger = logging.getLogger(__name__)


def create_simulation(simulation_type="PRED_PREY", config_path=None, steps=1000, bounds=[-200, 200, -200, 200], pred_percent=0.25, food_amount=10):
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
    pred_pop = int(len(population.population.items())*pred_percent)
    print(pred_pop)
    print(len(population.population.items()))
    prey_pop = len(population.population.items()) - pred_pop

    # Create agents
    agents = []
    objects = []

    # Add food
    for i in range(food_amount):
        objects.append(Obstacle(
            np.array([np.random.uniform(bounds[0], bounds[1]),
                      np.random.uniform(bounds[2], bounds[3])]),  # Center of the rectangle
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

    # Create agents with genomes
    for i in range(pred_pop):
        pos = np.array([np.random.uniform(bounds[0], bounds[1]),
                        np.random.uniform(bounds[2], bounds[3])])
        genome = population.population[i+1]
        agent = Predator(i, "NEAT", "PRED_PREY", pos, genome, config)
        agents.append(agent)
    for i in range(prey_pop):
        pos = np.array([np.random.uniform(bounds[0], bounds[1]),
                        np.random.uniform(bounds[2], bounds[3])])
        genome = population.population[i + pred_pop]
        agent = Prey(i + pred_pop, "NEAT",
                     "PRED_PREY", pos, genome, config)
        agents.append(agent)

    # Add agents and obstacles to environment
    env.add_agents(agents)
    env.add_obstacles(objects)
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
    num_pred_offspring = int(pred_pop - len(top_predators))
    num_prey_offspring = int(prey_pop - len(top_preys))

    # Breed and mutate predators and prey
    new_predators = breed_and_mutate(
        top_predators, is_predator=True, num_offspring=num_pred_offspring)
    new_preys = breed_and_mutate(
        top_preys, is_predator=False, num_offspring=num_prey_offspring)

    # Replace the old population with the new one
    env.overwrite_agents(top_predators + top_preys + new_predators + new_preys)


def genome_to_dict(genome):
    # Convert connections' tuple keys into strings
    connections = {str(k): vars(v) for k, v in genome.connections.items()}

    return {
        'key': genome.key,
        'fitness': genome.fitness,
        'nodes': {k: vars(v) for k, v in genome.nodes.items()},
        'connections': connections  # Use the stringified keys for connections
    }


def save_genomes_json(agents, file_path):
    genomes = [genome_to_dict(agent.neat_genome) for agent in agents]
    with open(file_path, 'w') as f:
        json.dump(genomes, f, indent=4)


def log_avg_network_size(agents):
    total_nodes = 0
    total_connections = 0
    total_agents = len(agents)

    # Loop through all agents and sum their network sizes
    for agent in agents:
        genome = agent.neat_genome
        num_nodes = len(genome.nodes)
        num_connections = len(genome.connections)

        total_nodes += num_nodes
        total_connections += num_connections

    # Calculate average size
    avg_nodes = total_nodes / total_agents if total_agents > 0 else 0
    avg_connections = total_connections / total_agents if total_agents > 0 else 0

    # Log the average network size
    print(f"Average number of nodes: {avg_nodes}")
    print(f"Average number of connections: {avg_connections}")

    # Optionally, write to a log file
    with open('./Data/network_size_log.txt', 'a') as log_file:
        log_file.write(
            f"Avg nodes: {avg_nodes}, Avg connections: {avg_connections}\n")


def main():
    try:
        # Configuration
        SIMULATION_TYPE = "PRED_PREY"
        CONFIG_PATH = "./Config/balls.conf"  # Path to your NEAT config file
        STEPS = 500
        EPOCHS = 50
        BOUNDS = [-200, 200, -200, 200]
        RATIO = 0.75
        FOODAMOUNT = 400
        pred_percent = 1 - RATIO
        # Create simulation
        env, population, config, populationSize, pred_pop, prey_pop = create_simulation(
            simulation_type=SIMULATION_TYPE, config_path=CONFIG_PATH, steps=STEPS, bounds=BOUNDS, pred_percent=pred_percent, food_amount=FOODAMOUNT)

        # Run the simulation
        log_avg_network_size(env.agents)
        for i in range(EPOCHS):
            env.run()
            mutate(population, config, env, populationSize, pred_pop, prey_pop)
            env.reset()
            print(f"Epoch {i+1} completed")
            logger.info(f"Epoch {i+1} completed")
        # save the pred and prey genomes
        with open('./Data/pred_genomes.pkl', 'wb') as f:
            pickle.dump([agent.neat_genome for agent in env.agents if isinstance(
                agent, Predator)], f)
        with open('./Data/prey_genomes.pkl', 'wb') as f:
            pickle.dump([agent.neat_genome for agent in env.agents if isinstance(
                agent, Prey)], f)
        # save the final genomes to json
        save_genomes_json(env.agents, './Data/final_genomes.json')
        log_avg_network_size(env.agents)
    except KeyboardInterrupt:
        logger.info("\nSimulation terminated by user")
    except Exception as e:
        logger.info(f"Error during simulation: {str(e)}")
        raise


if __name__ == "__main__":
    logging.basicConfig(filename='./Logs/sim.log', level=logging.INFO)
    logger.info('started')
    main()
