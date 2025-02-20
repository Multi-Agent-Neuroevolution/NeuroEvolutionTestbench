"""environment.py handles the environment components, such as agents and obstacles."""
from collections import defaultdict
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import matplotlib.pyplot as plt
import time
from utils import State
from obstacles import Food, Wall
from agents import Predator, Prey
import logging

logger = logging.getLogger(__name__)


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
        # Cell size can be adjusted here for better performance depending on sim
        self.spatial_grid = SpatialGrid(self.bounds, cell_size=10)
        # locking critical sections for each agent
        self.agent_locks = {}
        # Default to 8 workers, but is adjusted by sim_world.py
        self.max_workers = 8

    # TO DO: Try recoding this to better accomodate different simulation type (ie. not pred-prey)
    def initialize_environment(self, config, population, pred_pop, prey_pop, pred_spawn_bounds, prey_spawn_bounds, food_amount):
        self._initialize_agents(
            config, population, pred_pop, prey_pop, pred_spawn_bounds, prey_spawn_bounds)
        self._initialize_obstacles(food_amount)

    def _initialize_agents(self, config, population, pred_pop, prey_pop, pred_spawn_bounds, prey_spawn_bounds):
        agents = []

        # Initialize predators
        for i in range(pred_pop):
            pos = np.array([
                np.random.uniform(pred_spawn_bounds[0], pred_spawn_bounds[1]),
                np.random.uniform(pred_spawn_bounds[2], pred_spawn_bounds[3])
            ])
            genome = population.population[i + 1]
            agents.append(
                Predator(id=i, pos=pos, neat_genome=genome, neat_config=config))

        # Initialize prey
        for i in range(prey_pop):
            pos = np.array([
                np.random.uniform(prey_spawn_bounds[0], prey_spawn_bounds[1]),
                np.random.uniform(prey_spawn_bounds[2], prey_spawn_bounds[3])
            ])
            genome = population.population[i + pred_pop]
            agents.append(Prey(id=(i + pred_pop), pos=pos,
                          neat_genome=genome, neat_config=config))

        self.add_agents(agents)

    def _initialize_obstacles(self, food_amount):
        obstacles = []

        # Initialize food
        for _ in range(food_amount):
            pos = np.array([
                np.random.uniform(self.bounds[0], self.bounds[1]),
                np.random.uniform(self.bounds[2], self.bounds[3])
            ])
            obstacles.append(Food(pos))

        # Temporary, but initialize wall at the center
        obstacles.append(Wall(pos=np.array([0, 0]), width=100, height=45))

        self.add_obstacles(obstacles)

    # This definition handles adding agents to the environment
    def add_agents(self, agents):
        self.agents = agents
        for agent in agents:
            self.agent_locks[agent] = Lock()

    # ADRIAN: This seems redundant with the add_agents function (both are used in sim_world.py)
    def overwrite_agents(self, agents):
        self.agents = agents
        for agent in agents:
            self.agent_locks[agent] = Lock()

    def add_obstacles(self, obstacles):
        """Adds obstacles to the environment.

        Args:
            obstacles (list): List of obstacles to add to the environment.
        """
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
            # Check bounds
            agent.check_bounds(self.bounds)
            # ADRIAN: should this be made into an else function for the above?
            agent.get_collisions()
            agent.solve_collision()
            # If the agent is dead, it's removed from the environment
            if not agent.living:
                agent.fitness = -9999
                self.agents.remove(agent)  # Remove dead agent

    # # This definition is FOR DEBUGGING PURPOSES and is for visualizing the environment
    # def view(self, real_time=False):
    #     # plt.close('all')  # Close any existing figures

    #     # Create figure and axes with a larger size for better visibility
    #     fig, ax = plt.subplots(figsize=(12, 12))
    #     ax.set_xlim(self.bounds[0], self.bounds[1])
    #     ax.set_ylim(self.bounds[2], self.bounds[3])

    #     # Add grid for better spatial reference
    #     ax.grid(True, linestyle='--', alpha=0.3)
    #     ax.set_facecolor('#f0f0f0')  # Light gray background

    #     # This segment of the code draws all existing objects in the environment
    #     for i, obstacle in enumerate(self.obstacles):
    #         if obstacle.shape == "circle":
    #             circle = plt.Circle(
    #                 obstacle.pos,
    #                 obstacle.radius,
    #                 color = obstacle.color if hasattr(obstacle, 'color') else 'red',
    #                 alpha=0.7,
    #                 label=f'Obstacle {i}: {obstacle.type}' if hasattr(obstacle, 'type') else f'Obstacle {i}'
    #             )
    #             ax.add_artist(circle)
    #         elif obstacle.shape == "rectangle":
    #             rect = plt.Rectangle(
    #                 (obstacle.pos[0] - obstacle.width/2, obstacle.pos[1] - obstacle.height/2),
    #                 obstacle.width,
    #                 obstacle.height,
    #                 color=obstacle.color if hasattr(obstacle, 'color') else 'red',
    #                 alpha=0.7,
    #                 label=f'Obstacle {i}: {obstacle.type}' if hasattr(obstacle, 'type') else f'Obstacle {i}'
    #             )
    #             ax.add_artist(rect)

    #     # This segment of the code draws all existing agents in the environment
    #     for i, agent in enumerate(self.agents):
    #         # Draw vision circle (as in, how far the agent can see). Vision radius is second value in the tuple (this should be made a constant)
    #         vision_circle = plt.Circle(agent.pos, 10, color='green', alpha=0.1, fill=True)
    #         ax.add_artist(vision_circle)

    #         # Draw agent itself
    #         agent_circle = plt.Circle(agent.pos, agent.radius, color='blue', alpha=0.7)
    #         ax.add_artist(agent_circle)

    #         # This adds an ID label to the agent
    #         ax.annotate(
    #             f'A{i}',
    #             xy=(agent.pos[0], agent.pos[1]),
    #             xytext=(5, 5),
    #             textcoords='offset points',
    #             fontsize=8,
    #             bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
    #         )

    #         # Draw connections agent has between all objects
    #         if hasattr(agent, 'state') and hasattr(agent.state, 'objs'):
    #             for obj in agent.state.objs:
    #                 # Calculate distance
    #                 distance = np.linalg.norm(agent.pos - obj.pos)

    #                 # Draw line with distance label
    #                 line = ax.plot([agent.pos[0], obj.pos[0]], [agent.pos[1], obj.pos[1]], 'k--', alpha=0.3, linewidth=0.5)[0]

    #                 # Add distance label at midpoint
    #                 midpoint = (agent.pos + obj.pos) / 2
    #                 ax.annotate(
    #                     f'{distance:.1f}',
    #                     xy=(midpoint[0], midpoint[1]),
    #                     fontsize=6,
    #                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
    #                 )

    #     # Add title with simulation info
    #     ax.set_title(f'Environment Type: {self.type}\n' f'Agents: {len(self.agents)} | ' f'Obstacles: {len(self.obstacles)}')

    #     # Add legend
    #     if self.obstacles:
    #         ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    #     # Adjust layout to prevent cutting off elements
    #     plt.tight_layout()

    #     # Finally, display the plot depending on if it's real-time or not
    #     if real_time:
    #         plt.ion()
    #         plt.draw()
    #         plt.pause(0.1)
    #         plt.close(fig)
    #     else:
    #         plt.show()

    # This definition handles food addition and removal

    def food_handler(self):
        # This segment checks food is "living" (in other words, not eaten) and removes it if it's not
        for obs in self.obstacles:
            if isinstance(obs, Food):
                if obs.living == False:
                    self.obstacles.remove(obs)

        # This segment handles the spawning of food
        if np.random.rand() < self.food_spawn_rate:
            pos = np.array([np.random.uniform(self.bounds[0], self.bounds[1]),
                           np.random.uniform(self.bounds[2], self.bounds[3])])
            food = Food(pos)
            self.obstacles.append(food)

    # This definition resets all agents when the current epoch is over

    def reset(self, prey_bound=[-150, 150, 50, 150], predator_bound=[-150, 150, -150, -50]):
        print("Resetting environment...")
        for agent in self.agents:
            # If-else statement separates prey and predators
            # TO DO: Move Predator() and Prey() subclasses to agent.py
            if isinstance(agent, Predator):
                pos = np.array([np.random.uniform(predator_bound[0], predator_bound[1]), np.random.uniform(
                    predator_bound[2], predator_bound[3])])
                agent.pos = pos
                agent.energy = 100
                agent.prey_eaten = 0
            else:
                pos = np.array([np.random.uniform(
                    prey_bound[0], prey_bound[1]), np.random.uniform(prey_bound[2], prey_bound[3])])
                agent.pos = pos
                agent.energy = 0

            # Regardless of agent type, fitness is reset to 0
            agent.fitness = 0
            agent.state = State()
        print("Environment reset")

    def run(self):
        print("Running simulation...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for _ in range(self.steps):
                start_time = time.time()

                # Update spatial grid
                self.update_spatial_grid()

                # Handle Agents
                list(executor.map(self.update_agent, self.agents))

                # Handle food
                self.food_handler()

                # print(f"Step {_} completed")

                # end_time = time.time()
                # print(f"Time taken: {(end_time - start_time)*1000}ms")
                # print number of prey and predatorys alive
                num_prey_alive = len(
                    [agent for agent in self.agents if not isinstance(agent, Predator)])
                num_predators_alive = len(
                    [agent for agent in self.agents if isinstance(agent, Predator)])

                print(f"Number of Prey Alive: {num_prey_alive}")
                print(f"Number of Predators Alive: {num_predators_alive}")
                # Find the fittest predator and prey
                # Find amount of food left
                # self.view(real_time=True)
