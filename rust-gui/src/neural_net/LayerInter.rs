use crate::neural_net::Layer;
use crate::neural_net::Node;
use iced::{Renderer,widget::canvas,Rectangle};

impl Layer {
    pub fn new(nodes: Vec<Node>) -> Self {
        Self { nodes }
    }

    pub fn draw(
        &mut self,
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

        for (i,node) in self.nodes_mut().iter_mut().enumerate(){
            let y = start_y + i as f32 * (node_radius * 2.0 + padding);
            layer_geometry.push(node.draw(x, y, renderer, node_radius, bounds));
        }
        /*for (i, node) in self.nodes.iter().enumerate() {
            let y = start_y + i as f32 * (node_radius * 2.0 + padding);
            layer_geometry.push(node.draw(x, y, renderer, node_radius, bounds));
        }*/

        layer_geometry
    }
    fn nodes(&self)->&Vec<Node>{
        &self.nodes

    }
    fn nodes_mut(&mut self)->&mut Vec<Node>{
        &mut self.nodes

    }
}
