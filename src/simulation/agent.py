import numpy as np
from collections import defaultdict
from utils import Shape
import neat
# This class works in conjunction with the Agent class, used to store all metrics calculated from agent performance
# Some metric ideas...
# fitness -> score "physical" capability somehow? or see how fitness is historically calculated
# age -> already a variable for Agents, but could use value to gauge health

import logging
logger = logging.getLogger(__name__)


class Metrics:
    def __init__(self):
        self._metrics = defaultdict(float)

    def update(self, metric_name, val):
        self._metrics[metric_name] = val

    def increment(self, metric_name, val):
        self._metrics[metric_name] += val

    def decrement(self, metric_name, val):
        self._metrics[metric_name] -= val

    def get(self, metric_name):
        return self._metrics[metric_name]

    def get_all(self):
        return dict(self._metrics)

    def reset(self):
        self._metrics.clear()

    # Variables that EVERY agent will have attached to itself:
    # id -> assign an ID to every agent for future referencing
    # age -> every agent must start at age 0, aging process TBD
    # Some additional things...
    # maybe lifespan? define how long an agent is allowed to live; could also be used to set a time for reproduction
    # pos -> array, holding X and Y positions which can each be updated continuously for movement
    # Additional:
    # should velocity be a quality? ie. some agents can move faster than others
    # selected_algorithm -> necessary in order to apply neural network algorithm to each agent and allow for easy substitution


# Used to determine the state of the agent, and what is happening around it. Updated every tick
class State:
    def __init__(self):
        self.vel = 0
        # list of obstacles/agents around the agent. Each object may or may not have collision.
        self.objs = []
        # list of objects close enought for the agent to interact with
        self.interactables = []
        self.collisions = []
        self.fitness = 0
        # These are pre-allocated for performance reasons
        self.pos_array = np.zeros(2)
        self.direction = np.zeros(2)


class Agent(Shape):
    def __init__(self, id, algorithm_name, relationship_name, pos, neat_genome, neat_config):
        super().__init__("agent", 1, 0, 0, pos)
        self.id = id
        self.age = 0
        self.type = "agent"
        self.neat_config = neat_config
        self.neat_genome = neat_genome
        self.brain = neat.nn.FeedForwardNetwork.create(neat_genome, neat_config)
        self.selected_algorithm = self.init_algorithm(algorithm_name)
        self.selected_relationship = self.init_relationship(relationship_name)
        self.metrics = Metrics()
        self.state = State()
        self.fitness = 0
        self.energy = 0
        self.alive = True
        self.inputs = []
        self.hasCollision = False

    def init_algorithm(self, algorithm_name):
        try:
            # This allows more algorithms to be implemented later on with elif
            if algorithm_name == "NEAT":
                # Code that calls function initializing NEAT algorithm
                pass  # remove these when actual code is implemented
        except:
            print(
                f"Invalid algorithm specified! {algorithm_name} is not implemented.")

    # Not sure if this def would be necessary, but this is would be skeletal groundwork
    def init_relationship(self, relationship_name):
        try:
            if relationship_name == "PRED_PREY":  # Just an example
                # Code that calls function initializing relationship type
                pass
        except:
            print(
                f"Invalid relationship specified! {relationship_name} is not implemented.")

    def interact(self, obj):
        if obj in self.state.interactables:
            obj.interact(self)

    # Update the position of the agent every tick (could be handled differently? Again skeletal basic idea)
    def update_pos(self):
        """
        empty for now
        """
        pass

    # Update the list of interactables around the agent
    def update_interatibles(self):
        self.state.interactables = [
            obj for obj in self.state.objs
            if np.linalg.norm(self.pos - obj.pos) <= 3
        ]

    def get_inputs(self, max_closest=5):
        # List to store relative positions and object type
        relative_objects = []

        # Collect relative positions and object types
        for obj in self.state.objs:
            relative_pos = self.get_relative_pos(obj)
            distance = np.linalg.norm(relative_pos)  # Euclidean distance
            if obj.shape == "agent" and obj.alive:
                # 1 for predator, 0 for prey
                obj_type = 1 if obj.energy > 0 else 0
                relative_objects.append((distance, relative_pos, obj_type))
            if obj.shape == "obstacle" and obj.interactible:
                # 2 for food, 3 for obstacle
                obj_type = 2 if obj.type == "food" else 3
                relative_objects.append((distance, relative_pos, obj_type))

        # Sort objects by distance
        relative_objects.sort(key=lambda x: x[0])

        # Take the 5 closest objects (or fewer if there aren't 5)
        closest_objects = relative_objects[:max_closest]

        # Flatten inputs (distance, x, y, type for each object)
        self.inputs = []
        for _, rel_pos, obj_type in closest_objects:
            self.inputs.append(rel_pos[0])  # x position
            self.inputs.append(rel_pos[1])  # y position
            self.inputs.append(obj_type)   # object type

        # Pad inputs to ensure a fixed size
        while len(self.inputs) < (max_closest * 3):  # 3: x, y, type
            self.inputs.append(-999)
        self.inputs.append(self.energy)  # Add energy as input
        return self.inputs

    def get_relative_pos(self, obj):
        return self.pos - obj.pos


# Handle updating each metric, then calculating a final value (fitness value?). Need to determine metrics

    def update_metrics(self):
        """
        empty for now
        """
        pass

    # The following is SUBJECT TO CHANGE depending on what metrics we end up deciding to measure
    def calc_metric_1(self):
        pass

    def calc_metric_2(self):
        pass

    # Would handle the mutation aspect of the proj., as specified in original project description
    def mutate(self):
        """
        empty for now
        """
        pass

    def get_collisions(self):
        self.state.collisions.clear()
        for obj in self.state.objs:
            if not obj.hasCollision:
                continue

            if obj.shape == "circle":
                # Check collision with circular objects
                dist = np.linalg.norm(self.pos - obj.pos)
                if dist <= self.radius + obj.radius:
                    self.state.collisions.append(obj)

            elif obj.shape == "rectangle":
                # Check collision with AABB
                if (self.pos[0] + self.radius >= obj.pos[0] - obj.width / 2 and
                    self.pos[0] - self.radius <= obj.pos[0] + obj.width / 2 and
                    self.pos[1] + self.radius >= obj.pos[1] - obj.height / 2 and
                        self.pos[1] - self.radius <= obj.pos[1] + obj.height / 2):
                    self.state.collisions.append(obj)

        return self.state.collisions

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
                nearest_x = np.clip(self.pos[0], collision.pos[0] - collision.width / 2 - self.radius, collision.pos[0] + collision.width / 2 + self.radius)
                nearest_y = np.clip(self.pos[1], collision.pos[1] - collision.height / 2 - self.radius, collision.pos[1] + collision.height / 2 + self.radius)

                # Compute vector from the nearest point to the agent
                direction = self.pos - np.array([nearest_x, nearest_y])
                norm = np.linalg.norm(direction)

                if norm > 0:
                    direction /= norm  # Normalize
                    # Move agent just outside the obstacle
                    self.pos = np.array([nearest_x, nearest_y]) + direction * self.radius
