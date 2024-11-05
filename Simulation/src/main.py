import numpy as np
from abc import ABC

# This initializes an abstract class to be used later for handling movement
class TaskState(ABC):
    obs: np.ndarray

