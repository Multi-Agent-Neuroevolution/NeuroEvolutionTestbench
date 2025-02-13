import random, neat
from predator_prey import Predator, Prey

# This function handles selecting parents to breed, then mutating the resultant child's genome
def breed_and_mutate(config, parents, is_predator, num_offspring):
    new_agents = []
    if len(parents) == 0:
        # generate new parents randomly
        for _ in range(num_offspring):
            # Create a child genome by crossover
            child_id = random.randint(0, 100000)
            child_genome = neat.DefaultGenome(child_id)
            child_genome.configure_new(config.genome_config)
            pos = (random.randint(0, 100), random.randint(0, 100))  # Random position
            if is_predator:
                new_agent = Predator(child_id, "NEAT", "PRED_PREY", pos, child_genome, config)
            else:
                new_agent = Prey(child_id, "NEAT", "PRED_PREY", pos, child_genome, config)
            new_agents.append(new_agent)
    else:
        for _ in range(num_offspring):
            # Select two random parents
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)

            # Create a child genome by crossover
            child_id = random.randint(0, 100000)  # Generate a unique ID
            child_genome = neat.DefaultGenome(child_id)
            child_genome.configure_crossover(parent1.neat_genome, parent2.neat_genome, config)

            # Mutate the child's genome
            child_genome.mutate(config.genome_config)

            # Create a new agent based on the child genome
            pos = (random.randint(0, 100), random.randint(0, 100))  # Random position
            if is_predator:
                new_agent = Predator(child_id, "NEAT", "PRED_PREY", pos, child_genome, config)
            else:
                new_agent = Prey(child_id, "NEAT", "PRED_PREY", pos, child_genome, config)
            new_agents.append(new_agent)
                
    return new_agents