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

    def __init__(self, id, pos, neat_genome, neat_config, sight, agent_type="agent", energy=0, move_speed=1.0, type=0, range=5):
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
        if neat_genome is not None or neat_config is not None:
            self.brain = neat.nn.RecurrentNetwork.create(
                neat_genome, neat_config)
        else:
            self.brain = None
        self.inputs = []
        self.sight = sight
        self.type = type
        self.alive = True
        self.interactionRange = range

    def interact(self, obj):
        if obj in self.state.interactables:
            obj.interact(self)

    def to_dict(self):
        return {
            "id": int(self.id),
            "x": float(self.pos[0]),
            "y": float(self.pos[1]),
            "color": "white",
            "agent_type": self.agent_type,
            "energy": float(self.energy),
            "fitness": float(self.fitness),
            "age": int(self.age),
            "alive": bool(self.alive),
            "move_speed": float(self.move_speed),
            "sight": float(self.sight),
            "type": int(self.type)
        }

    def update_action(self):
        """Updates the action of the agent based on the neural network output."""
        self.get_inputs()
        # IMPORTANT: The neural network is activated here
        action = self.brain.activate(self.inputs)
        action_choice = np.argmax(action)
        self._handle_movement(action_choice)
        self._handle_action(action_choice)
        self._update_fitness()
        if self.alive:
            self.age += 1

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

        return closest  # is returning min_distance necessary?

    def get_interactables(self, interaction_range):
        """Populate state.interactables with objects closer than interaction_range."""
        self.state.interactables.clear()
        for obj in self.state.objs:
            dist = np.linalg.norm(self.pos - obj.pos)
            if dist < interaction_range:
                self.state.interactables.append(obj)

    def get_inputs(self, max_closest=5):
        """
        Build a fixed-length input vector for the NN:
        For each of the N = max_closest nearest objects:
            [ dx, dy, is_pred, is_prey, is_food, in_bite_range, present ]
        plus [ energy_norm ] at the end.
        Total inputs = N*7 + 1
        """
        self.get_interactables(self.interactionRange)
        # 1) Gather all objects in sight
        sight = self.sight
        # state.objs was populated from the spatial grid already
        candidates = []
        for obj in self.state.objs:
            # normalized relative position
            dx = (obj.pos[0] - self.pos[0]) / sight
            dy = (obj.pos[1] - self.pos[1]) / sight

            # one‑hot type
            if isinstance(obj, Predator):
                type_vec = [1.0, 0.0, 0.0]
            elif isinstance(obj, Prey):
                type_vec = [0.0, 1.0, 0.0]
            elif isinstance(obj, Food):
                type_vec = [0.0, 0.0, 1.0]
            else:
                continue  # skip any other shapes

            # bite‑range flag
            in_bite = 1.0 if obj in self.state.interactables else 0.0

            # distance squared for sorting
            dist_sq = dx*dx + dy*dy

            candidates.append((dist_sq, dx, dy, type_vec, in_bite))

        # 2) Pick the N nearest
        closest = heapq.nsmallest(max_closest, candidates, key=lambda x: x[0])

        # 3) Flatten into input list
        inputs = []
        for _, dx, dy, type_vec, in_bite in closest:
            # [dx, dy] + [is_pred, is_prey, is_food] + [in_bite, present=1]
            inputs.extend([dx, dy] + type_vec + [in_bite, 1.0])

        # 4) Pad empty slots with
        num_missing = max_closest - len(closest)
        for _ in range(num_missing):
            inputs.extend([
                2.0, 2.0,        # dx, dy sentinel outside [-1,1]
                0.0, 0.0, 0.0,   # one‑hot all zero
                0.0,             # in_bite_range
                0.0              # present flag
            ])

        # 5) Append normalized energy
        max_e = constants.PRED_START_ENERGY if isinstance(
            self, Predator) else constants.PREY_START_ENERGY
        energy_norm = self.energy / max_e
        inputs.append(energy_norm)

        # 6) Save & return
        self.inputs = inputs
        return inputs

    def get_relative_pos(self, obj):
        return self.pos - obj.pos

    def get_collisions(self):
        """
        Populate self.state.collisions with any collidable objects
        intersecting this agent’s circle (self.pos, self.radius).
        Returns True if any were found.
        """
        self.state.collisions.clear()

        for obj in self.state.objs:
            if not obj.collidable or obj is self:
                continue

            if obj.shape == "Circle":
                # standard center‐to‐center test
                d = np.linalg.norm(self.pos - obj.pos)
                if d < (self.radius + obj.radius):
                    self.state.collisions.append(obj)

            elif obj.shape == "Rectangle":
                # rectangle defined from top‐left (obj.pos)
                left = obj.pos[0]
                top = obj.pos[1]
                right = left + obj.width
                bottom = top + obj.height

                # find closest point on rect to agent center
                nearest_x = np.clip(self.pos[0], left, right)
                nearest_y = np.clip(self.pos[1], top,  bottom)

                # distance² from agent center to that point
                dx = self.pos[0] - nearest_x
                dy = self.pos[1] - nearest_y
                if dx*dx + dy*dy < self.radius * self.radius:
                    self.state.collisions.append(obj)

        return bool(self.state.collisions)

    def solve_collision(self):
        for collision in self.state.collisions[:]:
            if collision.shape == "Circle":
                # Compute vector from obstacle to agent
                direction = self.pos - collision.pos
                norm = np.linalg.norm(direction)
                if norm > 0:
                    direction /= norm  # Normalize
                    # Move agent to nearest valid position outside the circle
                    self.pos = collision.pos + direction * \
                        (collision.radius + self.radius)
            elif collision.shape == "Rectangle":
                left = collision.pos[0]
                right = collision.pos[0] + collision.width
                top = collision.pos[1]
                bottom = collision.pos[1] + collision.height

                # Find the closest point on the expanded rect
                expanded_left = left - self.radius
                expanded_right = right + self.radius
                expanded_top = top - self.radius
                expanded_bottom = bottom + self.radius

                # Compute penetration in each axis
                dx = min(self.pos[0] - expanded_left,
                         expanded_right - self.pos[0])
                dy = min(self.pos[1] - expanded_top,
                         expanded_bottom - self.pos[1])

                if dx < dy:
                    # push out in x
                    self.pos[0] = expanded_left if self.pos[0] < (
                        left + right)/2 else expanded_right
                else:
                    # push out in y
                    self.pos[1] = expanded_top if self.pos[1] < (
                        top + bottom)/2 else expanded_bottom

    # This method adjusts the agent position if it goes out of bounds
    def check_bounds(self, bounds):
        if self.pos[0] < bounds[0]:
            self.pos[0] = bounds[1] - 1
        if self.pos[0] > bounds[1]:
            self.pos[0] = bounds[0] + 1
        if self.pos[1] < bounds[2]:
            self.pos[1] = bounds[3] - 1
        if self.pos[1] > bounds[3]:
            self.pos[1] = bounds[2] + 1


class Predator(Agent):
    """Class for the predator agent in the predator-prey simulation.

    Args:
        id (int): The unique identifier for the predator agent.
        pos (np.ndarray): The initial position of the predator agent.
        neat_genome (neat.DefaultGenome): The NEAT genome for the predator agent.
        neat_config (neat.DefaultConfig): The NEAT configuration for the predator agent. Also used for non neat agents.
        neat (bool): Whether the agent is using NEAT or not.
    """

    def __init__(self, id, pos, neat_genome, neat_config, type):
        super().__init__(id=id, pos=pos, neat_genome=neat_genome,
                         neat_config=neat_config, agent_type="PRED", energy=constants.PRED_START_ENERGY, sight=constants.PRED_SIGHT, move_speed=constants.PRED_SPEED, type=type, range=constants.PRED_INTERACTION_RADIUS)
        self.prey_eaten = 0
        self.ENERGY_COST = constants.PRED_MOVE_COST

    def to_dict(self):
        return {
            "id": int(self.id),
            "x": float(self.pos[0]),
            "y": float(self.pos[1]),
            "color": "yellow",
            "agent_type": self.agent_type,
            "energy": float(self.energy),
            "fitness": float(self.fitness),
            "age": int(self.age),
            "alive": bool(self.alive),
            "move_speed": float(self.move_speed),
            "sight": float(self.sight),
            "type": int(self.type),
            "prey_eaten": int(self.prey_eaten)
        }

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
        # Eating prey is the primary goal
        # TODO: Add these values to the constants file
        hunt_reward = self.prey_eaten * 15.0
        energy_reward = self.energy * 0.5
        survival_reward = self.age * 0.01
        self.fitness = hunt_reward + energy_reward + survival_reward

    def _eat(self):
        """Handles the eating action of the predator agent, finding the closest prey object if applicable."""
        def _prey_filter(obj):
            return obj.shape == "agent" and obj.alive and isinstance(obj, Prey)

        closest_prey = self._find_closest_target(_prey_filter)

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

    def __init__(self, id, pos, neat_genome, neat_config, type):
        super().__init__(id=id, pos=pos, neat_genome=neat_genome, energy=constants.PREY_START_ENERGY,
                         neat_config=neat_config, agent_type="PREY", move_speed=constants.PREY_SPEED, sight=constants.PREY_SIGHT, type=type, range=constants.PREY_INTERACTION_RADIUS)
        self.spawn = pos

    def to_dict(self):
        return {
            "id": int(self.id),
            "x": float(self.pos[0]),
            "y": float(self.pos[1]),
            "color": "green",
            "agent_type": self.agent_type,
            "energy": float(self.energy),
            "fitness": float(self.fitness),
            "age": int(self.age),
            "alive": bool(self.alive),
            "move_speed": float(self.move_speed),
            "sight": float(self.sight),
            "type": int(self.type)
        }

    def _handle_action(self, action_choice):
        """Handles the action of the prey agent based on the action choice."""
        if 0 <= action_choice <= 3:
            self.energy -= constants.PREY_MOVE_COST
        elif action_choice == 4:
            self._eat()
        if self.energy <= 0:
            self.alive = False

    def _update_fitness(self):
        """Updates the fitness of the prey agent."""
        # TODO: Add these values to the constants file
        distance_from_spawn = np.linalg.norm(self.pos - self.spawn)
        distance_reward = min(distance_from_spawn * 0.01,
                              1)  # Cap the distance reward
        age_reward = min(self.age * 0.1, 1)  # Cap the age reward
        energy_reward = self.energy * 0.5
        self.fitness = distance_reward + age_reward + energy_reward

    def _eat(self):
        """Handles the eating action of the prey agent, finding the closest food object if applicable."""
        def _food_filter(obj):
            return isinstance(obj, Food)

        closest_food = self._find_closest_target(_food_filter)

        if closest_food is None:
            # logger.info(
            #     f"Prey {self.id} chooses to eat, but fails to find food.")
            self.energy -= constants.PREY_FAIL_ENERGY_COST
        else:
            closest_food.living = False
            self.energy += constants.PREY_EAT_ENERGY_GAIN
            logger.info(f"Prey {self.id} eats succsefully.")
