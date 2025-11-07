"""constants.py"""
# Parameters for simulation creation
SIMULATION_TYPE = "PRED_PREY"
CONFIG_PATH = "./Config/neat.conf"
HYPERNEAT_CONFIG_PATH = "./Config/hypr.conf"
STEPS = 350
BOUNDS = [-300, 300, -300, 300]  # Bounds for the environment
# Parameter for number of times simulation will run
EPOCHS = 200


# Parameters for agents
# Ratio of predators to prey higher values mean more prey than predators.
RATIO = 0.75
PRED_PERCENT = 1 - RATIO
FOOD_AMOUNT = 1050  # Amount of food in the environment for prey to eat
PREY_SPAWN_BOUNDS = [-100, 100, 100, 25]
PRED_SPAWN_BOUNDS = [150, -150, -150, -50]
# Causes the predator and prey spawn bounds to be swapped at the halfway point of the simulation
SWAP_BOUNDS = True
HARD_BOUNDS = True  # If true, agents cannot leave the bounds of the environment, if false they will wrap around to the other side
# Rate at which food respawns, 0.1 = 10% chance of respawning each step
FOOD_RESPAWN_RATE = 0.05
SCALE_FACTOR = 1.0  # Scale factor used for uniformly scaling bounds of environment and spawn bounds. Larger values effectivly spread out the agents and obstacles and vice versa

# Predator parameters
PRED_SIGHT = 15     # Predator sight radius
PRED_INTERACTION_RADIUS = 5  # Predator interaction radius
PRED_MOVE_COST = 0.5       # Energy lost by predator when moving
PRED_EAT_ENERGY_GAIN = 75       # Energy gained by predator when eating prey
PRED_FAIL_ENERGY_COST = 20       # Energy lost by predator when failing to catch prey
PRED_SPEED = 1.35                # Speed of predator
# Agents starting energy, effects agents of all training types
PRED_START_ENERGY = 175         # Starting energy for predator
# Rate at which predator loose speed as they get more hungry (less energy) Set to 0 to disable
PRED_DECAY_MOVE_RATE = 0.05

# Prey parameters
PREY_SIGHT = 15     # Prey sight radius
PREY_INTERACTION_RADIUS = 6  # Prey interaction radius
PREY_SPEED = 1.25   # Speed of prey
PREY_MOVE_COST = 0.5          # Energy lost by prey when moving
PREY_FAIL_ENERGY_COST = 10  # Energy lost by prey when failing to find food
PREY_EAT_ENERGY_GAIN = 50      # Energy gained by prey when eating food
# Rate at which prey loose speed as they get more hungry (less energy) Set to 0 to disable
PREY_DECAY_MOVE_RATE = 0.05
PREY_START_ENERGY = 190        # Starting energy for prey

# Colors
PREDATOR_COLOR = "red"
PREY_COLOR = "blue"
FOOD_COLOR = "green"
OBSTACLE_COLOR = "yellow"

# Parameters for Neat/non-neat agents
NEAT = True  # If true, NEAT will be used for some agents
NON_NEAT = True  # If true some agents will be NEAT agents and some will be non-NEAT agents
HYPERNEAT = True  # If true, HyperNEAT will be used for some NEAT agents
# Percaentage of agents out of the total that will be NEAT agents, HyperNEAT agents, and non-NEAT agents. These values should sum to 1.0.
NEAT_PERCENT = 0.33
HYPERNEAT_PERCENT = 0.33
NON_NEAT_PERCENT = 0.33

# Misc
# If true, initial genomes will be saved to a json file at the start of training.This is really slow
SAVE_INIT_NETWORKS = True
# Breed and Mutate parameters
CROSS_OVER_RATE = 0.7  # Crossover rate for breeding, high values mean more crossover
CUT_OFF = 0.1  # percentage of agents that will be used for breading, 0.1 = 10% so best 10% of agents will breed
TOURNAMENT_SIZE = 3  # Tournament size for selection
HYPERNEAT_SUBSTRATE_SCHEMA = {
    'inputs': [(-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)],
    'outputs': [(-0.5, 0.0), (0.5, 0.0)]
}
