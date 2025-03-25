"""logs.py is where the logging functions are defined.

These functions are used to log data about the simulation, such as:
- the average network size of the agents
- the average fitness of the predator and prey populations
- and the final agent genomes. 

The functions are called from sim_world.py to log data at different stages of the simulation.
"""
from agents import Predator, Prey
import numpy as np
import json
import pickle


def genome_to_dict(genome):
    """Converts a genome to a dictionary, used in tandem with the save_genomes_json function.

    Args:
        genome (neat.genome.DefaultGenome): The genome to convert to a dictionary.

    Returns:
        dict: A dictionary representation of the genome.
    """
    connections = {str(k): vars(v) for k, v in genome.connections.items()}
    return {'key': genome.key, 'fitness': genome.fitness, 'nodes': {k: vars(v) for k, v in genome.nodes.items()}, 'connections': connections}


def save_genomes_json(agents):
    """Saves the final agent genomes to a JSON file.

    Args:
        agents (list): A list of all agents in the simulation.
    """
    genomes = [genome_to_dict(agent.neat_genome) for agent in agents]
    with open('./Data/final_genomes.json', 'w') as file:
        json.dump(genomes, file, indent=4)


def pickle_genomes(agents):
    """Saves the final agent genomes to a pickle file.

    Args:
        agents (list): A list of all agents in the simulation.
    """
    # Genomes from predators
    with open('./Data/pred_genomes.pkl', 'wb') as f:
        pickle.dump(
            [agent.neat_genome for agent in agents if isinstance(agent, Predator)], f)

    # Genomes from preys
    with open('./Data/prey_genomes.pkl', 'wb') as f:
        pickle.dump(
            [agent.neat_genome for agent in agents if isinstance(agent, Prey)], f)


def log_avg_network_size(agents):
    """Logs the average network size of the agents to a text file.

    Args:
        agents (list): A list of all agents in the simulation.
    """
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

    # Log the average network size, both in console and to text file
    print(f"Average number of nodes: {avg_nodes}")
    print(f"Average number of connections: {avg_connections}")
    with open('./Data/network_size_log.txt', 'w') as file:
        file.write(
            f"Avg nodes: {avg_nodes}, Avg connections: {avg_connections}\n")


def avg_agent_fitness(predators, preys):
    """Saves the average fitness of the predator and prey populations to a CSV file.

    Args:
        predators (list): A list of all predators in the simulation.
        preys (list): A list of all preys in the simulation.
    """
    avg_pred_fitness = np.mean([predator.fitness for predator in predators])
    avg_prey_fitness = np.mean([prey.fitness for prey in preys])
    with open('./Data/fitness.csv', 'a') as f:
        f.write(f"{avg_pred_fitness},{avg_prey_fitness}\n")
