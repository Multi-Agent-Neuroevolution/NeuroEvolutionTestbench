"""agent.py holds the Agent class and Metrics class for the simulation."""
import heapq
import numpy as np
from utils import State, Shape, Metrics
from obstacles import Food
import neat
import logging
import constants
logger = logging.getLogger(__name__)


class Agent(Shape):
    """Class for the agent in the simulation.

    Args:
        id (int): The unique identifier for the agent.
        pos (np.ndarray): The initial position of the agent.
        neat_genome (neat.DefaultGenome): The NEAT genome for the agent.
        neat_config (neat.DefaultConfig): The NEAT configuration for the agent.
        agent_type (str): The type of agent (e.g., predator, prey).
        energy (float): The initial energy of the agent.
        move_speed (float): The speed at which the agent moves.
    """

    def __init__(self, id, pos, neat_genome, neat_config, sight, agent_type="agent", energy=0, move_speed=1.0, _neat=True):
        super().__init__(shape="agent", radius=1, width=0,
                         height=0, pos=pos, collidable=False)
        self.id = id
        self.pos = pos
        self.neat_genome = neat_genome
        self.neat_config = neat_config
        self.agent_type = agent_type
        self.energy = energy
        self.move_speed = move_speed
        self.age = 0
        self.fitness = 0
        self.state = State()
        self.metrics = Metrics()
        self.brain = neat.nn.FeedForwardNetwork.create(
            neat_genome, neat_config)
        self.inputs = []
        self.sight = sight
        self.neat = _neat
        self.alive = True

    def interact(self, obj):
        if obj in self.state.interactables:
            obj.interact(self)

    def update_action(self):
        """Updates the action of the agent based on the neural network output."""
        self.get_inputs()
        # IMPORTANT: The neural network is activated here
        action = self.brain.activate(self.inputs)
        action_choice = np.argmax(action)
        self._handle_movement(action_choice)
        self._handle_action(action_choice)
        self._update_fitness()

    def _handle_movement(self, action_choice):
        """Handles the movement of the agent based on the action choice.

        Args:
            action_choice (int): The action choice made by the agent.
        """
        match action_choice:
            case 0:  # Agent moves up
                self.pos[1] += self.move_speed
            case 1:  # Agent moves down
                self.pos[1] -= self.move_speed
            case 2:  # Agent moves left
                self.pos[0] -= self.move_speed
            case 3:  # Agent moves right
                self.pos[0] += self.move_speed
            case _:  # Default case (no movement)
                self.pos = self.pos

    def _handle_action(self, action_choice):
        """Handles the action of the agent based on the action choice. Overwritten in subclass."""
        pass

    def _update_fitness(self):
        """Updates the fitness of the agent. Overwritten in subclass."""
        pass

    def _find_closest_target(self, target_filter):
        """Finds the closest target object based on the filter function.

        Args:
            target_filter (function): The filter function to apply to the objects.

        Returns:
            closest (object): The closest target object.
            min_distance (float): The minimum distance to the closest target object.
        """
        closest = None
        min_distance = float('inf')

        for obj in self.state.interactables:
            if target_filter(obj):
                distance = np.linalg.norm(self.pos - obj.pos)
                if distance < min_distance:
                    closest = obj
                    min_distance = distance

        return closest, min_distance  # is returning min_distance necessary?

    # This function is used to get the inputs for the neural network. Faster

    def get_inputs(self, max_closest=5):
        # Pre-calculate the squared interaction radius
        interaction_radius_squared = 5 * 5

        relative_objects = []
        self.state.interactables = []

        for obj in self.state.objs:
            rel_x = obj.pos[0] - self.pos[0]
            rel_y = obj.pos[1] - self.pos[1]

            squared_dist = rel_x*rel_x + rel_y*rel_y

            if squared_dist <= interaction_radius_squared:
                self.state.interactables.append(obj)

            # Determine object type
            obj_type = -1
            if obj.shape == "agent" and obj.alive:
                obj_type = 1 if obj.energy > 0 else 0
            elif obj.shape == "obstacle" and obj.interactible:
                obj_type = 2 if obj.type == "food" else 3

            # Only add objects with a valid type to the heap
            if obj_type != -1:
                relative_objects.append(
                    (squared_dist, (rel_x, rel_y), obj_type))

        # Get the max_closest objects
        closest_objects = heapq.nsmallest(
            max_closest, relative_objects, key=lambda x: x[0])

        # Flatten Inputs
        self.inputs = []
        for _, rel_pos, obj_type in closest_objects:
            self.inputs.extend([rel_pos[0], rel_pos[1], obj_type])

        # Padding
        padding_needed = (max_closest * 3) - len(self.inputs)
        if padding_needed > 0:
            self.inputs.extend([-1] * padding_needed)

        # Add energy as input
        self.inputs.append(self.energy)

        return self.inputs

    def get_relative_pos(self, obj):
        return self.pos - obj.pos

    def get_collisions(self):
        self.state.collisions.clear()
        for obj in self.state.objs:
            if not obj.collidable:
                continue
            if obj.shape == "circle":
                # Check for circle collision
                dist = np.linalg.norm(self.pos - obj.pos)
                if dist < (self.radius + obj.radius):
                    self.state.collisions.append(obj)
            elif obj.shape == "rectangle":
                # Check for rectangle collision
                nearest_x = np.clip(self.pos[0], obj.pos[0] - obj.width / 2,
                                    obj.pos[0] + obj.width / 2)
                nearest_y = np.clip(self.pos[1], obj.pos[1] - obj.height / 2,
                                    obj.pos[1] + obj.height / 2)

                dist = np.linalg.norm(
                    self.pos - np.array([nearest_x, nearest_y]))
                if dist < self.radius:
                    self.state.collisions.append(obj)

        if len(self.state.collisions) > 0:
            return True
        return False

    def solve_collision(self):
        for collision in self.state.collisions[:]:
            if collision.shape == "circle":
                # Compute vector from obstacle to agent
                direction = self.pos - collision.pos
                norm = np.linalg.norm(direction)
                if norm > 0:
                    direction /= norm  # Normalize
                    # Move agent to nearest valid position outside the circle
                    self.pos = collision.pos + direction * \
                        (collision.radius + self.radius)

            elif collision.shape == "rectangle":
                # Get the nearest valid position outside the rectangle
                nearest_x = np.clip(self.pos[0], collision.pos[0] - collision.width /
                                    2 - self.radius, collision.pos[0] + collision.width / 2 + self.radius)
                nearest_y = np.clip(self.pos[1], collision.pos[1] - collision.height /
                                    2 - self.radius, collision.pos[1] + collision.height / 2 + self.radius)

                # Compute vector from the nearest point to the agent
                direction = self.pos - np.array([nearest_x, nearest_y])
                norm = np.linalg.norm(direction)

                if norm > 0:
                    direction /= norm  # Normalize
                    # Move agent just outside the obstacle
                    self.pos = np.array(
                        [nearest_x, nearest_y]) + direction * self.radius

    # This definition adjusts the agent position if it goes out of bounds
    def check_bounds(self, bounds):
        if self.pos[0] < bounds[0]:
            self.pos[0] = bounds[0] + 1
        if self.pos[0] > bounds[1]:
            self.pos[0] = bounds[1] - 1
        if self.pos[1] < bounds[2]:
            self.pos[1] = bounds[2] + 1
        if self.pos[1] > bounds[3]:
            self.pos[1] = bounds[3] - 1


class Predator(Agent):
    """Class for the predator agent in the predator-prey simulation.

    Args:
        id (int): The unique identifier for the predator agent.
        pos (np.ndarray): The initial position of the predator agent.
        neat_genome (neat.DefaultGenome): The NEAT genome for the predator agent.
        neat_config (neat.DefaultConfig): The NEAT configuration for the predator agent. Also used for non neat agents.
        neat (bool): Whether the agent is using NEAT or not.
    """

    def __init__(self, id, pos, neat_genome, neat_config, neat):
        super().__init__(id=id, pos=pos, neat_genome=neat_genome,
                         neat_config=neat_config, agent_type="PRED", energy=100, sight=constants.PRED_SIGHT, move_speed=constants.PRED_SPEED, _neat=neat)
        self.prey_eaten = 0
        self.ENERGY_COST = constants.PRED_MOVE_COST

    def _handle_action(self, action_choice):
        """Handles the action of the predator agent based on the action choice.

        Args:
            action_choice (int): The index of the action with the highest value.
        """
        # Deducts energy if the action is a movement, otherwise calls the eat function
        if 0 <= action_choice <= 3:
            self.energy -= self.ENERGY_COST
        elif action_choice == 4:
            self._eat()

        if self.energy <= 0:
            self.alive = False
            # logger.info(f"Predator {self.id} has run out of energy and died.")

    def _update_fitness(self):
        """Updates the fitness of the predator agent based on the number of prey eaten and current energy."""
        self.fitness = (self.prey_eaten * 10) + (self.energy / 3)

    def _eat(self):
        """Handles the eating action of the predator agent, finding the closest prey object if applicable."""
        def _prey_filter(obj):
            return obj.shape == "agent" and obj.alive and isinstance(obj, Prey)

        closest_prey, _ = self._find_closest_target(_prey_filter)

        if closest_prey is None:
            self.energy -= constants.PRED_FAIL_ENERGY_COST
            logger.info(
                f"Predator {self.id} chooses to eat, but fails to find a prey.")
        else:
            closest_prey.alive = False
            self.prey_eaten += 1
            self.energy += constants.PRED_EAT_ENERGY_GAIN
            logger.info(
                f"Predator {self.id} chooses to eat Prey {closest_prey.id} successfully.")
            # TO DO: Share with predators around it


class Prey(Agent):
    """Class for the prey agent in the predator-prey simulation.

    Args:
        id (int): The unique identifier for the prey agent.
        pos (np.ndarray): The initial position of the prey agent.
        neat_genome (neat.DefaultGenome): The NEAT genome for the prey agent. 
        neat_config (neat.DefaultConfig): The NEAT configuration for the prey agent. Also used for non neat agents.
        neat (bool): Whether the agent is using NEAT or not.
    """

    def __init__(self, id, pos, neat_genome, neat_config, neat):
        super().__init__(id=id, pos=pos, neat_genome=neat_genome,
                         neat_config=neat_config, agent_type="PREY", move_speed=constants.PREY_SPEED, sight=constants.PREY_SIGHT, _neat=neat)
        self.spawn = pos

    def _handle_action(self, action_choice):
        """Handles the action of the prey agent based on the action choice."""
        if action_choice == 4:
            self._eat()

    def _update_fitness(self):
        """Updates the fitness of the prey agent."""
        self.fitness += 0.1

    def calcualte_distance_moved(self):
        """Calculates the distance moved by the prey agent."""
        return np.linalg.norm(self.pos - self.spawn)

    def _eat(self):
        """Handles the eating action of the prey agent, finding the closest food object if applicable."""
        def _food_filter(obj):
            return isinstance(obj, Food)

        closest_food, _ = self._find_closest_target(_food_filter)

        if closest_food is None:
            # logger.info(
            #     f"Prey {self.id} chooses to eat, but fails to find food.")
            self.fitness -= 0.25
        else:
            closest_food.living = False
            self.fitness += 0.5
            logger.info(f"Prey {self.id} eats succsefully.")
