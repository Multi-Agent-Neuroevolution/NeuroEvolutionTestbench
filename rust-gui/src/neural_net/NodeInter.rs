use crate::neural_net::Node;
use iced::{color,widget::canvas,Point,Renderer,Size,Color,Rectangle};
impl Node {
    pub fn new(value: f64) -> Self {
        Self {
            coordinates: Point::new(0.0, 0.0),
            value,
            weights: None,
        }
    }

    pub fn draw(
        &mut self,
        x: f32,
        y: f32,
        renderer: &Renderer,
        radius: f32,
        bounds: Rectangle,
    ) -> canvas::Geometry {

        let coordinates = Point::new(x,y);
        let mut frame = canvas::Frame::new(renderer, bounds.size());

        // Create circle path centered at the given coordinates
        let circle = canvas::Path::circle(coordinates, radius);
        self.setCoordinates(coordinates);

        // Calculate color based on node value
        let intensity = (self.value.tanh() + 1.0) / 2.0;
        let color = Color::from_rgb(intensity as f32, intensity as f32, intensity as f32);

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

    fn setCoordinates(&mut self, point:Point){
        self.coordinates = point;
    }
    fn getCoordinates(&self)->Point{
        self.coordinates
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
impl weightedConstructor for Node {
    fn new(value:f64,weights:Vec<f64>)->Self{
        Node{
            coordinates: Point::new(0.0, 0.0),
            value,
            weights: Some(weights),
        }

    }

}

trait NullConstructor {
    fn new() -> Self;
}
trait weightedConstructor {
    fn new(value:f64,weights:Vec<f64>)->Self;
}
