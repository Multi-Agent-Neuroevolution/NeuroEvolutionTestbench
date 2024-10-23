use iced::{color, widget::canvas, Point, Renderer, Size};

/*
 * Contains and id and vec of layers for multiple neural nets
 */
pub struct NeuralNet {
    id: u32,
    layers: Vec<Layer>,
}
impl NeuralNet {
    pub fn new(id: u32, layers: Vec<Layer>) -> Self {
        Self { id, layers }
    }
}
pub struct Layer {
    nodes: Vec<Node>,
}
impl Layer {
    pub fn new(nodes: Vec<Node>) -> Self {
        Self { nodes }
    }
}
pub struct Node {
    value: f64,
    weights: Option<Vec<f64>>,
}

impl Node {
    fn new(weights: Vec<f64>) -> Self {
        Self {
            value: 0.0,
            weights: Some(weights),
        }
    }
    fn draw(x: f32, y: f32, renderer: &Renderer, radius: f32) -> canvas::Geometry {
        let mut frame = canvas::Frame::new(renderer, Size::new(radius * 2.0, radius * 2.0));
        let circle = canvas::Path::circle(Point::new(x, y), radius);
        frame.fill(&circle, color!(5));
        frame.into_geometry()
    }
}
impl NullConstructor for Node {
    fn new() -> Self {
        Self {
            value: 0.0,
            weights: None,
        }
    }
}

trait NullConstructor {
    fn new() -> Self;
}
