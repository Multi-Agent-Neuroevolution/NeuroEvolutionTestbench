import random, neat
from predator_prey import Predator, Prey

# This function handles selecting parents to breed, then mutating the resultant child's genome
def breed_and_mutate(config, parents, is_predator, num_offspring):
    new_agents = []

    for _ in range(num_offspring):
        child_id = random.randint(0, 100000)
        child_genome = neat.DefaultGenome(child_id)
        pos = (random.randint(0, 100), random.randint(0, 100))  # Random position

        # If there are no parents available(?), a new genome is created.
        # Otherwise, two parents are selected to breed and the child genome is created by crossover, then mutated
        if len(parents) == 0:
            child_genome.configure_new(config.genome_config)
        else:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child_genome.configure_crossover(parent1.neat_genome, parent2.neat_genome, config)
            child_genome.mutate(config.genome_config)

        # This determines whether the new agent is a predator or prey
        if is_predator:
            new_agent = Predator(child_id, "NEAT", "PRED_PREY", "PRED", pos, child_genome, config)
        else:
            new_agent = Prey(child_id, "NEAT", "PRED_PREY", "PREY", pos, child_genome, config)

        new_agents.append(new_agent)
                
    return new_agents