# This is the enviroment file

from collections import defaultdict
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import matplotlib.pyplot as plt
import time
from utils import shape
from predator_prey import Predator, Prey
from agent import State
import json
import logging

logger = logging.getLogger(__name__)

# Handles the creation of obstacles in the environment
class Obstacle(shape):
    def __init__(self, pos, type, hasCollision, color, interactible, isGoal, shape, radius, width, height):
        super().__init__(shape, radius, width, height, pos)
        self.hasCollision = hasCollision
        self.color = color
        self.interactible = interactible
        self.type = type        # Type is used to determine the type of obstacle (food? door? etc.)
        self.alive = True
        self.isGoal = isGoal    # isGoal is used to determine if the obstacle is a goal for the agent. NOT USED FOR PREDATOR-PREY

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
    def __init__(self, type, steps=500, bounds=(-200, 200, -200, 200), food_spawn_rate=0.1):
        self.agents = []
        self.bounds = bounds
        self.obstacles = []
        self.type = type
        self.steps = steps
        self.food_spawn_rate = food_spawn_rate
        self.spatial_grid = SpatialGrid(self.bounds, cell_size=10)  # Cell size can be adjusted here for better performance depending on sim
        self.agent_locks = {}                                       # locking critical sections for each agent
        self.max_workers = 8                                        # Default to 8 workers, but is adjusted by sim_world.py

    # This definition handles adding agents to the environment
    def add_agents(self, agents):
        self.agents = agents
        for agent in agents:
            self.agent_locks[agent] = Lock()

    # This definition handles adding obstacles to the environment
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
            # Get nearby objects
            nearby = self.spatial_grid.get_nearby_objects(agent.pos, 10)
            agent.state.objs = [obj for obj in nearby]

            agent.update_action()

            # Check bounds and handle death
            self.check_bounds(agent)

            # If the agent is dead, it's removed from the environment
            if not agent.alive:
                agent.fitness = -9999
                self.agents.remove(agent)  # Remove dead agent
            
            # ADRIAN: should this be made into an else function for the above?
            agent.get_collisions()
            agent.solve_collision()

    # This definition is FOR DEBUGGING PURPOSES and is for visualizing the environment
    def view(self, real_time=False):
        # plt.close('all')  # Close any existing figures

        # Create figure and axes with a larger size for better visibility
        fig, ax = plt.subplots(figsize=(12, 12))
        ax.set_xlim(self.bounds[0], self.bounds[1])
        ax.set_ylim(self.bounds[2], self.bounds[3])

        # Add grid for better spatial reference
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_facecolor('#f0f0f0')  # Light gray background

        # This segment of the code draws all existing objects in the environment
        for i, obstacle in enumerate(self.obstacles):
            if obstacle.shape == "circle":
                circle = plt.Circle(
                    obstacle.pos,
                    obstacle.radius,
                    color = obstacle.color if hasattr(obstacle, 'color') else 'red',
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

        # This segment of the code draws all existing agents in the environment
        for i, agent in enumerate(self.agents):
            # Draw vision circle (as in, how far the agent can see). Vision radius is second value in the tuple (this should be made a constant)
            vision_circle = plt.Circle(agent.pos, 10, color='green', alpha=0.1, fill=True)
            ax.add_artist(vision_circle)

            # Draw agent itself
            agent_circle = plt.Circle(agent.pos, agent.radius, color='blue', alpha=0.7)
            ax.add_artist(agent_circle)

            # This adds an ID label to the agent
            ax.annotate(
                f'A{i}',
                xy=(agent.pos[0], agent.pos[1]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
            )

            # Draw connections agent has between all objects
            if hasattr(agent, 'state') and hasattr(agent.state, 'objs'):
                for obj in agent.state.objs:
                    # Calculate distance
                    distance = np.linalg.norm(agent.pos - obj.pos)

                    # Draw line with distance label
                    line = ax.plot([agent.pos[0], obj.pos[0]], [agent.pos[1], obj.pos[1]], 'k--', alpha=0.3, linewidth=0.5)[0]

                    # Add distance label at midpoint
                    midpoint = (agent.pos + obj.pos) / 2
                    ax.annotate(
                        f'{distance:.1f}',
                        xy=(midpoint[0], midpoint[1]),
                        fontsize=6,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
                    )

        # Add title with simulation info
        ax.set_title(f'Environment Type: {self.type}\n' f'Agents: {len(self.agents)} | ' f'Obstacles: {len(self.obstacles)}')

        # Add legend
        if self.obstacles:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        # Adjust layout to prevent cutting off elements
        plt.tight_layout()

        # Finally, display the plot depending on if it's real-time or not
        if real_time:
            plt.ion()
            plt.draw()
            plt.pause(0.1)
            plt.close(fig)
        else:
            plt.show()

    # This definition handles food addition and removal
    def food_handler(self):
        # This segment checks food is "alive" (in other words, not eaten) and removes it if it's not
        for obs in self.obstacles:
            if obs.type == "food":
                if obs.alive == False:
                    self.obstacles.remove(obs)
        
        # This segment handles the spawning of food
        if np.random.rand() < self.food_spawn_rate:
            pos = np.array([np.random.uniform(self.bounds[0], self.bounds[1]), np.random.uniform(self.bounds[2], self.bounds[3])])
            food = Obstacle(pos, type="food", hasCollision=False, color="green", interactible=True, isGoal=False, shape="circle", radius=5, width=0, height=0)
            self.obstacles.append(food)

    # This definition adjusts the agent position if it goes out of bounds
    def check_bounds(self, agent):
        if agent.pos[0] < self.bounds[0]:
            agent.pos[0] = self.bounds[0] + 1
        if agent.pos[0] > self.bounds[1]:
            agent.pos[0] = self.bounds[1] - 1
        if agent.pos[1] < self.bounds[2]:
            agent.pos[1] = self.bounds[2] + 1
        if agent.pos[1] > self.bounds[3]:
            agent.pos[1] = self.bounds[3] - 1

    # This definition resets all agents when the current epoch is over
    def reset(self, prey_bound=[-150, 150, 50, 150], predator_bound=[-150, 150, -150, -50]):
        for agent in self.agents:
            # If-else statement separates prey and predators
            if isinstance(agent, Predator):
                pos = np.array([np.random.uniform(predator_bound[0], predator_bound[1]), np.random.uniform(predator_bound[2], predator_bound[3])])
                agent.pos = pos
                agent.energy = 100
                agent.prey_eaten = 0
            else:
                pos = np.array([np.random.uniform(prey_bound[0], prey_bound[1]), np.random.uniform(prey_bound[2], prey_bound[3])])
                agent.pos = pos
                agent.energy = 0
            
            # Regardless of agent type, fitness is reset to 0
            agent.fitness = 0
            agent.state = State()

    def overwrite_agents(self, agents):
        self.agents = agents
        for agent in agents:
            self.agent_locks[agent] = Lock()

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for _ in range(self.steps):
                start_time = time.time()

                # Update spatial grid
                self.update_spatial_grid()

                # Handle Agents
                list(executor.map(self.update_agent, self.agents))
                # Handle food
                self.food_handler()
                # end_time = time.time()
                # print(f"Time taken: {(end_time - start_time)*1000}ms")
                # print number of prey and predatorys alive
                # num_prey_alive = len(
                #     [agent for agent in self.agents if isinstance(agent, Prey)])
                # num_predators_alive = len(
                #     [agent for agent in self.agents if isinstance(agent, Predator)])

                # print(f"Number of Prey Alive: {num_prey_alive}")
                # print(f"Number of Predators Alive: {num_predators_alive}")
                # Find the fittest predator and prey
                # Find amount of food left
                # self.view(real_time=True)