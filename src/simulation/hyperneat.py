"""
hyperneat.py

Implements HyperNEAT offspring generation for Predator and Prey agents.
"""

import random
import neat
import numpy as np
from agents import Predator, Prey


def create_substrate(schema):
    """
    Create a HyperNEAT Substrate given a coordinate schema.

    Schema format:
        {
            'inputs': [(x1, y1), ...],   # normalized [-1,1] coordinates
            'outputs': [(x2, y2), ...]
        }
    """
    try:
        from neat.hyperneat import Substrate

    except ImportError:
        raise ImportError(
            "HyperNEAT extension not found. Install neat-incubator or equivalent.")
    return Substrate(input_coordinates=schema['inputs'], output_coordinates=schema['outputs'])


def generate_hyperneat_offspring(hyperneat_cfg, num_offspring, bounds, substrate_schema, subclass):
    """
    Generate new agents using HyperNEAT.

    Args:
        hyperneat_cfg (neat.Config): Configuration for CPPN and substrate parameters.
        num_offspring (int): Number of offspring to generate.
        bounds (tuple): (xmin, xmax, ymin, ymax) spawn area.
        substrate_schema (dict): Defines 'inputs' and 'outputs' coords for the substrate.
        subclass (str): 'predator' or 'prey'.

    Returns:
        List[Agent]: Newly created Predator or Prey instances with hyperneat brains.
    """
    new_agents = []
    for _ in range(num_offspring):
        # Create and mutate a new CPPN genome
        cppn_id = random.randint(1, 1_000_000)
        cppn = neat.DefaultGenome(cppn_id)
        cppn.configure_new(hyperneat_cfg.genome_config)
        cppn.mutate(hyperneat_cfg.genome_config)

        # Build substrate and generate phenome
        substrate = create_substrate(substrate_schema)
        try:
            phenome = neat.nn.HyperNEATNetwork.create(
                cppn, hyperneat_cfg, substrate)
        except AttributeError:
            raise RuntimeError(
                "HyperNEATNetwork not available; ensure hyperneat support is installed.")

        # Random spawn position
        x = random.uniform(bounds[0], bounds[1])
        y = random.uniform(bounds[2], bounds[3])
        pos = np.array([x, y])

        # Instantiate appropriate agent
        agent_id = cppn.key
        if subclass == 'predator':
            agent = Predator(id=agent_id, pos=pos, neat_genome=cppn,
                             neat_config=hyperneat_cfg, type=2)
        else:
            agent = Prey(id=agent_id, pos=pos, neat_genome=cppn,
                         neat_config=hyperneat_cfg, type=2)

        # Override the agent's brain to use the HyperNEAT phenome
        agent.brain = phenome
        new_agents.append(agent)

    return new_agents

# Integration notes:
# 1) In evolution_utils.py, import:
#       from hyperneat_utils import generate_hyperneat_offspring
# 2) Define a substrate schema (e.g., in constants.py or config):
#       HYPERNEAT_SUBSTRATE_SCHEMA = {
#           'inputs': [(-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)],
#           'outputs': [(0.0, 0.0), ...]
#       }
# 3) In server.evolve_all, replace the HyperNEAT stub:
#       elif flag == 2:
#           offspring = generate_hyperneat_offspring(
#               cfg,
#               num_offspring,
#               bounds,
#               HYPERNEAT_SUBSTRATE_SCHEMA,
#               subclass
#           )
# 4) Ensure neat-incubator or another HyperNEAT extension is installed and available.
