import numpy as np
from collections import defaultdict
from utils import shape
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


class Agent(shape):
    def __init__(self, id, algorithm_name, relationship_name, pos,):
        super().__init__("agent", 1, 0, 0, pos)
        self.id = id
        self.age = 0
        self.neat_genome = neat_genome
        self.brain = neat.nn.FeedForwardNetwork.create(neat_genome, config)
        self.selected_algorithm = self.init_algorithm(algorithm_name)
        self.selected_relationship = self.init_relationship(relationship_name)
        self.metrics = Metrics()
        self.state = State()
        self.random_movement = np.zeros(2)
        self.energy = 0
        self.alive = True
        self.inputs

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

    def get_inputs(self):
        self.inputs = []
        for obj in self.state.objs:
            relative_pos = self.get_relative_pos(obj)
            if obj.shape == "agent":
                if obj.alive:
                    if obj.energy > 0:
                        self.inputs.append((relative_pos, "pred"))
                    else:
                        self.inputs.append((relative_pos, "prey"))

    def get_relative_pos(self, obj):
        return self.pos - obj.pos

    # Determine what action the agent should take based on its current state
    def update_action(self):
        # move randomly
        if self.state.interactables:
            # Vectorized!!
            distances = np.array([np.linalg.norm(self.pos - obj.pos)
                                 for obj in self.state.interactables])
            closest_idx = np.argmin(distances)
            closest_obj = self.state.interactables[closest_idx]
            distance = distances[closest_idx]

            if distance > 0:
                # Reuse pre-allocated array
                np.subtract(closest_obj.pos, self.pos,
                            out=self.state.direction)
                self.state.direction /= distance
                self.pos += self.state.direction
            else:
                # Reuse pre-allocated array
                np.random.uniform(-1, 1, size=2, out=self.random_movement)
                self.pos += self.random_movement

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
        self.state.collisions.clear()  # Clear the list of collisions
        for obj in self.state.objs:
            if obj.shape != "agent" and obj.hasCollision:   # Only check for collisions with obstacles
                if np.linalg.norm(self.pos - obj.pos) <= self.radius:
                    self.state.collisions.append(obj)
        return self.state.collisions

    def solve_collision(self):
        # Create copy of list for iteration. This is necessary because we are modifying the list. But it is kinda slow
        for collision in self.state.collisions[:]:
            # Reuse pre-allocated arrays FAST!!
            np.subtract(self.pos, collision.pos, out=self.state.direction)
            norm = np.linalg.norm(self.state.direction)
            if norm > 0:
                self.state.direction /= norm
                self.pos += self.state.direction
            self.state.collisions.remove(collision)
