"""
hyperneat_utils.py

Manual HyperNEAT implementation using PyTorch-based CPPN (no NEAT dependency).
Generates a feed-forward substrate network (Phenome) by querying a CPPN on coordinate pairs.
Agents receive a `.brain.activate(inputs)` API matching NEAT-Python.
"""

import torch
import torch.nn as nn
import random
import numpy as np
from agents import Predator, Prey


def create_substrate(schema):
    """
    From schema dict, return input coords list, output coords list, and all (input,output) pairs.

    schema format:
      'inputs': [(x1,y1), ...],
      'outputs': [(x2,y2), ...]

    Returns:
        inputs, outputs, pairs
    """
    inputs = schema['inputs']
    outputs = schema['outputs']
    pairs = [(ic, oc) for ic in inputs for oc in outputs]
    return inputs, outputs, pairs


def create_schema_from_inputs_outputs():
    max_closest = 5
    feature_dims = 7
    input_dim = max_closest * feature_dims + 1    # 36
    n_actions = 5                                 # e.g. from your genome config

    # 2) Lay out the inputs on a grid in [-1,1]²
    grid_size = int(np.ceil(np.sqrt(input_dim)))      # 6
    xs = np.linspace(-1, 1, grid_size)
    ys = np.linspace(-1, 1, grid_size)
    inputs = [(float(xs[i//grid_size]), float(ys[i % grid_size]))
              for i in range(input_dim)]

    # 3) Position outputs along the top edge (or any pattern you choose)
    outputs = [(-1 + 2*i/(n_actions-1), 1.0) for i in range(n_actions)]

    # 4) Bundle into your schema dict
    HYPER_NEAT_SCHEMA = {
        'inputs': inputs,
        'outputs': outputs
    }
    return HYPER_NEAT_SCHEMA


class CPPN(nn.Module):
    """
    A small feed-forward CPPN: tanh activations on hidden layers, linear output.
    """

    def __init__(self, input_dim=4, hidden_dims=[16, 16], output_dim=1):
        super().__init__()
        dims = [input_dim] + hidden_dims + [output_dim]
        self.layers = nn.ModuleList([
            nn.Linear(dims[i], dims[i+1]) for i in range(len(dims)-1)
        ])

    def forward(self, x):
        for lyr in self.layers[:-1]:
            x = torch.tanh(lyr(x))
        return self.layers[-1](x)

    def mutate(self, std=0.1):
        with torch.no_grad():
            for p in self.parameters():
                p.add_(torch.randn_like(p) * std)


class HyperNEATPhenome:
    """
    Phenotype network built from a substrate weight matrix.
    Provides `activate(inputs)` method like NEAT-Python.
    """

    def __init__(self, weight_matrix: np.ndarray):
        # weight_matrix shape (n_outputs, n_inputs)
        self.weights = weight_matrix

    def activate(self, inputs):
        x = np.array(inputs, dtype=np.float32)
        out = self.weights.dot(x)
        return out.tolist()


def generate_hyperneat_offspring(
    cfg,
    num_offspring,
    bounds,
    substrate_schema,
    subclass
):
    """
    Manually evolve CPPN and assign agent.brain to a HyperNEATPhenome.

    cfg keys:
      - 'hidden_dims': list[int]
      - 'mutate_std': float
    bounds: (xmin, xmax, ymin, ymax)
    """
    new_agents = []
    # correctly unpack create_substrate
    inputs, outputs, pairs = create_substrate(substrate_schema)
    n_in = len(inputs)
    n_out = len(outputs)

    for _ in range(num_offspring):
        # init & mutate CPPN
        cppn = CPPN(
            input_dim=4,
            hidden_dims=cfg.get('hidden_dims', [16, 16]),
            output_dim=1
        )
        cppn.mutate(std=cfg.get('mutate_std', 0.1))

        # compute substrate weight matrix
        weights = []
        for ic, oc in pairs:
            ix, iy = ic
            ox, oy = oc
            inp_tensor = torch.tensor([ix, iy, ox, oy], dtype=torch.float32)
            w = cppn(inp_tensor).item()
            weights.append(w)
        matrix = np.array(weights, dtype=np.float32).reshape(n_out, n_in)

        # wrap in phenome
        phenome = HyperNEATPhenome(matrix)

        # spawn location
        x = random.uniform(bounds[0], bounds[1])
        y = random.uniform(bounds[2], bounds[3])
        pos = np.array([x, y], dtype=np.float32)

        # instantiate agent
        agent_id = random.randint(1, 1_000_000)
        agent_cls = Predator if subclass == 'predator' else Prey
        agent = agent_cls(id=agent_id, pos=pos,
                          neat_genome=None, neat_config=None, type=2)

        # assign brain
        agent.brain = phenome
        new_agents.append(agent)

    return new_agents
