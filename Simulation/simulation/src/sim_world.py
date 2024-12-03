import numpy as np
import matplotlib.pyplot as plt
from agent import Agent
from enviroment import Environment, Obstacle
import multiprocessing

def create_simulation(num_agents=5, simulation_type="PRED_PREY"):
    # Create the environment with optimal number of workers
    num_cores = multiprocessing.cpu_count()
    env = Environment(simulation_type)
    env.max_workers = max(1, num_cores - 1)  # Leave one core for system processes
    
    # Create the agents
    agents = []
    objects = []
    
    # Add obstacles
    objects.append(Obstacle(
        np.array([50, 50]),  # Center of the circle/rectangle
        "food",
        True,  # hasCollision
        "green",
        True,  # interactible
        False,  # isGoal
        "circle",  # shape
        1,     # radius
        0,     # width (0 for circle)
        0      # height (0 for circle)
    ))
    
    objects.append(Obstacle(
        np.array([20, 20]),  # Center of the rectangle
        "door",
        True,  # hasCollision
        "red",  # color
        True,  # interactible
        False,  # isGoal
        "rectangle",
        0,     # radius (0 for rectangle)
        2,    # width
        10     # height
    ))
    
    # Create agents with random positions
    for i in range(num_agents):
        pos = np.array([np.random.uniform(-200, 200), np.random.uniform(-200, 200)])
        agents.append(Agent(i, "NEAT", "PRED_PREY", pos))
    
    # Add agents and obstacles to environment
    env.add_agents(agents)
    env.add_obstacles(objects)
    
    return env

def main():
    try:
        # Configuration
        NUM_AGENTS = 5000  
        SIMULATION_TYPE = "PRED_PREY"
        
        # Create simulation
        env = create_simulation(num_agents=NUM_AGENTS, simulation_type=SIMULATION_TYPE)
        print(f"Starting simulation with {NUM_AGENTS} agents...")
        print(f"Using {env.max_workers} Logical CPU cores for parallel processing")
        
        # Run the simulation
        env.run()
        
    except KeyboardInterrupt:
        print("\nSimulation terminated by user")
    except Exception as e:
        print(f"Error during simulation: {str(e)}")
        raise

if __name__ == "__main__":
    main()