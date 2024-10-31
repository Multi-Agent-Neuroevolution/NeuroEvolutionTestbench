use iced::{color, widget::canvas, Point, Renderer, Size};
use iced::{Color, Rectangle};
use serde::Deserialize;

mod LayerInter;
mod NeuralNetInter;
mod NodeInter;

#[derive(Default, Clone)]
pub struct NeuralNet {
    id: u32,
    layers: Vec<Layer>,
}

#[derive(Deserialize, Clone, Default)]
pub struct NeuralNetState {
    pub layers: Vec<Vec<f64>>,
}

#[derive(Default, Clone)]
pub struct Layer {
    nodes: Vec<Node>,
}

#[derive(Default, Clone)]
pub struct Node {
    value: f64,
    weights: Option<Vec<f64>>,
}
