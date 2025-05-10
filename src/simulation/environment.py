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
import logs
import copy
import math
import constants
import json
from messenger import messageChannel

logger = logging.getLogger(__name__)


class SpatialGrid:
    """
    Uniform grid for spatial partitioning of objects, accounting for object extents.

    Attributes:
        bounds (tuple): (min_x, max_x, min_y, max_y) of the world.
        cell_size (float): Side length of each grid cell.
        width (int): Number of cells horizontally.
        height (int): Number of cells vertically.
        grid (defaultdict): Maps (cell_x, cell_y) to list of objects.
    """

    def __init__(self, bounds, cell_size=10):
        self.bounds = bounds
        self.cell_size = cell_size
        self.width = math.ceil((bounds[1] - bounds[0]) / cell_size)
        self.height = math.ceil((bounds[3] - bounds[2]) / cell_size)
        self.grid = defaultdict(list)

    def get_cell_coords(self, pos):
        """
        Convert world position to grid cell indices, clamped to valid range.
        """
        x = int((pos[0] - self.bounds[0]) / self.cell_size)
        y = int((pos[1] - self.bounds[2]) / self.cell_size)
        x = max(0, min(self.width - 1, x))
        y = max(0, min(self.height - 1, y))
        return x, y

    def insert(self, obj):
        """
        Insert an object into all grid cells that its bounding box overlaps.
        Rectangles: defined by top-left corner (pos), extents width & height.
        Circles: defined by center pos & radius.
        """
        # Determine bounding box
        if hasattr(obj, 'width') and hasattr(obj, 'height'):
            min_x = obj.pos[0]
            max_x = obj.pos[0] + obj.width
            min_y = obj.pos[1]
            max_y = obj.pos[1] + obj.height
        elif hasattr(obj, 'radius'):
            min_x = obj.pos[0] - obj.radius
            max_x = obj.pos[0] + obj.radius
            min_y = obj.pos[1] - obj.radius
            max_y = obj.pos[1] + obj.radius
        else:
            min_x = max_x = obj.pos[0]
            min_y = max_y = obj.pos[1]

        # Convert bounding coords to cell indices
        cell_x_min = int((min_x - self.bounds[0]) / self.cell_size)
        cell_x_max = int((max_x - self.bounds[0]) / self.cell_size)
        cell_y_min = int((min_y - self.bounds[2]) / self.cell_size)
        cell_y_max = int((max_y - self.bounds[2]) / self.cell_size)

        # Clamp cell ranges
        cell_x_min = max(0, min(self.width - 1, cell_x_min))
        cell_x_max = max(0, min(self.width - 1, cell_x_max))
        cell_y_min = max(0, min(self.height - 1, cell_y_min))
        cell_y_max = max(0, min(self.height - 1, cell_y_max))

        # Insert into overlapped cells
        for cx in range(cell_x_min, cell_x_max + 1):
            for cy in range(cell_y_min, cell_y_max + 1):
                self.grid[(cx, cy)].append(obj)

    def rebuild(self, objects):
        """
        Clear and rebuild the entire grid from a list of objects.
        Useful if objects move every step.
        """
        self.grid.clear()
        for obj in objects:
            self.insert(obj)

    def get_nearby_objects(self, pos, radius):
        cell_x, cell_y = self.get_cell_coords(pos)
        radius_cells = int(radius / self.cell_size) + 1

        seen = set()
        for dx in range(-radius_cells, radius_cells + 1):
            for dy in range(-radius_cells, radius_cells + 1):
                cx, cy = cell_x + dx, cell_y + dy
                if not (0 <= cx < self.width and 0 <= cy < self.height):
                    continue
                for obj in self.grid[(cx, cy)]:
                    seen.add(obj)
        return list(seen)


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
    def initialize_environment(self, config, population, pred_pop, prey_pop, pred_spawn_bounds, prey_spawn_bounds, food_amount, prey_pop_no_neat=0, pred_pop_no_neat=0):
        self._initialize_agents(
            config, population, pred_pop, prey_pop, pred_spawn_bounds, prey_spawn_bounds, pred_no_neat_pop=pred_pop_no_neat, prey_no_neat_pop=prey_pop_no_neat)
        self._initialize_obstacles(food_amount)

    def _initialize_agents(self, config, population, pred_pop, prey_pop, pred_spawn_bounds, prey_spawn_bounds, pred_no_neat_pop=0, prey_no_neat_pop=0):
        agents = []
        # Initialize predators
        for i in range(pred_pop):

            pos = np.array([
                np.random.uniform(pred_spawn_bounds[0], pred_spawn_bounds[1]),
                np.random.uniform(pred_spawn_bounds[2], pred_spawn_bounds[3])
            ])
            genome = copy.deepcopy(population.population[i + 1])
            agents.append(
                Predator(id=i, pos=pos, neat_genome=genome, neat_config=config["predNeatConfig"], type=1))

        # Initialize prey
        for i in range(prey_pop):

            pos = np.array([
                np.random.uniform(prey_spawn_bounds[0], prey_spawn_bounds[1]),
                np.random.uniform(prey_spawn_bounds[2], prey_spawn_bounds[3])
            ])
            genome = copy.deepcopy(population.population[i + pred_pop])
            agents.append(Prey(id=(i + pred_pop), pos=pos,
                          neat_genome=genome, neat_config=config["preyNeatConfig"], type=1))
        # Initialize pred_no_neat
        for i in range(pred_no_neat_pop):

            pos = np.array([
                np.random.uniform(pred_spawn_bounds[0], pred_spawn_bounds[1]),
                np.random.uniform(pred_spawn_bounds[2], pred_spawn_bounds[3])
            ])
            genome = copy.deepcopy(population.population[i + 1])
            agents.append(
                Predator(id=(i + pred_pop), pos=pos, neat_genome=genome, neat_config=config["predStdConfig"], type=0))

        # Initialize prey_no_neat
        for i in range(prey_no_neat_pop):

            pos = np.array([
                np.random.uniform(prey_spawn_bounds[0], prey_spawn_bounds[1]),
                np.random.uniform(prey_spawn_bounds[2], prey_spawn_bounds[3])
            ])
            genome = copy.deepcopy(population.population[i + pred_pop])
            agents.append(Prey(id=(i + prey_pop), pos=pos,
                          neat_genome=genome, neat_config=config["preyStdConfig"], type=0))

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

        # look for a file in ./Objects/objects.json then parse it and add the objects to the obstacles list
        try:
            with open('./Objects/objects.json', 'r') as f:
                data = json.load(f)
                for obj in data:
                    if obj['type'] == 'Rectangle':
                        pos = np.array([obj['x'], obj['y']])
                        width = obj['width']
                        height = obj['height']
                        obstacles.append(Wall(pos, width, height))
        except FileNotFoundError:
            print("No objects.json file found, using default obstacles.")
        self.add_obstacles(obstacles)

    # This definition handles adding agents to the environment
    def add_agents(self, agents):
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
        self.spatial_grid.rebuild(self.agents + self.obstacles)
        for agent in self.agents:
            self.spatial_grid.insert(agent)
        for obstacle in self.obstacles:
            self.spatial_grid.insert(obstacle)

    def update_agent(self, agent):
        """Updates the agent's state and checks for collisions.

        Args:
            agent (Agent): The agent to update.
        """
        with self.agent_locks[agent]:
            # Get nearby objects
            nearby_objects = self.spatial_grid.get_nearby_objects(
                agent.pos, agent.sight)
            # Update agent state
            agent.state.objs = nearby_objects
            # Update agent's position
            agent.update_action()
            # Check bounds
            agent.check_bounds(self.bounds)
            # ADRIAN: should this be made into an else function for the above?
            if agent.get_collisions():
                agent.solve_collision()

    def food_handler(self):
        """Handles food-related operations, such as spawning and removal."""
        # This segment checks food is "living" (in other words, not eaten) and removes it if it's not
        self.obstacles = [o for o in self.obstacles if not (
            isinstance(o, Food) and not o.living)]

        # This segment handles the spawning of food
        if np.random.rand() < self.food_spawn_rate:
            pos = np.array([np.random.uniform(self.bounds[0], self.bounds[1]),
                           np.random.uniform(self.bounds[2], self.bounds[3])])
            food = Food(pos)
            if len(self.obstacles) + 1 < 5000:
                self.obstacles.append(food)

    def remove_dead_agents(self):
        """Removes dead agents from the environment."""
        self.agents = [agent for agent in self.agents if agent.alive]

    # This definition resets all agents when the current epoch is over
    def reset(self, pred_energy, prey_energy, prey_bound=[-150, 150, 50, 150], predator_bound=[-150, 150, -150, -50]):
        """Resets the environment by reinitializing all agents.

        Args:
            prey_bound (list, optional): The bounds for the prey agents. Defaults to [-150, 150, 50, 150].
            predator_bound (list, optional): The bounds for the predator agents. Defaults to [-150, 150, -150, -50].
        """
        print("Resetting environment...")
        for agent in self.agents:
            if isinstance(agent, Predator):
                pos = np.array([np.random.uniform(predator_bound[0], predator_bound[1]), np.random.uniform(
                    predator_bound[2], predator_bound[3])])
                agent.pos = pos
                agent.energy = pred_energy
                agent.prey_eaten = 0
                agent.alive = True
            else:
                pos = np.array([np.random.uniform(
                    prey_bound[0], prey_bound[1]), np.random.uniform(prey_bound[2], prey_bound[3])])
                agent.pos = pos
                agent.energy = prey_energy
                agent.alive = True

            agent.fitness = 0
            agent.state = State()
        # Reset food
        self.obstacles = [o for o in self.obstacles if not (
            isinstance(o, Food))]
        for _ in range(constants.FOOD_AMOUNT):
            pos = np.array([np.random.uniform(self.bounds[0], self.bounds[1]),
                           np.random.uniform(self.bounds[2], self.bounds[3])])
            food = Food(pos)
            if len(self.obstacles) + 1 < 5000:
                self.obstacles.append(food)
        print("Environment reset")

    def run(self):
        """Runs the simulation for the specified number of steps."""
        print("Running simulation...")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for step in range(self.steps):
                obstacle_dict = []
                step_start_time = time.time()

                # Update spatial grid
                self.update_spatial_grid()

                # Handle Agents
                list(executor.map(self.update_agent, self.agents))

                # Remove dead agents
                self.remove_dead_agents()

                # Handle food
                self.food_handler()

                # Send data to the GUI
                sendData = {"agents": [agent.to_dict() for agent in self.agents], "shapes": [
                    obstacle.to_dict() for obstacle in self.obstacles]}
                messageChannel.put(sendData)

                # Log agents alive
                logs.log_alive_agents(self.agents)
                num_pred_stand, num_pred_neat, num_pred_hyper = logs.pass_predator_log(
                    self.agents)
                um_prey_stand, num_prey_neat, num_prey_hyper = logs.pass_prey_log(
                    self.agents)

                # Calculate and print time taken for this `step in milliseconds
                step_time = 1000 * (time.time() - step_start_time)
                print(
                    f"Step {step+1}/{self.steps}, Time/step: {step_time:.4f}ms Prey(: Neat:{num_prey_neat}, Stand:{um_prey_stand}, Hyper:{num_prey_hyper} ), Predators(: Neat: {num_pred_neat}, Stand: {num_pred_stand}, Hyper: {num_pred_hyper} )     ", end='\r')
                percent_complete = (step + 1) / self.steps * 100
                for i in range(50):
                    if i < int(percent_complete / 2):
                        print("█", end='')
                    else:
                        print(" ", end='')

        # Print a newline at the end to ensure the next output starts on a fresh line
        print()
