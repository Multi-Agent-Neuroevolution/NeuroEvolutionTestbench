use crate::neural_net::Layer;
use crate::neural_net::NeuralNet;
use crate::neural_net::NeuralNetState;
use crate::neural_net::Node;
use iced::Color;
use iced::Point;
use iced::Rectangle;
use iced::{widget::canvas, Renderer};

impl NeuralNet {
    pub fn new(id: u32, layers: Vec<Layer>) -> Self {
        Self { id, layers }
    }

    pub fn draw(&self, bounds: Rectangle, renderer: &Renderer) -> Vec<canvas::Geometry> {
        let mut neural_net_geometry = Vec::new();
        let mut node_geometry = Vec::new();
        let mut neural_net_node_coordinates: Vec<Vec<Point>> = Vec::new();

        let height = bounds.height;
        let width = bounds.width;

        // Get the size of the largest layer for scaling
        let tallest_layer = self.layers.iter().map(|f| f.nodes.len()).max().unwrap_or(1);

        let percent_pad = 3.0;
        let node_radius = self.get_node_radius(height, tallest_layer as f32, percent_pad);
        let horizontal_positions = self.get_layer_positions(width, node_radius * 2.0);

        // Draw each layer
        for (i, layer) in self.layers.iter().enumerate() {
            let x_pos = horizontal_positions[i];
            let (layer_geometry, layer_coordinates) = layer.draw(
                x_pos,
                height,
                renderer,
                node_radius,
                node_radius * percent_pad,
                bounds,
            );
            node_geometry.extend(layer_geometry);
            neural_net_node_coordinates.push(layer_coordinates);
        }
        neural_net_geometry.push(self.draw_edges(bounds, renderer, neural_net_node_coordinates));
        neural_net_geometry.extend(node_geometry);

        neural_net_geometry
    }

    fn draw_edges(
        &self,
        bounds: Rectangle,
        renderer: &Renderer,
        coordinates: Vec<Vec<Point>>,
    ) -> canvas::Geometry {
        let mut frame = canvas::Frame::new(renderer, bounds.size());
        for (i, layer) in coordinates.iter().enumerate() {
            match coordinates.get(i + 1) {
                None => break,
                Some(next_layer) => {
                    for (j, coordinate_start) in layer.iter().enumerate() {
                        for (k, coordinate_end) in next_layer.iter().enumerate() {
                            let weight = self.get_weight(i, j, k);
                            if weight != 0.0 {
                                let edge = canvas::Path::line(*coordinate_start, *coordinate_end);
                                let intensity = (weight.tanh() + 1.0) / 2.0;
                                let color = Color::from_rgb(
                                    intensity as f32,
                                    intensity as f32,
                                    intensity as f32,
                                );
                                frame.fill(&edge, color);
                                frame.stroke(
                                    &edge,
                                    canvas::Stroke::default()
                                        .with_color(Color::BLACK)
                                        .with_width(1.0),
                                );
                            }
                        }
                    }
                }
            }
        }
        frame.into_geometry()
    }

    fn get_weight(&self, i: usize, j: usize, k: usize) -> f64 {
        let weights_option = self
            .layers
            .get(i)
            .unwrap()
            .nodes
            .get(j)
            .unwrap()
            .weights
            .clone();
        match weights_option {
            Some(weights) => return *weights.get(k).unwrap(),
            None => return 0.0,
        }
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
