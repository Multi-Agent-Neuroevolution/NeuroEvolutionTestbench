import numpy as np


import logging
logger = logging.getLogger(__name__)
class shape:
    def __init__(self, shape, radius, width, height, pos):
        self.shape = shape
        self.radius = radius
        self.width = width
        self.height = height
        self.pos = pos
