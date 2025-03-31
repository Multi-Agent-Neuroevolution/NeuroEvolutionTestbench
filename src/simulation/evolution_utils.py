"""evolution_utils.py"""
import random
import neat
from agents import Predator, Prey

# This function handles selecting parents to breed, then mutating the resultant child's genome


def breed_and_mutate(config, parents, num_offspring, bounds, multi_model=False, model_split=0.5):
    new_agents = []

    for _ in range(num_offspring):
        child_id = random.randint(0, 100000)
        child_genome = neat.DefaultGenome(child_id)

        # If there are no parents available(?), a new genome is created.
        # Otherwise, two parents are selected to breed and the child genome is created by crossover, then mutated
        if multi_model:
            config.genome_config.__dict__['conn_add_prob'] = 0
            config.genome_config.__dict__['conn_delete_prob'] = 0
            config.genome_config.__dict__['node_add_prob'] = 0
            config.genome_config.__dict__['node_delete_prob'] = 0
        if len(parents) == 0:
            child_genome.configure_new(config.genome_config)
        else:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child_genome.configure_crossover(
                parent1.neat_genome, parent2.neat_genome, config)
            child_genome.mutate(config.genome_config)

        # This determines whether the new agent is a predator or prey
        pos = [random.uniform(bounds[0], bounds[1]),
               random.uniform(bounds[0], bounds[1])]
        if parent1 is isinstance(Predator):
            new_agent = Predator(id=child_id, pos=pos,
                                 neat_genome=child_genome, neat_config=config)
        else:
            new_agent = Prey(id=child_id, pos=pos,
                             neat_genome=child_genome, neat_config=config)

        new_agents.append(new_agent)

        return new_agents
