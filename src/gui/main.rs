// This is the main file for the GUI, it will be responsible for creating the GUI and handling user input
// It is built using the iced crate.

use crate::WebClient::comms::communication_client::CommunicationClient;
use crate::WebClient::comms::JsonData;
use iced::Executor;
use tokio::runtime::Runtime;
use tonic::{Request, Status};
use iced::widget::canvas::{Canvas, Fill, Frame, Geometry, Path};
use iced::widget::{button, canvas, column, row, text, Column, Row};
use iced::{mouse, Color, Length, Point, Rectangle, Renderer, Size, Subscription, Theme};
use tokio::sync::mpsc;
use tokio::sync::mpsc::{Receiver, Sender};
use WebClient::getConnection;
mod WebClient;
mod neural_net;
mod sim_view;
use iced::time;
use neural_net::{Layer, NeuralNet};
use serde::{Deserialize, Serialize};
use serde_json;
use sim_view::{Shape, Simulation};
use std::future::IntoFuture;
use std::time::Duration;
use tonic::transport::Channel;

#[derive(Default)]
struct View {
    speed: i32,
    agent_view: AgentView,
    sim_view: SimulationView,
    nn_view: NNView,
    simulation_data: SimulationData,
    receiver: Option<Receiver<JsonData>>,
    sender: Option<Sender<JsonData>>,
    connection: Option<CommunicationClient<Channel>>
}
#[derive(Default, Clone)]
struct SimulationView {
    //This is going to be deprecated or deleteds
    color: Color,
    simulation: Simulation,
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
    IncrementPressedx10,
    DecrementPressed,
    DecrementPressedx10,
    Tick,
    SimStart,
    SimPause,
    SimEnd,
}

#[derive(Deserialize, Clone, Default)]
struct Agent {
    id: usize,
    x: f64,
    y: f64,
}

#[derive(Deserialize, Clone, Default)]
struct SimulationData {
    agents: Vec<Agent>,
    shapes: Vec<Shape>,
    layers: Vec<Layer>,
}

pub fn main() -> iced::Result {
    iced::application("Multi Agent Neural Evolution", View::update, View::view)
        .subscription(View::subscription)
        .theme(|_| Theme::GruvboxDark)
        .antialiasing(true)
        .centered()
        .run()
}
impl View {
    fn new() -> Self {
        let (send, recv) = mpsc::channel::<JsonData>(100000000000000);
        let rt = Runtime::new().unwrap();
        let conn = rt.block_on(getConnection()).unwrap();
        Self {
            speed: 1,
            agent_view: AgentView::new(),
            sim_view: SimulationView::new(),
            nn_view: NNView::new(),
            simulation_data: SimulationData::default(),
            receiver: Some(recv),
            sender: Some(send),
            connection: Some(conn)
        }
    }
    fn view(&self) -> Column<Message> {
        //SimulationView
        let sim_view = self
            .sim_view
            .draw()
            .width(Length::FillPortion(65))
            .height(Length::Fill);
        //AgentView
        let agent_view = self.agent_view.view();
        //NNViews
        let nn_view = self.nn_view.draw();
        let agent_nn_col = column!(agent_view, nn_view)
            .width(Length::FillPortion(35))
            .height(Length::Fill);

        let content = row!(sim_view, agent_nn_col)
            .width(Length::Fill)
            .height(Length::Fill);

        let container = column![self.controls(), content];
        container
    }
    fn controls(&self) -> Row<Message> {
        //Top Controls
        let top_controls = row![
            button("File"),
            button("Edit"),
            button("View"),
            button("<<").on_press(Message::DecrementPressedx10),
            button("<").on_press(Message::DecrementPressed),
            text(format!("x{}", self.speed)),
            button(">").on_press(Message::IncrementPressed),
            button(">>").on_press(Message::IncrementPressedx10)
        ]
        .spacing(10);
        top_controls
    }
    fn update(&mut self, message: Message) {
        match message {
            Message::IncrementPressed => self.speed += 1,
            //prevent speed from going negative
            Message::DecrementPressed => self.speed = self.speed.saturating_sub(1),
            Message::IncrementPressedx10 => self.speed += 10,
            Message::DecrementPressedx10 => self.speed = self.speed.saturating_sub(10),
            Message::Tick => {
            }
            Message::SimStart => {
                let rt = Runtime::new().unwrap();
                let cloneConn = self.connection.as_mut().unwrap().clone();
                let cloneSend = self.sender.as_mut().unwrap().clone();
                rt.spawn(async { WebClient::getSimStream(cloneConn, cloneSend); });
                for _i in 0..999{
                    self.get_simulation_data();
                }
            }
            Message::SimPause => {}
            Message::SimEnd => {}
        }
        if self.speed < 1 {
            self.speed = 1;
        }
        // let simulation_data = self.get_simulation_data();
        // self.update_simulation_data(simulation_data);
    }
    fn get_simulation_data(&mut self) -> SimulationData {
        //In the future this will be replaced with a function that gets the data from the simulation over a web socket
        /*let json_data = r#"
        {
            "agents": [
                {
                    "id": 1,
                    "x": 0.0,
                    "y": 0.0,
                    "color": "white"

                },
                {
                    "id": 2,
                    "x": 1.0,
                    "y": 1.0,
                    "color": "blue"
                }
            ],
            "shapes": [
                {
                    "type": "Circle",
                    "x": 350.0,
                    "y": 450.0,
                    "radius": 50.0,
                    "color": "purple"
                },
                {
                    "type": "Rectangle",
                    "x": 0.0,
                    "y": 0.0,
                    "width": 50.0,
                    "height": 5000.0,
                    "color": "white"
                },
                {
                    "type": "Rectangle",
                    "x": 100.0,
                    "y": 100.0,
                    "width": 50.0,
                    "height": 50.0,
                    "color": "red"
                },
                {
                    "type": "Triangle",
                    "x1": 50.0,
                    "y1": 50.0,
                    "x2": 100.0,
                    "y2": 85.0,
                    "x3": 50.0,
                    "y3": 120.0,
                    "color": "blue"
                },
                {
                    "type": "Line",
                    "x1": 450.0,
                    "y1": 250.0,
                    "x2": 200.0,
                    "y2": 100.0,
                    "color": "green"

                }
            ],
        "layers": [
        {
                "nodes": [
                        {
                                "value": 3.4,
                                "weights": [0.74, 3.34, 9.50, 0.1]
                        },
                        {
                                "value": 0.004,
                                "weights": [0.074, 5.34, 1.50, 4.1]
                        }

                    ]
            },
            {
                "nodes": [
                        {
                                "value": 3.4,
                                "weights": [0.74, 3.34, 9.50, 0.1]
                        },
                        {
                                "value": 47.2,
                                "weights": [0.89, 0.16, 6.7, 0.01]
                        },
                        {
                                "value": 33.9,
                                "weights": [6.9, 5.26, 2.91, 1.43]
                        },
                        {
                                "value": 2.9,
                                "weights": [69, 1.1, 3.11, 200]
                        }
                    ]
            },
            {
                "nodes": [
                        {
                                "value": 3.4,
                                "weights": [0.74, 3.34, 9.50]
                        },
                        {
                                "value": 47.2,
                                "weights": [0.89, 0.16, 6.7]
                        },
                        {
                                "value": 33.9,
                                "weights": [6.9, 5.26, 2.91]
                        },
                        {
                                "value": 2.9,
                                "weights": [69, 1.1, 3.11]
                        }
                    ]
            },
            {
                    "nodes": [
                        {
                                "value": 22.1
                        },
                        {
                                "value": 6.4
                        },
                        {
                                "value": 1.1
                        }
                    ]
            }
        ]
        }
        "#;*/

        /*let json_data: SimulationData =
            serde_json::from_str(&self.receiver.as_mut().unwrap().recv().unwrap().json_data)
                .expect("Failed to parse JSON");*/
        //let simulation_data = self.get_simulation_data();
        let received = &self.receiver.as_mut().unwrap().blocking_recv().unwrap().json_data;
        let json_data: SimulationData = serde_json::from_str(&received).expect("Failed to parse JSON");
        self.update_simulation_data(json_data.clone());
        json_data
    }
    fn update_simulation_data(&mut self, simulation_data: SimulationData) {
        self.simulation_data = simulation_data;
        self.agent_view.color = Color::from_rgb(0.0, 1.0, 0.0);
        self.nn_view.update_network(&self.simulation_data.layers);
        self.sim_view.update_sim(&self.simulation_data.shapes);
    }
    fn subscription(&self) -> Subscription<Message> {
        time::every(Duration::from_millis(16)).map(|_| Message::Tick)
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
            button("Pause")
                .width(Length::FillPortion(1))
                .on_press(Message::SimPause),
            button("Play")
                .width(Length::FillPortion(1))
                .on_press(Message::SimStart),
            button("Step").width(Length::FillPortion(1))
        ];
        controls
    }
}

impl NNView {
    pub fn new() -> Self {
        Self {
            color: Color::from_rgb(0.0, 0.0, 1.0),
            neural_net: NeuralNet::default(),
        }
    }
    pub fn update_network(&mut self, neural_state: &Vec<Layer>) {
        self.neural_net = NeuralNet::from_data(neural_state)
    }
    pub fn draw(&self) -> Column<Message> {
        let nn_view = Canvas::new(self).width(Length::Fill).height(Length::Fill);
        let container = column![nn_view];
        container
    }
}

impl SimulationView {
    pub fn new() -> Self {
        Self {
            color: Color::from_rgb(1.0, 0.0, 0.0),
            simulation: Simulation::new(),
        }
    }
    pub fn update_sim(&mut self, shapes: &Vec<Shape>) {
        self.simulation.add_shapes(shapes);
    }
    pub fn draw(&self) -> Column<Message> {
        let sim_view = Canvas::new(self).width(Length::Fill).height(Length::Fill);
        let container = column![sim_view];
        container
    }
}

impl<Message> canvas::Program<Message> for SimulationView {
    //This will be in charge of drawing the simulation
    //The actual simulation will be handled somewhere else.
    type State = ();
    fn draw(
        &self,
        _state: &(),
        renderer: &Renderer,
        _theme: &Theme,
        bounds: Rectangle,
        _cursor: mouse::Cursor,
    ) -> Vec<canvas::Geometry> {
        self.simulation.draw(renderer, bounds)
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
        renderer: &Renderer,
        _theme: &Theme,
        bounds: Rectangle,
        _cursor: mouse::Cursor,
    ) -> Vec<canvas::Geometry> {
        self.neural_net.draw(bounds, renderer)
    }
}
