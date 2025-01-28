import neat
import numpy as np
from agent import Agent

import logging
logger = logging.getLogger(__name__)


class Predator(Agent):
    def __init__(self, id, algorithm_name, relationship_name, pos, neat_genome, neat_config):
        super().__init__(id, "NEAT", "PRED_PREY", pos, neat_genome, neat_config)
        self.energy = 100  # Starting energy
        self.prey_eaten = 0  # Number of prey eaten

    def update_action(self):
        if self.energy <= 0:
            self.alive = False
        else:
            self.get_inputs()
            # Neural network activation AI!!!! LLM BLOCK CHAIN AI CHAIN!
            action = self.brain.activate(self.inputs)

            # Determine action (move or eat)
            # 5 outputs (move up, down, left, right, eat)
            action_choice = np.argmax(action)

            # Map action to movement or eating OM NOM NOM NOM NOM!!!
            if action_choice == 0:  # Move Up
                self.pos[1] += 1
                # Energy loss for moving
                self.energy -= 0.005  # Energy consumed per movement
            elif action_choice == 1:  # Move Down
                self.pos[1] -= 1
                # Energy loss for moving
                self.energy -= 0.005  # Energy consumed per movement
            elif action_choice == 2:  # Move Left
                self.pos[0] -= 1
                # Energy loss for moving
                self.energy -= 0.005  # Energy consumed per movement
            elif action_choice == 3:  # Move Right
                self.pos[0] += 1
                # Energy loss for moving
                self.energy -= 0.005  # Energy consumed per movement
            elif action_choice == 4:  # Eat
                self.eat()

            # Calculate fitness
            self.calc_fitness()

    def calc_fitness(self):
        # Calculate fitness based on number of prey eaten and current energy
        self.fitness = self.prey_eaten*10 + self.energy/3

    def eat(self):
        # Find closest prey (if any)
        closest_prey = None
        min_distance = float('inf')

        for obj in self.state.objs:
            if obj.shape == "agent" and obj.alive and isinstance(obj, Prey):
                distance = np.linalg.norm(self.pos - obj.pos)
                if distance < min_distance:
                    closest_prey = obj
                    min_distance = distance
        if (closest_prey is None):
            self.energy -= 0.1
            return
        else:
            # Predator eats the closest prey, gains energy, and removes the prey
            logger.info(f"Predator {self.id} eats prey {
                        closest_prey.id} and gains energy.")
            self.energy += 20  # Regain energy (this can be adjusted)
            closest_prey.alive = False  # Remove prey by marking it as dead
            self.prey_eaten += 1  # Increment prey eaten counter


class Prey(Agent):
    def __init__(self, id, algorithm_name, relationship_name, pos, neat_genome, neat_config):
        super().__init__(id, "NEAT", "PRED_PREY", pos, neat_genome, neat_config)

    def update_action(self):

        self.get_inputs()
        action = self.brain.activate(self.inputs)  # Neural network activation

        # Determine action (move or eat)
        # Assuming 5 outputs (move up, down, left, right, eat)
        action_choice = np.argmax(action)

        # Map action to movement
        if action_choice == 0:  # Move Up
            self.pos[1] += 1.5
            self.fitness += 0.01  # Reward for moving
        elif action_choice == 1:  # Move Down
            self.pos[1] -= 1.5
            self.fitness += 0.01  # Reward for moving
        elif action_choice == 2:  # Move Left
            self.pos[0] -= 1.5
            self.fitness += 0.01  # Reward for moving
        elif action_choice == 3:  # Move Right
            self.pos[0] += 1.5
            self.fitness += 0.01  # Reward for moving
        elif action_choice == 4:  # Eat
            self.eat()  # Implement eat logic for prey (e.g., regenerate energy)

    def eat(self):
        logger.info(f"Prey {self.id} eats")
