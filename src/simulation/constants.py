"""constants.py"""
# Parameters for simulation creation
SIMULATION_TYPE = "PRED_PREY"
CONFIG_PATH = "./Config/neat.conf"
HYPERNEAT_CONFIG_PATH = "./Config/hypr.conf"
STEPS = 250
BOUNDS = [-200, 200, -200, 200]  # Bounds for the environment

# Parameters for agents
# Ratio of predators to prey higher values mean more prey than predators.
RATIO = 0.75
PRED_PERCENT = 1 - RATIO
FOOD_AMOUNT = 1650  # Amount of food in the environment for prey to eat
PREY_SPAWN_BOUNDS = [-100, 100, 100, 25]
PRED_SPAWN_BOUNDS = [150, -150, -150, -50]
# Causes the predator and prey spawn bounds to be swapped at the halfway point of the simulation
SWAP_BOUNDS = True
# Rate at which food respawns, 0.1 = 10% chance of respawning each step
FOOD_RESPAWN_RATE = 0.1
SCALE_FACTOR = 3.0  # Scale factor used for uniformly scaling bounds of environment and spawn bounds. Larger values effectivly spread out the agents and obstacles and vice versa

# Parameters for Agents
PREY_SIGHT = 15     # Prey sight radius
PRED_SIGHT = 12     # Predator sight radius
PRED_INTERACTION_RADIUS = 5  # Predator interaction radius
PREY_INTERACTION_RADIUS = 5  # Prey interaction radius
PREY_SPEED = 1.5    # Speed of prey
PRED_SPEED = 1.65      # Speed of predator

PRED_START_ENERGY = 150         # Starting energy for predator
PRED_MOVE_COST = 0.5            # Energy lost by predator when movings
PRED_EAT_ENERGY_GAIN = 50       # Energy gained by predator when eating prey
PRED_FAIL_ENERGY_COST = 3       # Energy lost by predator when failing to catch prey

PREY_START_ENERGY = 100         # Starting energy for prey
PREY_MOVE_COST = 0.5          # Energy lost by prey when moving
# Energy lost by prey when failing to escape predator
PREY_FAIL_ENERGY_COST = 0.55
PREY_EAT_ENERGY_GAIN = 20      # Energy gained by prey when eating food
# Rate at which prey loose speed as they get more hungry (less energy) Set to 0 to disable
PREY_DECAY_MOVE_RATE = 0.15

# Parameters for Neat/non-neat agents
NEAT = True  # If true, NEAT will be used for some agents
NON_NEAT = True  # If true some agents will be NEAT agents and some will be non-NEAT agents
HYPERNEAT = True  # If true, HyperNEAT will be used for some NEAT agents
# Percaentage of agents out of the total that will be NEAT agents, HyperNEAT agents, and non-NEAT agents. These values should sum to 1.0.
NEAT_PERCENT = 0.3
HYPERNEAT_PERCENT = 0.3
NON_NEAT_PERCENT = 0.4


# Breed and Mutate parameters
CROSS_OVER_RATE = 0.7  # Crossover rate for breeding, high values mean more crossover
CUT_OFF = 0.1  # percentage of agents that will be used for breading, 0.1 = 10% so best 10% of agents will breed
TOURNAMENT_SIZE = 3  # Tournament size for selection
HYPERNEAT_SUBSTRATE_SCHEMA = {
    'inputs': [(-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)],
    'outputs': [(-0.5, 0.0), (0.5, 0.0)]
}
# Parameter for number of times simulation will run
EPOCHS = 850
