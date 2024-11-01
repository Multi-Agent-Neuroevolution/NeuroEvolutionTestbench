use iced::{color, widget::canvas, Point, Renderer, Size};
use iced::{Color, Rectangle};
use serde::Deserialize;

mod LayerInter;
mod NeuralNetInter;
mod NodeInter;

#[derive(Deserialize, Clone, Default)]
pub struct NeuralNet {
    id: u32,
    layers: Vec<Layer>,
}

#[derive(Deserialize, Default, Clone)]
#[serde(tag = "nodes")]
pub struct Layer {
    nodes: Vec<Node>,
}

#[derive(Deserialize, Default, Clone)]
pub struct Node {
    value: f64,
    weights: Option<Vec<f64>>,
}
