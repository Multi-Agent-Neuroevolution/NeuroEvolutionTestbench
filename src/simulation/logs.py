"""logs.py"""
# 5 different logging-related files are generated and stored in the Data folder. The files are:
# final_genomes.json - handled by save_genomes_json
# pred_genomes.pkl - handled by pickle_genomes
# prey_genomes.pkl - handled by pickle_genomes
# network_size_log.txt - handled by log_avg_network_size
# fitness.csv - handled by avg_agent_fitness

from agents import Predator, Prey
import numpy as np
import json
import pickle

# Definition for converting a genome to a dictionary, used in tandem with the genome JSON saving function below
def genome_to_dict(genome):
    # Convert connections' tuple keys into strings
    connections = {str(k): vars(v) for k, v in genome.connections.items()}

    # Returns the genome key, fitness, nodes, and connections its made
    return {'key': genome.key, 'fitness': genome.fitness, 'nodes': {k: vars(v) for k, v in genome.nodes.items()}, 'connections': connections}

# Definition for saving the final agent genomes to a JSON file
def save_genomes_json(agents):
    # Convert each agent's genome to a dictionary using the genome_to_dict def
    genomes = [genome_to_dict(agent.neat_genome) for agent in agents]

    with open('./Data/final_genomes.json', 'w') as file:
        json.dump(genomes, file, indent=4)

# Definition for saving genomes to a pickle file
def pickle_genomes(agents):
    # Genomes from predators
    with open('./Data/pred_genomes.pkl', 'wb') as f:
        pickle.dump([agent.neat_genome for agent in agents if isinstance(agent, Predator)], f)
    
    # Genomes from preys
    with open('./Data/prey_genomes.pkl', 'wb') as f:
        pickle.dump([agent.neat_genome for agent in agents if isinstance(agent, Prey)], f)

# Definition for logging the average network size to a text file
def log_avg_network_size(agents):
    # Initialize local variables
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
    with open('./Data/network_size_log.txt', 'a') as file:
        file.write(f"Avg nodes: {avg_nodes}, Avg connections: {avg_connections}\n")

# Definition for saving the average fitness of predators and preys population to a CSV file
def avg_agent_fitness(predators, preys):
    avg_pred_fitness = np.mean([predator.fitness for predator in predators])
    avg_prey_fitness = np.mean([prey.fitness for prey in preys])
    with open('./Data/fitness.csv', 'a') as f:
        f.write(f"{avg_pred_fitness},{avg_prey_fitness}\n")