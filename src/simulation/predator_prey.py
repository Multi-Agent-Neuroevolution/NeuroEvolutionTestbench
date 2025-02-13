import neat
import numpy as np
from agent import Agent

import logging
logger = logging.getLogger(__name__)


class Predator(Agent):
    def __init__(self, id, algorithm_name, relationship_name, relationship_role, pos, neat_genome, neat_config):
        super().__init__(id, "NEAT", "PRED_PREY", "PRED", pos, neat_genome, neat_config)
        self.energy = 100  # Starting energy
        self.prey_eaten = 0  # Number of prey eaten

    def update_action(self):
        if self.energy <= 0:
            self.alive = False
        else:
            self.get_inputs()
            # Neural network activation AI!!!! LLM BLOCK CHAIN AI CHAIN!
            action = self.brain.activate(self.inputs)

            # Determine action (move or eat), then match it to the match statement below
            action_choice = np.argmax(action)
            match action_choice:
                case 0:  # Agent moves up
                    self.pos[1] += 1
                    self.energy -= 0.15
                case 1:  # Agent moves down
                    self.pos[1] -= 1
                    self.energy -= 0.15
                case 2:  # Agent moves left
                    self.pos[0] -= 1
                    self.energy -= 0.15
                case 3:  # Agent moves right
                    self.pos[0] += 1
                    self.energy -= 0.15
                case 4:  # Agent eats a prey
                    self.eat()
                case _:  # Default case (should replace pass)
                    pass

            # Calculate fitness
            self.calc_fitness()

    def calc_fitness(self):
        # Calculate fitness based on number of prey eaten and current energy
        self.fitness = self.prey_eaten*10 + self.energy/3

    def eat(self):
        closest_prey = None
        min_distance = float('inf')

        # Runs through all prey agent-type objects to find the closest prey
        for obj in self.state.interactables:
            if obj.shape == "agent" and obj.alive and isinstance(obj, Prey):
                distance = np.linalg.norm(self.pos - obj.pos)
                if distance < min_distance:
                    closest_prey = obj
                    min_distance = distance

        # If there's no prey nearby, deduct energy; otherwise, eat the prey (marking it as dead) and gain energy
        if (closest_prey is None):
            self.energy -= 4
            return
        else:
            logger.info(f"Predator {self.id} eats prey {closest_prey.id} and gains energy.")
            self.energy += 12  # Regain energy (this can be adjusted)
            closest_prey.alive = False  # Remove prey by marking it as dead
            self.prey_eaten += 1  # Increment prey eaten counter
            # Share with predators around it


class Prey(Agent):
    def __init__(self, id, algorithm_name, relationship_name, relationship_role, pos, neat_genome, neat_config):
        super().__init__(id, "NEAT", "PRED_PREY", "PREY", pos, neat_genome, neat_config)

    def update_action(self):
        self.get_inputs()
        action = self.brain.activate(self.inputs)  # IMPORTANT: The neural network is activated here

        # Determine action (move or eat), then match it to the match statement below
        action_choice = np.argmax(action)
        match action_choice:
            case 0:  # Agent moves up
                self.pos[1] += 1.5
            case 1:  # Agent moves down
                self.pos[1] -= 1.5
            case 2:  # Agent moves left
                self.pos[0] -= 1.5
            case 3:  # Agent moves right
                self.pos[0] += 1.5
            case 4:  # Agent eats a food object
                self.eat()
            case _:  # Default case (should replace pass)
                pass

        # Reward for staying alive
        self.fitness += 0.1

    # This function handles the eating action of the prey, finding the closest food object if applicable
    def eat(self):
        closest_food = None
        min_distance = float('inf')

        # Runs through all food-type objects if they exist in order to determine the one closest to the prey
        for obj in self.state.objs:
            if obj.type == "food":
                distance = np.linalg.norm(self.pos - obj.pos)
                if distance < min_distance:
                    closest_food = obj
                    min_distance = distance
        
        # If there's no food nearby, deduct fitness; otherwise, eat the food (marking the object as dead) and gain fitness
        if closest_food is None:
            logger.info(f"Prey {self.id} fails to find food")
            self.fitness -= 0.025
            return
        else:
            logger.info(f"Prey {self.id} eats")
            obj.alive = False
            self.fitness += 0.05
