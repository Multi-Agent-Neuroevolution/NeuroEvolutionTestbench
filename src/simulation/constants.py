"""constants.py"""
# Parameters for simulation creation
SIMULATION_TYPE = "PRED_PREY"
CONFIG_PATH = "./Config/neat.conf"
STEPS = 100
BOUNDS = [-200, 200, -200, 200]
RATIO = 0.75
PRED_PERCENT = 1 - RATIO
FOOD_AMOUNT = 100
PREY_SPAWN_BOUNDS = [-150, 150, 50, 150]
PRED_SPAWN_BOUNDS = [-150, 150, -150, -50]
FOOD_RESPAWN_RATE = 0.1

# Parameters for Agents
PREY_SIGHT = 12
PRED_SIGHT = 10
PREY_SPEED = 1.5
PRED_SPEED = 1
PRED_MOVE_COST = 0.10
PRED_EAT_ENERGY_GAIN = 12
PRED_FAIL_ENERGY_COST = 3

# Parameter for number of times simulation will run
EPOCHS = 2
