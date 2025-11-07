"""evolution_utils.py"""
import random
import neat
import copy
from agents import Predator, Prey
import logging
logger = logging.getLogger(__name__)

# This function handles selecting parents to breed, then mutating the resultant child's genome


def breed_and_mutate(config, parents, num_offspring, bounds, multi_model, crossover_rate=0.7, torunament_size=3, subclass=None):
    new_agents = []
    used_ids = set()  # Hashing for  unique IDs

    type = 0 if multi_model else 1
    extinction = False

    def generate_unique_id():
        # Determine ID range once outside the loop
        if subclass == "predator":
            id_range = (50001, 100000) if type == 0 else (0, 50000)
        elif subclass == "prey":
            id_range = (150001, 200000) if type == 0 else (100001, 150000)
        else:
            return random.randint(0, 1000000)  # Fallback

        while True:
            child_id = random.randint(id_range[0], id_range[1])
            if child_id not in used_ids:
                used_ids.add(child_id)
                return child_id

    for _ in range(num_offspring):
        child_id = generate_unique_id()

        # Create a new genome and mutate it
        child_genome = neat.DefaultGenome(child_id)

        if not parents:
            # EXTINCTION: Create and mutate a new genome from scratch
            extinction = True
            child_genome.configure_new(config.genome_config)
            child_genome.mutate(config.genome_config)

            pos = [random.uniform(bounds[0], bounds[1]),
                   random.uniform(bounds[0], bounds[1])]

            # Randomly decide whether it's a predator or prey
            if subclass == "predator":
                new_agent = Predator(id=child_id, pos=pos,
                                     neat_genome=child_genome, neat_config=config, type=type)
            if subclass == "prey":
                new_agent = Prey(id=child_id, pos=pos,
                                 neat_genome=child_genome, neat_config=config, type=type)

            new_agents.append(new_agent)
            continue

        # Either clone a parent or perform crossover
        if random.random() > (min(0.0, (1 - crossover_rate))) or len(parents) < 2:
            parent = random.choice(parents)
            child_genome.configure_crossover(
                parent.neat_genome, parent.neat_genome, config)
        else:
            parent1 = select_parent(parents, torunament_size)
            parent2 = select_parent(parents, torunament_size)
            child_genome.configure_crossover(
                parent1.neat_genome, parent2.neat_genome, config)

        # Mutate the child genome. This sometimes fails so we need to catch the exception. This is a band-aid solution
        # TODO: Find out whats causing the mutation to fail and fix it
        try:
            child_genome.mutate(config.genome_config)
        except Exception as e:
            print(f"Error during mutation of agent type: {type},  {e}")
            continue

        pos = [random.uniform(bounds[0], bounds[1]),
               random.uniform(bounds[0], bounds[1])]

        if subclass == "predator":
            new_agent = Predator(id=child_id, pos=pos,
                                 neat_genome=child_genome, neat_config=config if multi_model else config, type=type)
        if subclass == "prey":
            new_agent = Prey(id=child_id, pos=pos,
                             neat_genome=child_genome, neat_config=config if multi_model else config, type=type)

        new_agents.append(new_agent)
        if extinction:
            print(
                f"EXTINCTION EVENT: Agents of type {subclass} have gone extinct. If frequent, this will harm training progress. Change Configs?")
            logger.info(
                f"EXTINCTION EVENT: Agents of type {subclass} have gone extinct. If frequent, this will harm training progress. Change Configs?")
            extinction = False
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
