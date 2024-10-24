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
    fn draw(&self,width:f32,height:f32,renderer:&Renderer)->Vec<canvas::Geometry>{

        let mut NeuralNetGeometry = Vec::new();

        let percentPad = 0.05;
        let tallestLayer = self.layers.iter().map(|f|f.nodes.len()).max();

        let mut layerCount=0;
        if let Some(layerSize) = tallestLayer{
            layerCount=layerSize;
        }
        let node_radius = &self.get_Node_radius(height, layerCount as f32, percentPad);
        let horizontal_positions = &self.get_Layer_positions(width, 10.0);

        for i in 0..self.layers.len(){
            let currentlayer=self.layers.get(i).expect("No Layer found");
            let current_x_pos=horizontal_positions.get(i).expect("No position found");

            let LayerGeometery = currentlayer.draw(*current_x_pos, height, renderer, *node_radius, node_radius*percentPad);
            NeuralNetGeometry.extend(LayerGeometery);

        }


        NeuralNetGeometry
    }
    fn get_Node_radius(&self,size:f32,sections:f32,percentPad:f32)->f32{
        let node_Size:f32 = (size/sections)*(1.0-percentPad);
        node_Size
    }
    fn get_Layer_positions(&self,width:f32,padding:f32)->Vec<f32>{
        let distance = (width-(2.0*padding))/(self.layers.len() as f32);
        let mut x_positions = Vec::new();
        let mut x_position=padding;
        for _i in 0..self.layers.len(){
            x_positions.push(x_position);
            x_position = x_position + distance;
        }
        x_positions
    }
}
pub struct Layer {
    nodes: Vec<Node>,
}
impl Layer {
    pub fn new(nodes: Vec<Node>) -> Self {
        Self { nodes }
    }
    /*
     * draw a layer calculate the even amount of nodes to have them centered node size will be calculated in neural net struct to make sure the nodes stay in the window
     */
    fn draw(&self,x:f32,height:f32,renderer:&Renderer,nodeSize:f32,padding:f32)->Vec<canvas::Geometry>{
        let mut y = height;
        let mut layerGeometry = Vec::new();

        let layer_height = ((self.nodes.len() as f32)*nodeSize*2.0)+(((self.nodes.len()-1) as f32)*padding);
        let space_remaining = height - layer_height;
        let mut offset = layer_height + space_remaining/2.0;

        for node in self.nodes{//@TODO FIX THIS COMPILATION ERROR
            layerGeometry.push(node.draw(x, offset, renderer, nodeSize));
            offset = offset - (nodeSize*2.0 + padding);//node size is radius and circle drawer sets x and y on center so need to be nodeSize*2
        }
        layerGeometry

    }
}
pub struct Node {
    value: f64,
    weights: Option<Vec<f64>>,
    coordinates: Point
}

impl Node {
    fn new(weights: Vec<f64>) -> Self {
        Self {
            coordinates: Point::new(0.0, 0.0),
            value: 0.0,
            weights: Some(weights),
        }
    }
    /**
     * draw a node at x and with with a radius called by layer struct @TODO make configurable color
     *
     */
    fn draw(&self,x: f32, y: f32, renderer: &Renderer, radius: f32) -> canvas::Geometry {

        let mut frame = canvas::Frame::new(renderer, Size::new(radius * 2.0, radius * 2.0));
        let circle = canvas::Path::circle(Point::new(x, y), radius);
        frame.fill(&circle, color!(5));
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
