import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import Dict, List

from agent import Agent
from movement import MovementHandler # Left out the distances def for now

# NOTES: The plotting here is just for making sure that movement actually works and will not be used in the final product!
# Later on will be connected to the GUI being developed in Rust

class MovementTest:
    def __init__(self, num_agents):
        self.movement_handler = MovementHandler(bounds=(-50, 50, -50, 50), 
                                                max_speed=2.0, acceleration=0.5, friction=0.1)
        
        # Creating agents here with random starting placements
        self.agents: List[Agent] = []
        for i in range(num_agents):
            print('AGENT ', num_agents,' created!')
            random_pos = np.random.uniform(-30, 30, 2)
            agent = Agent(id=i, algorithm_name="NEAT", relationship_name="PRED_PREY", pos=random_pos)
            self.agents.append(agent)
            
        # Initializing the movement state for every agent
        self.state = self.movement_handler.create_state(self.agents)
        
        # Setup the matplotlib figure for later use
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.scatter = None
        self.frame_count = 0
        
    # These next 2 defs can be chosen which one is used for testing, there are lines below that can be (un)commented
    # Agents will have random movement
    def generate_random_actions(self) -> Dict[int, np.ndarray]:
        actions = {}
        for agent in self.agents:
            # This generates the random direction, specifically the angle variable
            angle = np.random.uniform(0, 2 * np.pi)
            action = np.array([np.cos(angle), np.sin(angle)])
            actions[agent.id] = action
        return actions
    
    # Agents will move in a counterclockwise cicrcle, useful for checking velocity values and whatnot when adjusting movement code
    def generate_circular_actions(self) -> Dict[int, np.ndarray]:
        actions = {}
        for agent in self.agents:
            x, y = agent.pos
            action = np.array([-y, x])  # Makes so the agent's next position will be perpendicular to the current one
            action = action / (np.linalg.norm(action) + 1e-8)  # Normalizing the movement vector
            actions[agent.id] = action
        return actions
    
    # This is where the movement actions of each agent are ran and plot data is updated
    def update(self, frame):
        self.frame_count += 1
        
        # This is where you can comment which kind of actions to use
        actions = self.generate_random_actions()
        # actions = self.generate_circular_actions()
        
        # Update state using the action chosen above
        self.state = self.movement_handler.update(self.state, actions)
        
        # Update the plot
        positions = self.state.obs
        if self.scatter is None:
            self.scatter = self.ax.scatter(positions[:, 0], positions[:, 1], c=range(len(self.agents)))
        else:
            self.scatter.set_offsets(positions)
            
       
            
        return self.scatter,
    
    # This part is mainly for the plot itself
    def run(self, frames=500):
        
        # Set up plot
        min_x, max_x, min_y, max_y = self.movement_handler.bounds
        self.ax.set_xlim(min_x, max_x)
        self.ax.set_ylim(min_y, max_y)
        self.ax.set_aspect('equal')
        self.ax.grid(True)
        self.ax.set_title('Basic Random Movement!')
        
        # Handles the animation for the plot
        # for some reason in Spyder this gives a warning that it is unused; it isn't!
        anim = FuncAnimation(
            self.fig, 
            self.update, 
            frames=frames,
            interval=50,  # gonna note that this is in ms for future reference, probably not necessary
            blit=True
        )
        
        # Final plotting stuff, first two lines here make sure that each frame is actually visible when previewing
        plt.draw()
        plt.pause(0.05)
        plt.show()

if __name__ == "__main__":
    # Random seed, self explanatory; change the number so if you're using random actions the paths are different
    np.random.seed(42)
    
    # Initializes the test!
    test = MovementTest(num_agents=20) # Num_agents seems self explanatory here too
    test.run(frames=500)