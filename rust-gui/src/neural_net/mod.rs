use iced::{color, widget::canvas, Point, Renderer, Size};
use iced::{Color, Rectangle};
use serde::Deserialize;

#[derive(Default, Clone)]
pub struct NeuralNet {
    id: u32,
    layers: Vec<Layer>,
}

#[derive(Deserialize, Clone, Default)]
pub struct NeuralNetState {
    pub layers: Vec<Vec<f64>>,
}

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
        (height / (sections * 1.0)) * (1.0 - (percent_pad / 100.0))
    }

    fn get_layer_positions(&self, width: f32, node_diameter: f32) -> Vec<f32> {
        let padding = node_diameter;
        let available_width = width - (2.0 * padding);
        let distance = available_width / (self.layers.len().max(1) as f32 - 1.0);

        (0..self.layers.len())
            .map(|i| padding + (distance * i as f32))
            .collect()
    }

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

#[derive(Default, Clone)]
pub struct Layer {
    nodes: Vec<Node>,
}

impl Layer {
    pub fn new(nodes: Vec<Node>) -> Self {
        Self { nodes }
    }

    fn draw(
        &self,
        x: f32,
        canvas_height: f32,
        renderer: &Renderer,
        node_radius: f32,
        padding: f32,
        bounds: Rectangle,
    ) -> Vec<canvas::Geometry> {
        let mut layer_geometry = Vec::new();

        // Calculate total height needed for nodes + padding
        let total_node_height = (self.nodes.len() as f32) * (node_radius * 2.0);
        let total_padding = ((self.nodes.len() - 1) as f32) * padding;
        let layer_height = total_node_height + total_padding;

        // Calculate starting y position to center the layer
        let start_y = (canvas_height - layer_height) / 2.0 + node_radius;

        for (i, node) in self.nodes.iter().enumerate() {
            let y = start_y + i as f32 * (node_radius * 2.0 + padding);
            layer_geometry.push(node.draw(x, y, renderer, node_radius, bounds));
        }

        layer_geometry
    }
}

#[derive(Default, Clone)]
pub struct Node {
    value: f64,
    coordinates: Point,
    weights: Option<Vec<f64>>,
}

impl Node {
    fn new(value: f64) -> Self {
        Self {
            coordinates: Point::new(0.0, 0.0),
            value,
            weights: None,
        }
    }

    fn draw(
        &self,
        x: f32,
        y: f32,
        renderer: &Renderer,
        radius: f32,
        bounds: Rectangle,
    ) -> canvas::Geometry {
        let mut frame = canvas::Frame::new(renderer, bounds.size());

        // Create circle path centered at the given coordinates
        let circle = canvas::Path::circle(Point::new(x, y), radius);

        // Calculate color based on node value
        let intensity = (self.value.tanh() + 1.0) / 2.0;
        let color = Color::from_rgb(intensity as f32, 0.0, 0.0);

        // Fill and stroke the circle
        frame.fill(&circle, color);
        frame.stroke(
            &circle,
            canvas::Stroke::default()
                .with_color(Color::BLACK)
                .with_width(1.0),
        );

        frame.into_geometry()
    }
}

impl NullConstructor for Node {
    fn new() -> Self {
        Self {
            coordinates: Point::new(0.0, 0.0),
            value: 0.0,
            weights: None,
        }
    }
}

trait NullConstructor {
    fn new() -> Self;
}
