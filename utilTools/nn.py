# this python code is used to create a basic json file that represents a neural network to be used for displaying in the rust-gui

import json


class NeuralNetwork:
    def __init__(self, nodes, weights):
        self.nodes = nodes
        self.weights = weights

    # converts the nodes and weights to a json string
    def to_json(self):
        return json.dumps({
            'nodes': self.nodes,
            'weights': self.weights
        })

    # def save_to_file(self, filename):
    #    with open(filename, 'w') as f:
    #        f.write(self.to_json())

    # trying an export method that returns the json string instead of writing to a file
    def export(self):
        return self.to_json()


if __name__ == "__main__":
    nodes = [
        {'id': 1, 'value': 0.1},
        {'id': 2, 'value': 0.3},
        {'id': 3, 'value': 0.5}
    ]
    weights = [
        {'from': 1, 'to': 2, 'weight': 0.5},
        {'from': 2, 'to': 3, 'weight': 1.2}
    ]
    neural_network = NeuralNetwork(nodes, weights)
    neural_network.export('neural_network.json')
