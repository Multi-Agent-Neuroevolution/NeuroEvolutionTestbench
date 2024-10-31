use crate::neural_net::Layer;
use crate::neural_net::NeuralNet;
use crate::neural_net::NeuralNetState;
use crate::neural_net::Node;
use iced::Rectangle;
use iced::{widget::canvas, Renderer};

impl NeuralNet {
    pub fn new(id: u32, layers: Vec<Layer>) -> Self {
        Self { id, layers }
    }

    pub fn draw(&self, bounds: Rectangle, renderer: &Renderer) -> Vec<canvas::Geometry> {
        let mut neural_net_geometry = Vec::new();
        let height = bounds.height;
        let width = bounds.width;

        // Get the size of the largest layer for scaling
        let tallest_layer = self.layers.iter().map(|f| f.nodes.len()).max().unwrap_or(1);

        let percent_pad = 0.0;
        let node_radius = self.get_node_radius(height, tallest_layer as f32, percent_pad);
        let horizontal_positions = self.get_layer_positions(width, node_radius * 2.0);

        // Draw connections between layers first (if you want to add this feature)
        // TODO: Add connection drawing logic here

        // Draw each layer
        for (i, layer) in self.layers.iter().enumerate() {
            let x_pos = horizontal_positions[i];
            let layer_geometry = layer.draw(
                x_pos,
                height,
                renderer,
                node_radius,
                node_radius * percent_pad,
                bounds,
            );
            neural_net_geometry.extend(layer_geometry);
        }

        neural_net_geometry
    }

    fn get_node_radius(&self, height: f32, sections: f32, percent_pad: f32) -> f32 {
        (height / (sections * 5.0)) * (1.0 - (percent_pad / 100.0))
    }

    fn get_layer_positions(&self, width: f32, node_diameter: f32) -> Vec<f32> {
        let padding = node_diameter;
        let available_width = width - (2.0 * padding);
        let distance = available_width / (self.layers.len().max(1) as f32 - 1.0);

        (0..self.layers.len())
            .map(|i| padding + (distance * i as f32))
            .collect()
    }

    /*
     * @TODO need to update this function to fit weights
     */
    pub fn from_data(data: &NeuralNetState) -> Self {
        let layers: Vec<Layer> = data
            .layers
            .iter()
            .map(|layer| {
                let nodes: Vec<Node> = layer.iter().map(|&value| Node::new(value)).collect();
                Layer::new(nodes)
            })
            .collect();

        NeuralNet::new(1, layers)
    }
}
