# This is the enviroment file
import numpy as np
import matplotlib.pyplot as plt
import time
from utils import shape
import json


class Obstacle(shape):
    def __init__(self, pos, type, hasCollision, color, interactible, isGoal, shape, radius, width, height):
        super().__init__(shape, radius, width, height, pos)
        self.hasCollision = hasCollision
        self.color = color
        self.interactible = interactible
        # used to determine the type of obstacle, such as food, door, etc.
        self.type = type
        # used to determine if the agent has reached the goal for simulations where the task is to reach a goal. Not used for predator-prey
        self.isGoal = isGoal

    def interact(self, agent):
        if self.interactible:
            if self.type == "food":
                agent.state.fitness += 1  # True American units
            elif self.type == "door":
                self.hasCollision = not self.hasCollision


import numpy as np
import matplotlib.pyplot as plt
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from collections import defaultdict

class SpatialGrid:
    def __init__(self, bounds, cell_size=10):
        self.cell_size = cell_size
        self.bounds = bounds
        self.width = int((bounds[1] - bounds[0]) / cell_size)
        self.height = int((bounds[3] - bounds[2]) / cell_size)
        self.grid = defaultdict(list)
        
    def get_cell_coords(self, pos):
        x = int((pos[0] - self.bounds[0]) / self.cell_size)
        y = int((pos[1] - self.bounds[2]) / self.cell_size)
        return x, y
    
    def insert(self, obj):
        cell_x, cell_y = self.get_cell_coords(obj.pos)
        self.grid[(cell_x, cell_y)].append(obj)
    
    def get_nearby_objects(self, pos, radius):
        cell_x, cell_y = self.get_cell_coords(pos)
        cells_to_check = []
        radius_cells = int(radius / self.cell_size) + 1
        
        for dx in range(-radius_cells, radius_cells + 1):
            for dy in range(-radius_cells, radius_cells + 1):
                cells_to_check.append((cell_x + dx, cell_y + dy))
        
        nearby = []
        for cell in cells_to_check:
            nearby.extend(self.grid[cell])
        
        return [obj for obj in nearby if np.linalg.norm(obj.pos - pos) < radius]

class Environment:
    def __init__(self, type):
        self.agents = []
        self.bounds = (-200, 200, -200, 200)
        self.obstacles = []
        self.type = type
        self.spatial_grid = SpatialGrid(self.bounds)
        self.agent_locks = {}
        self.max_workers = 8  # Adjust based on your CPU cores
        
    def add_agents(self, agents):
        self.agents = agents
        for agent in agents:
            self.agent_locks[agent] = Lock()
            
    def add_obstacles(self, obstacles):
        self.obstacles = obstacles
    
    def update_spatial_grid(self):
        self.spatial_grid = SpatialGrid(self.bounds)
        for agent in self.agents:
            self.spatial_grid.insert(agent)
        for obstacle in self.obstacles:
            self.spatial_grid.insert(obstacle)
    
    def update_agent(self, agent):
        with self.agent_locks[agent]:
            # Get nearby objects using spatial partitioning
            nearby = self.spatial_grid.get_nearby_objects(agent.pos, 10) # 10 is the radius of the circle around the agent
            agent.state.objs = [obj for obj in nearby if obj is not agent]
            
            # Update agent state and position
            agent.update_action()
            agent.get_collisions()
            agent.solve_collision()
            self.check_bounds(agent)

    def view(self, real_time=False):
        """
        Enhanced visualization function for debugging purposes.
        Includes agent IDs, velocities, and better color coding.
        """
        #plt.close('all')  # Close any existing figures
        
        # Create figure and axes with a larger size for better visibility
        fig, ax = plt.subplots(figsize=(12, 12))
        ax.set_xlim(self.bounds[0], self.bounds[1])
        ax.set_ylim(self.bounds[2], self.bounds[3])
        
        # Add grid for better spatial reference
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_facecolor('#f0f0f0')  # Light gray background
        
        # Draw obstacles
        for i, obstacle in enumerate(self.obstacles):
            if obstacle.shape == "circle":
                circle = plt.Circle(
                    obstacle.pos, 
                    obstacle.radius, 
                    color=obstacle.color if hasattr(obstacle, 'color') else 'red',
                    alpha=0.7,
                    label=f'Obstacle {i}: {obstacle.type}' if hasattr(obstacle, 'type') else f'Obstacle {i}'
                )
                ax.add_artist(circle)
            elif obstacle.shape == "rectangle":
                rect = plt.Rectangle(
                    (obstacle.pos[0] - obstacle.width/2, obstacle.pos[1] - obstacle.height/2),
                    obstacle.width,
                    obstacle.height,
                    color=obstacle.color if hasattr(obstacle, 'color') else 'red',
                    alpha=0.7,
                    label=f'Obstacle {i}: {obstacle.type}' if hasattr(obstacle, 'type') else f'Obstacle {i}'
                )
                ax.add_artist(rect)
                
        # Draw agents and their properties
        for i, agent in enumerate(self.agents):
            # Draw vision radius
            vision_circle = plt.Circle(
                agent.pos,
                10,  # vision radius
                color='green',
                alpha=0.1,
                fill=True
            )
            ax.add_artist(vision_circle)
            
            # Draw agent
            agent_circle = plt.Circle(
                agent.pos,
                agent.radius,
                color='blue',
                alpha=0.7
            )
            ax.add_artist(agent_circle)
            
            # Add agent ID
            ax.annotate(f'A{i}', 
                       xy=(agent.pos[0], agent.pos[1]),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=8,
                       bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
            
            # Draw connections to visible objects
            if hasattr(agent, 'state') and hasattr(agent.state, 'objs'):
                for obj in agent.state.objs:
                    # Calculate distance
                    distance = np.linalg.norm(agent.pos - obj.pos)
                    
                    # Draw line with distance label
                    line = ax.plot([agent.pos[0], obj.pos[0]], 
                                 [agent.pos[1], obj.pos[1]], 
                                 'k--', 
                                 alpha=0.3,
                                 linewidth=0.5)[0]
                    
                    # Add distance label at midpoint
                    midpoint = (agent.pos + obj.pos) / 2
                    ax.annotate(f'{distance:.1f}', 
                              xy=(midpoint[0], midpoint[1]),
                              fontsize=6,
                              bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
            
            # Draw velocity vector if available
            if hasattr(agent, 'velocity'):
                velocity_magnitude = np.linalg.norm(agent.velocity)
                if velocity_magnitude > 0:
                    ax.arrow(agent.pos[0], 
                            agent.pos[1],
                            agent.velocity[0], 
                            agent.velocity[1],
                            head_width=0.5,
                            head_length=1,
                            fc='red',
                            ec='red',
                            alpha=0.5)
        
        # Add title with simulation info
        ax.set_title(f'Environment Type: {self.type}\n'
                    f'Agents: {len(self.agents)} | '
                    f'Obstacles: {len(self.obstacles)}')
        
        # Add legend
        if self.obstacles:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Adjust layout to prevent cutting off elements
        plt.tight_layout()
        
        if real_time:
            plt.ion()
            plt.draw()
            plt.pause(0.1)
            plt.close(fig)
        else:
            plt.show()


    def check_bounds(self, agent):
        # Existing bounds checking code...
        if agent.pos[0] < self.bounds[0]:
            agent.pos[0] = self.bounds[0]+1
        if agent.pos[0] > self.bounds[1]:
            agent.pos[0] = self.bounds[1]-1
        if agent.pos[1] < self.bounds[2]:
            agent.pos[1] = self.bounds[2]+1
        if agent.pos[1] > self.bounds[3]:
            agent.pos[1] = self.bounds[3]-1

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while True:
                start_time = time.time()
                
                # Update spatial grid
                self.update_spatial_grid()
                
                # Process agents in parallel
                list(executor.map(self.update_agent, self.agents))
                
                end_time = time.time()
                print(f"Time taken: {(end_time - start_time)*1000}ms")
                self.view(real_time=False)
            