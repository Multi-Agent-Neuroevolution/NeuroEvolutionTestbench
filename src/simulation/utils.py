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

    def getRenderData(self):
        if self.shape == "Circle":
            return {"type":"Circle","x":self.pos[0],"y":self.pos[1],"radius":self.radius,"Color":"green"}
        else:
            return {"type":"Rectangle","x":self.pos[0],"y":self.pos[1],"witdth":self.width,"height":self.height,"Color":"red"}
