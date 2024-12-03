import numpy as np
from typing import List, Dict, Tuple
from main import TaskState
from agent import Agent

# NOTES: I implemented velocity and friction values just in case (better to work from a detailed system and simplify than the other way around).
# If that isn't necessary then easily removable!

# This is the base movement state to be assigned to each agent


class MovementState(TaskState):
    def __init__(self, agents: List[Agent], bounds: Tuple[float, float, float, float]):
        self.agents = agents
        # (min_x, max_x, min_y, max_y); these are the boundaries, self-explanatory
        self.bounds = bounds
        # Saves individual vel. values per agent
        self.velocities = {agent.id: np.zeros(2) for agent in agents}

    # This returns the position of each agent
    @property
    def obs(self) -> np.ndarray:
        return np.array([agent.pos for agent in self.agents])

# This handles the actual movement of each agent once the movement states have been assigned


class MovementHandler:
    def __init__(self,
                 bounds: Tuple[float, float, float,
                               float] = (-100, 100, -100, 100),
                 max_speed: float = 5.0, acceleration: float = 1.0, friction: float = 0.1):
        self.bounds = bounds
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.friction = friction

    # This initializes the movement state per agent
    def create_state(self, agents: List[Agent]) -> MovementState:
        return MovementState(agents, self.bounds)

    # This updates the movement stats per agent
    def update(self, state: MovementState, actions: Dict[int, np.ndarray]) -> MovementState:
        for agent in state.agents:
            # This checks to make sure that the agent currently being handled hasn't been assigned a movement action
            if agent.id not in actions:
                continue

            # This gets the agent's velocity
            velocity = state.velocities[agent.id]
            action = actions[agent.id]

            # In case the agent's action isn't normalized, this part of the for loop does so
            action_norm = np.linalg.norm(action)
            if action_norm > 1.0:
                action = action / action_norm

            # After getting the current velocity of the agent, apply the acceleration and friction values to update the velocity value
            new_velocity = velocity + action * self.acceleration
            new_velocity *= (1 - self.friction)

            # This part of the for loop makes sure that the speed is limited to a more reasonable level
            speed = np.linalg.norm(new_velocity)
            if speed > self.max_speed:
                new_velocity = new_velocity * (self.max_speed / speed)

            # The position of the agent is then calculated based on the final velocity value, making sure the agent stays within bounds
            new_pos = agent.pos + new_velocity
            min_x, max_x, min_y, max_y = self.bounds
            new_pos[0] = np.clip(new_pos[0], min_x, max_x)
            new_pos[1] = np.clip(new_pos[1], min_y, max_y)

            # The agent's position is finally updated, as well as the new current velocity. The metrics are all updated into the Metrics class
            agent.pos = new_pos
            state.velocities[agent.id] = new_velocity
            agent.metrics.update('speed', np.linalg.norm(new_velocity))
            agent.metrics.update('position_x', new_pos[0])
            agent.metrics.update('position_y', new_pos[1])

        return state

    # Not really useful for now but this calculates the distance between all agents for the future
    def get_distances(self, state: MovementState) -> np.ndarray:
        positions = state.obs  # This uses the obs property to read where each agent is
        # Here distances[i, j] means distance between agent i and agent j
        distances = np.linalg.norm(
            positions[:, np.newaxis] - positions, axis=2)
        return distances
