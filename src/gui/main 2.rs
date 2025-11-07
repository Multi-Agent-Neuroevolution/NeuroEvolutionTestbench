// This is the main file for the GUI, it will be responsible for creating the GUI and handling user input
// It is built using the iced crate.

use crate::WebClient::comms::communication_client::CommunicationClient;
use crate::WebClient::comms::JsonData;
use iced::widget::canvas::{Canvas, Fill, Frame, Geometry, Path};
use iced::widget::{button, canvas, column, row, text, Column, Row};
use iced::Executor;
use iced::{mouse, Color, Length, Point, Rectangle, Renderer, Size, Subscription, Theme};
use std::sync::mpsc::{Receiver, Sender};
use tokio::runtime::Runtime;
use tokio::sync::mpsc;
use tonic::{Request, Status};
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
use std::thread::sleep;
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
    connection: Option<CommunicationClient<Channel>>,
    rt: Option<Runtime>,
    isRunning: bool,
    selected_agent_id: Option<usize>,
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
    BestAgent,
    SimEnd,
    AgentSelected(usize),
    NextAgent,
    PrevAgent,
}

#[derive(Deserialize, Clone, Default)]
struct Agent {
    id: usize,
    x: f32,
    y: f32,
    color: String,
    agent_type: Option<String>,
    energy: Option<f32>,
    fitness: Option<f32>,
    age: Option<u32>,
    alive: Option<bool>,
    move_speed: Option<f32>,
    sight: Option<f32>,
    #[serde(rename = "type")]
    agent_subtype: Option<i32>,
    prey_eaten: Option<u32>,
}

#[derive(Deserialize, Clone, Default)]
struct SimulationData {
    agents: Vec<Agent>,
    shapes: Vec<Shape>,
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
        let (send, recv) = std::sync::mpsc::channel::<JsonData>();
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
            connection: Some(conn),
            rt: Some(rt),
            isRunning: false,
            selected_agent_id: None,
        }
    }
    fn view(&self) -> Column<Message> {
        // Get selected agent
        let selected_agent = self
            .selected_agent_id
            .and_then(|id| self.simulation_data.agents.iter().find(|a| a.id == id));

        //SimulationView
        let sim_view = self.sim_view.draw().height(Length::Fill);
        //AgentView
        let agent_view = self.agent_view.view(selected_agent);
        //NNViews
        let nn_view = self.nn_view.draw();
        let agent_nn_col = column!(agent_view, nn_view);

        let content = row!(sim_view, agent_nn_col);

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
                self.get_simulation_data();
            }
            Message::SimStart => {
                let cloneConn = match self.connection.as_mut() {
                    Some(conn) => conn.clone(),
                    None => match self.rt.as_mut() {
                        Some(rt) => rt.block_on(getConnection()).unwrap(),
                        None => {
                            self.rt = Some(Runtime::new().unwrap());
                            self.rt.as_mut().unwrap().block_on(getConnection()).unwrap()
                        }
                    },
                };
                //let cloneConn = self.connection.as_mut().unwrap().clone();
                let cloneSend = match self.sender.as_mut() {
                    Some(send) => send.clone(),
                    None => {
                        let (send, recv) = std::sync::mpsc::channel::<JsonData>();
                        self.sender = Some(send.clone());
                        self.receiver = Some(recv);
                        send
                    }
                };
                self.rt.as_mut().unwrap().spawn(async move {
                    WebClient::getSimStream(cloneConn, cloneSend).await;
                });
                self.isRunning = true;
            }
            Message::SimEnd => {}
            Message::AgentSelected(agent_id) => {
                self.selected_agent_id = Some(agent_id);
                self.fetch_neural_network(agent_id);
            }
            Message::NextAgent => {
                if !self.simulation_data.agents.is_empty() {
                    let current_index = self
                        .selected_agent_id
                        .and_then(|id| self.simulation_data.agents.iter().position(|a| a.id == id))
                        .unwrap_or(0);
                    let next_index = (current_index + 1) % self.simulation_data.agents.len();
                    let next_agent_id = self.simulation_data.agents[next_index].id;
                    self.selected_agent_id = Some(next_agent_id);
                    self.fetch_neural_network(next_agent_id);
                }
            }
            Message::PrevAgent => {
                if !self.simulation_data.agents.is_empty() {
                    let current_index = self
                        .selected_agent_id
                        .and_then(|id| self.simulation_data.agents.iter().position(|a| a.id == id))
                        .unwrap_or(0);
                    let prev_index = if current_index == 0 {
                        self.simulation_data.agents.len() - 1
                    } else {
                        current_index - 1
                    };
                    let prev_agent_id = self.simulation_data.agents[prev_index].id;
                    self.selected_agent_id = Some(prev_agent_id);
                    self.fetch_neural_network(prev_agent_id);
                }
            }
            Message::BestAgent => {
                if !self.simulation_data.agents.is_empty() {
                    if let Some(best_agent) = self.simulation_data.agents.iter().max_by(|a, b| {
                        a.fitness
                            .unwrap_or(0.0)
                            .partial_cmp(&b.fitness.unwrap_or(0.0))
                            .unwrap()
                    }) {
                        self.selected_agent_id = Some(best_agent.id);
                        self.fetch_neural_network(best_agent.id);
                    }
                }
            }
        }
        if self.speed < 1 {
            self.speed = 1;
        }
    }
    fn get_simulation_data(&mut self) {
        if let Some(receiver) = &mut self.receiver {
            match receiver.try_recv() {
                Ok(sentData) => {
                    let received = &sentData.json_data;
                    match serde_json::from_str::<SimulationData>(&received) {
                        Ok(json_data) => self.update_simulation_data(json_data),
                        Err(e) => println!("Failed to parse JSON: {}", e),
                    }
                }
                Err(std::sync::mpsc::TryRecvError::Empty) => {
                    // No data available, that's fine
                }
                Err(std::sync::mpsc::TryRecvError::Disconnected) => {
                    println!("Channel disconnected");
                    self.isRunning = false;
                }
            }
        }
    }

    fn fetch_neural_network(&mut self, agent_id: usize) {
        if let Some(connection) = &mut self.connection {
            if let Some(rt) = &mut self.rt {
                let mut conn_clone = connection.clone();
                rt.spawn(async move {
                    match WebClient::getNeuralNet(&mut conn_clone, agent_id as i32).await {
                        neural_data => {
                            // TODO: Parse neural data and update nn_view
                            println!(
                                "Received neural network data for agent {}: {:?}",
                                agent_id, neural_data
                            );
                        }
                    }
                });
            }
        }
    }
    fn update_simulation_data(&mut self, simulation_data: SimulationData) {
        self.simulation_data = simulation_data;

        // Auto-select first agent if none is selected and agents exist
        if self.selected_agent_id.is_none() && !self.simulation_data.agents.is_empty() {
            self.selected_agent_id = Some(self.simulation_data.agents[0].id);
            self.fetch_neural_network(self.simulation_data.agents[0].id);
        }

        self.agent_view.color = Color::from_rgb(0.0, 1.0, 0.0);
        //self.nn_view.update_network(&self.simulation_data.layers);
        self.sim_view
            .update_sim(&self.simulation_data.shapes, &self.simulation_data.agents);
    }
    fn subscription(&self) -> Subscription<Message> {
        if self.isRunning {
            time::every(Duration::from_millis(1)).map(|_| Message::Tick)
        } else {
            Subscription::none()
        }
    }
}

impl AgentView {
    pub fn new() -> Self {
        Self {
            color: Color::from_rgb(0.0, 1.0, 0.0),
        }
    }
    fn view(&self, selected_agent: Option<&Agent>) -> Column<Message> {
        let agent_info = if let Some(agent) = selected_agent {
            column![
                text(format!("Agent ID: {}", agent.id)),
                text(format!("Position: ({:.2}, {:.2})", agent.x, agent.y)),
                text(format!(
                    "Type: {}",
                    agent.agent_type.as_ref().unwrap_or(&"Unknown".to_string())
                )),
                text(format!("Energy: {:.2}", agent.energy.unwrap_or(0.0))),
                text(format!("Fitness: {:.2}", agent.fitness.unwrap_or(0.0))),
                text(format!("Age: {}", agent.age.unwrap_or(0))),
                text(format!("Alive: {}", agent.alive.unwrap_or(false))),
                text(format!("Speed: {:.2}", agent.move_speed.unwrap_or(0.0))),
                text(format!("Sight: {:.2}", agent.sight.unwrap_or(0.0))),
                if let Some(prey_eaten) = agent.prey_eaten {
                    text(format!("Prey Eaten: {}", prey_eaten))
                } else {
                    text("")
                }
            ]
            .spacing(5)
            .padding(10)
        } else {
            column![text("No agent selected")].spacing(5).padding(10)
        };

        let container = column![self.controls(), agent_info];
        container
    }
    fn controls(&self) -> Row<Message> {
        let controls = row![
            button("Prev Agent")
                .width(Length::FillPortion(1))
                .on_press(Message::PrevAgent),
            button("Next Agent")
                .width(Length::FillPortion(1))
                .on_press(Message::NextAgent),
            button("Best Agent")
                .width(Length::FillPortion(1))
                .on_press(Message::BestAgent),
            button("Connect to simulation")
                .width(Length::FillPortion(1))
                .on_press(Message::SimStart)
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
    pub fn update_sim(&mut self, shapes: &Vec<Shape>, agents: &Vec<Agent>) {
        self.simulation.add_shapes(shapes);
        self.simulation.add_agents(agents)
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
