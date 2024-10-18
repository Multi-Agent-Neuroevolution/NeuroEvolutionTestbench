


/*
 * Contains and id and vec of layers for multiple neural nets
 */
pub struct NeuralNet{
    id:u32,
    layers:Vec<Layer>

}
impl NeuralNet{
    pub fn new(id:u32,layers:Vec<Layer>)->Self{
        Self{id,layers}
    }
}
pub struct Layer{
    nodes:Vec<Node>
}
impl Layer{
    pub fn new(nodes:Vec<Node>)->Self{
        Self{nodes}
    }

}
pub struct Node{
    value:f64,
    weights:Option<Vec<f64>>
}

impl Node{
    fn new(weights:Vec<f64>)->Self{
        Self{
            value:0.0,
            weights:Some(weights)
        }
    }

}
impl NullContructor for Node{
    fn new()->Self{
        Self{
            value:0.0,
            weights:None
        }
    }
}

trait NullContructor{
    fn new()->Self;

}
