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

# Parameter for number of times simulation will run
EPOCHS = 2