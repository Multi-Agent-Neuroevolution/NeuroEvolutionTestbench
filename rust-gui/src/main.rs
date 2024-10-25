// This is the main file for the GUI, it will be responsible for creating the GUI and handling user input
// It is built using the iced crate.

use iced::border::width;
use iced::widget::canvas::{Canvas, Fill, Frame, Geometry, Path};
use iced::widget::{button, canvas, column, pane_grid, row, text, Column, PaneGrid, Row, Text};
use iced::{mouse, Color, Length, Point, Rectangle, Renderer, Size, Theme};
mod neural_net;
use neural_net::{NeuralNet, NeuralNetState};
use serde::{Deserialize, Serialize};
use serde_json;
#[derive(Default, Clone)]
struct View {
    counter: i32,
    agent_view: AgentView,
    sim_view: SimulationView,
    nn_view: NNView,
}
#[derive(Default, Clone, Copy)]
struct SimulationView {
    color: Color,
}
#[derive(Default, Clone, Copy)]
struct AgentView {
    color: Color,
}
#[derive(Default, Clone)]
struct NNView {
    color: Color,
    neural_net: NeuralNet,
}

#[derive(Debug, Clone, Copy)]
enum Message {
    IncrementPressed,
    DecrementPressed,
}

#[derive(Deserialize)]
struct Agent {
    id: usize,
    x: f64,
    y: f64,
}

#[derive(Deserialize)]
#[serde(tag = "type")]
enum Shape {
    Circle {
        x: f64,
        y: f64,
        radius: f64,
        color: String,
    },
    Rectangle {
        x: f64,
        y: f64,
        width: f64,
        height: f64,
        color: String,
    },
    Triangle {
        x1: f64,
        y1: f64,
        x2: f64,
        y2: f64,
        x3: f64,
        y3: f64,
        color: String,
    },
    Line {
        x1: f64,
        y1: f64,
        x2: f64,
        y2: f64,
        color: String,
    },
}

#[derive(Deserialize)]
struct SimulationData {
    agents: Vec<Agent>,
    shapes: Vec<Shape>,
    neural_state: NeuralNetState,
}

fn main() {
    let _ = iced::run(
        "Multi-agent Neuroevolution Simulator",
        View::update,
        View::view,
    );
}

impl View {
    fn new() -> Self {
        Self {
            counter: 0,
            agent_view: AgentView::new(),
            sim_view: SimulationView::new(),
            nn_view: NNView::new(),
        }
    }
    fn view(&self) -> Column<Message> {
        //Top Controls
        let top_controls = row![
            button("File"),
            button("Edit"),
            button("View"),
            button("<"),
            text("0x"),
            button(">")
        ]
        .spacing(10);

        //SimulationView
        let sim_view = self
            .sim_view
            .view()
            .width(Length::FillPortion(65))
            .height(Length::Fill);
        //AgentView
        let agent_view = self.agent_view.view();
        //NNView
        let nn_view = self.nn_view.view();

        let agent_nn_col = column!(agent_view, nn_view)
            .width(Length::FillPortion(35))
            .height(Length::Fill);

        let content = row!(sim_view, agent_nn_col)
            .width(Length::Fill)
            .height(Length::Fill);

        let container = column![top_controls, content];
        container
    }
    fn update(&mut self, message: Message) {
        // match message {
        //     Message::IncrementPressed => self.counter += 1,
        //     Message::DecrementPressed => self.counter -= 1,
        // }
        //This function will handle updating the simulation, agents, and neural network
        //It is going to have to use some type of timer so it still updates even if the user is not interacting with the app
        //It will also need to interface with a websocket to get the data from the simulation, so it is going to need to be async or something
    }
}

impl AgentView {
    pub fn new() -> Self {
        Self {
            color: Color::from_rgb(0.0, 1.0, 0.0),
        }
    }
    fn view(&self) -> Column<Message> {
        let agent_view = canvas(AgentView {
            color: Color::from_rgb(0.0, 1.0, 0.0),
        })
        .width(Length::Fill)
        .height(Length::Fill);
        let container = column![agent_view, self.controlls()];
        container
    }
    fn controlls(&self) -> Row<Message> {
        let controls = row![
            button("Add Agent"),
            button("Remove Agent"),
            button("Pause"),
            button("Play"),
            button("Step"),
            button("Reset")
        ];
        controls
    }
}

impl NNView {
    pub fn new() -> Self {
        // Parse your JSON and create neural network
        let json_data = r#"
        {
            "neuralnet_state": {
                "layers": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            }
        }
        "#;
        let json_data: SimulationData =
            serde_json::from_str(json_data).expect("Failed to parse JSON");
        let neural_net = NeuralNet::from_data(&json_data.neural_state);

        Self {
            color: Color::from_rgb(0.0, 0.0, 1.0),
            neural_net,
        }
    }

    fn view(&self) -> Column<Message> {
        let nn_view = Canvas::new(self).width(Length::Fill).height(Length::Fill);

        Column::new().push(nn_view)
    }
}

impl SimulationView {
    pub fn new() -> Self {
        Self {
            color: Color::from_rgb(1.0, 0.0, 0.0),
        }
    }
    fn view(&self) -> Column<Message> {
        let sim_view = canvas(SimulationView {
            color: Color::from_rgb(1.0, 0.0, 0.0),
        })
        .width(Length::Fill)
        .height(Length::Fill);
        let container = column![sim_view];
        container
    }
}

impl<Message> canvas::Program<Message> for SimulationView {
    //This will be in charge of drawing the simulation
    //The actual simulation will be handled somewhere else. Proabably
    type State = ();
    fn draw(
        &self,
        _state: &(),
        renderer: &Renderer,
        _theme: &Theme,
        bounds: Rectangle,
        _cursor: mouse::Cursor,
    ) -> Vec<canvas::Geometry> {
        let mut frame = canvas::Frame::new(renderer, bounds.size());
        let rect = canvas::Path::rectangle(Point::new(0.0, 0.0), frame.size());
        frame.fill(&rect, self.color);
        vec![frame.into_geometry()]
    }
}

impl<Message> canvas::Program<Message> for AgentView {
    type State = ();
    fn draw(
        &self,
        _state: &(),
        renderer: &Renderer,
        _theme: &Theme,
        bounds: Rectangle,
        _cursor: mouse::Cursor,
    ) -> Vec<canvas::Geometry> {
        let mut frame = canvas::Frame::new(renderer, bounds.size());
        let rect = canvas::Path::rectangle(Point::new(0.0, 0.0), frame.size());
        frame.fill(&rect, self.color);
        vec![frame.into_geometry()]
    }
}

impl<Message> canvas::Program<Message> for NNView {
    type State = ();

    fn draw(
        &self,
        _state: &(),
        renderer: &Renderer, // We'll use this renderer directly
        _theme: &Theme,
        bounds: Rectangle,
        _cursor: mouse::Cursor,
    ) -> Vec<Geometry> {
        let mut frame = Frame::new(renderer, bounds.size());

        // Call your neural network draw function with the provided renderer
        let geometries = self.neural_net.draw(
            bounds.width,
            bounds.height,
            renderer, // Use the renderer parameter directly
        );

        // Combine the neural network geometries with any background/additional drawing
        let mut all_geometries = Vec::new();

        // Add background if desired
        let background = canvas::Path::rectangle(Point::new(0.0, 0.0), frame.size());
        frame.fill(&background, self.color);
        all_geometries.push(frame.into_geometry());

        // Add neural network geometries
        all_geometries.extend(geometries);

        all_geometries
    }
}
