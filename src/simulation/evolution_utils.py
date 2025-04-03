"""evolution_utils.py"""
import random
import neat
import copy
from agents import Predator, Prey

# This function handles selecting parents to breed, then mutating the resultant child's genome


def breed_and_mutate(config, parents, num_offspring, bounds, multi_model, crossover_rate=0.7, torunament_size=3):
    new_agents = []
    configCopy = copy.deepcopy(config)
    used_ids = set()  # HashSet to ensure unique IDs

    def generate_unique_id():
        while True:
            child_id = random.randint(0, 100000)
            if child_id not in used_ids:
                used_ids.add(child_id)
                return child_id

    for _ in range(num_offspring):
        child_id = generate_unique_id()
        child_genome = neat.DefaultGenome(child_id)

        # If there are no parents available(?), a new genome is created.
        # Otherwise, two parents are selected to breed and the child genome is created by crossover, then mutated
        if multi_model == True:
            configCopy.genome_config.__dict__['conn_add_prob'] = 0
            configCopy.genome_config.__dict__['conn_delete_prob'] = 0
            configCopy.genome_config.__dict__['node_add_prob'] = 0
            configCopy.genome_config.__dict__['node_delete_prob'] = 0

            if random.random() > crossover_rate or len(parents) < 2:
                # Clone a parent with mutation only
                parent = random.choice(parents)
                child_genome = neat.DefaultGenome(child_id)
                child_genome.configure_crossover(
                    parent.neat_genome, parent.neat_genome, config)  # Self-crossover is cloning
            else:
                # Normal crossover
                parent1 = select_parent(parents, torunament_size)
                parent2 = select_parent(parents, torunament_size)
                child_genome = neat.DefaultGenome(child_id)
                child_genome.configure_crossover(
                    parent1.neat_genome, parent2.neat_genome, config)

            # Always mutate
            child_genome.mutate(config.genome_config)

            # This determines whether the new agent is a predator or prey
            pos = [random.uniform(bounds[0], bounds[1]),
                   random.uniform(bounds[0], bounds[1])]

            if isinstance(parents[1], Predator):
                new_agent = Predator(id=child_id, pos=pos,
                                     neat_genome=child_genome, neat_config=configCopy, neat=False)
            else:
                new_agent = Prey(id=child_id, pos=pos,
                                 neat_genome=child_genome, neat_config=configCopy, neat=False)

            new_agents.append(new_agent)
        else:
            if random.random() > crossover_rate or len(parents) < 2:
                # Clone a parent with mutation only
                parent = random.choice(parents)
                child_genome = neat.DefaultGenome(child_id)
                child_genome.configure_crossover(
                    parent.neat_genome, parent.neat_genome, config)  # Self-crossover is cloning
            else:
                # Normal crossover
                parent1 = select_parent(parents, torunament_size)
                parent2 = select_parent(parents, torunament_size)
                child_genome = neat.DefaultGenome(child_id)
                child_genome.configure_crossover(
                    parent1.neat_genome, parent2.neat_genome, config)

            # Always mutate
            child_genome.mutate(config.genome_config)

            # This determines whether the new agent is a predator or prey
            pos = [random.uniform(bounds[0], bounds[1]),
                   random.uniform(bounds[0], bounds[1])]

            if isinstance(parents[1], Predator):
                new_agent = Predator(id=child_id, pos=pos,
                                     neat_genome=child_genome, neat_config=config, neat=True)
            else:
                new_agent = Prey(id=child_id, pos=pos,
                                 neat_genome=child_genome, neat_config=config, neat=True)

            new_agents.append(new_agent)
    return new_agents


def select_parent(parents, tournament_size):
    """Selects a parent from the list of parents using tournament selection.

    Args:
        parents (list): A list of all parents in the simulation.

    Returns:
        object: A randomly selected parent.
    """
    tournament = random.sample(parents, min(tournament_size, len(parents)))
    winner = max(tournament, key=lambda x: x.fitness)
    return winner
