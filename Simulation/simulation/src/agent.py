import numpy as np
from collections import defaultdict

# This class works in conjunction with the Agent class, used to store all metrics calculated from agent performance
# Some metric ideas...
    # fitness -> score "physical" capability somehow? or see how fitness is historically calculated
    # age -> already a variable for Agents, but could use value to gauge health
    
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

class Agent:
    def __init__(self, id, algorithm_name, relationship_name, pos):
        self.id = id;
        self.age = 0;
        self.selected_algorithm = self.init_algorithm(algorithm_name);
        self.selected_relationship = self.init_relationship(relationship_name);
        self.pos = np.array(pos);
        self.metrics = Metrics();
        
    def init_algorithm(self, algorithm_name):
        try:
            # This allows more algorithms to be implemented later on with elif
            if algorithm_name == "NEAT":
                # Code that calls function initializing NEAT algorithm
                pass # remove these when actual code is implemented
        except:
            print(f"Invalid algorithm specified! {algorithm_name} is not implemented.")
            
    # Not sure if this def would be necessary, but this is would be skeletal groundwork
    def init_relationship(self, relationship_name):
        try:
            if relationship_name == "PRED_PREY": # Just an example
                # Code that calls function initializing relationship type
                pass
        except:
            print(f"Invalid relationship specified! {relationship_name} is not implemented.")
            
    # Update the position of the agent every tick (could be handled differently? Again skeletal basic idea)
    def update_pos(self):
        """
        empty for now
        """
        pass
        
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
