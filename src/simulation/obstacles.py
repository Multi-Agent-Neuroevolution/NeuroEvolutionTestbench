"""obstacles.py holds the Obstacle() class and its subclasses."""
from utils import Shape

# Handles the creation of obstacles in the environment
class Obstacle(Shape):
    def __init__(self, pos, shape, radius, width, height, color, interactible, collidable, goal_obstacle):
        super().__init__(shape=shape, radius=radius, width=width, height=height, pos=pos, collidable=collidable)
        self.interactible = interactible
        self.goal_obstacle = goal_obstacle   # goal_obstacle is used to determine if the obstacle is a goal for the agent. NOT USED FOR PREDATOR-PREY
        self.color = color # TO DO: Move color to Shape() class, then adjust all subclasses to account for that
        self.living = True

    def to_dict(self):
        """Empty method to be overridden by subclasses."""
        pass
    
    def get_class(self):
        return self.__class__.__name__

class Food(Obstacle):
    def __init__(self, pos):
        super().__init__(pos=pos, shape="circle", radius=1, width=0, height=0, color="green", interactible=True, collidable=False, goal_obstacle=False)
    
    def to_dict(self):
        return {
            "type": self.shape,
            "x": float(self.pos[0]),
            "y": float(self.pos[1]),
            "radius": self.radius,
            "color": self.color,
        }

class Wall(Obstacle):
    def __init__(self, pos, width, height):
        super().__init__(pos=pos, shape="rectangle", radius=0, width=width, height=height, color="red", interactible=False, collidable=True, goal_obstacle=False)
        # Note to self: may want to make goal_obstacle a parameter in the future depending on ideas
    
    def to_dict(self):
        return {
            "type": self.shape,
            "x": float(self.pos[0]),
            "y": float(self.pos[1]),
            "width": self.width,
            "height": self.height,
            "color": self.color,
        }