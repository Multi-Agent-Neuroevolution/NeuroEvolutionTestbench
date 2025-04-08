"""constants.py"""
# Parameters for simulation creation
SIMULATION_TYPE = "PRED_PREY"
CONFIG_PATH = "./Config/neat.conf"
STEPS = 700
BOUNDS = [-200, 200, -200, 200]  # Bounds for the environment

# Parameters for agents
# Ratio of predators to prey higher values mean more prey than predators.
RATIO = 0.95
PRED_PERCENT = 1 - RATIO
FOOD_AMOUNT = 100  # Amount of food in the environment for prey to eat
PREY_SPAWN_BOUNDS = [-150, 150, 150, 50]
PRED_SPAWN_BOUNDS = [150, -150, -150, -50]
# Causes the predator and prey spawn bounds to be swapped at the halfway point of the simulation
SWAP_BOUNDS = False
# Rate at which food respawns, 0.1 = 10% chance of respawning each step
FOOD_RESPAWN_RATE = 0.1
SCALE_FACTOR = 1.0  # Scale factor used for uniformly scaling bounds of environment and spawn bounds. Larger values effectivly spread out the agents and obstacles and vice versa

# Parameters for Agents
PREY_SIGHT = 12  # Prey sight radius
PRED_SIGHT = 12  # Predator sight radius
PREY_SPEED = 1.5
PRED_SPEED = 1
PRED_MOVE_COST = 0.12      # Energy lost by predator when movings
PRED_EAT_ENERGY_GAIN = 30  # Energy gained by predator when eating prey
PRED_FAIL_ENERGY_COST = 3  # Energy lost by predator when failing to catch prey

# Parameters for Neat/non-neat agents

# If true some agents will be NEAT agents and some will be non-NEAT agents
MULTI_MODEL = True
MODEL_SPLIT = 0.5  # If multi_model is true, this is the split between the two models


# Breed and Mutate parameters
CROSS_OVER_RATE = 0.7  # Crossover rate for breeding high values mean more crossover
CUT_OFF = 0.1  # percentage of agents that will be used for breading, 0.1 = 10% so best 10% of agents will breed
TOURNAMENT_SIZE = 3  # Tournament size for selection

# Parameter for number of times simulation will run
EPOCHS = 500
