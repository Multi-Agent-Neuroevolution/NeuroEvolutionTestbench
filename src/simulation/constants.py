"""constants.py"""
# Parameters for simulation creation
SIMULATION_TYPE = "PRED_PREY"
CONFIG_PATH = "./Config/neat.conf"
STEPS = 1
BOUNDS = [-200, 200, -200, 200]  # Bounds for the environment
# Ratio of predators to prey higher values mean more prey than predators.
RATIO = 0.5
PRED_PERCENT = 1 - RATIO
FOOD_AMOUNT = 100
PREY_SPAWN_BOUNDS = [-150, 150, 50, 150]
PRED_SPAWN_BOUNDS = [-150, 150, -150, -50]
FOOD_RESPAWN_RATE = 0.1
SCALE_FACTOR = 0.5  # Scale factor used for uniformly scaling bounds of environment and spawn bounds. Larger values effectivly spread out the agents and obstacles and vice versa
# Parameters for Agents
PREY_SIGHT = 12  # Prey sight radius
PRED_SIGHT = 10  # Predator sight radius
PREY_SPEED = 1.5
PRED_SPEED = 1
PRED_MOVE_COST = 0.12      # Energy lost by predator when moving
PRED_EAT_ENERGY_GAIN = 12  # Energy gained by predator when eating prey
PRED_FAIL_ENERGY_COST = 3  # Energy lost by predator when failing to catch prey
# Parameters for Neat/non-neat agents
# If true, the NEAT config will be set to not mutate connections or nodes
MULTI_MODEL = False
MODEL_SPLIT = 0.5  # If multi_model is true, this is the split between the two models

# Parameter for number of times simulation will run
EPOCHS = 1
