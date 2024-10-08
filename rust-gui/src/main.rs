use iced::border::width;
use iced::widget::canvas::{Canvas, Fill, Frame, Path};
use iced::widget::{button, canvas, column, pane_grid, row, text, Column, PaneGrid, Row, Text};
use iced::{mouse, Color, Length, Point, Rectangle, Renderer, Size, Theme};
#[derive(Default, Clone, Copy)]
struct View {
    counter: i32,
}
struct SimulationView {
    color: Color,
}
struct AgentView {
    color: Color,
}
struct NNView {
    color: Color,
}

#[derive(Debug, Clone, Copy)]
enum Message {
    IncrementPressed,
    DecrementPressed,
}

fn main() {
    let _ = iced::run(
        "Multi-agent Neuroevolution Simulator",
        View::update,
        View::view,
    );
}

impl View {
    fn view(&self) -> Column<Message> {
        //Top Controls
        let top_controls = row![button("File"), button("Edit"), button("View")].spacing(10);

        //SimulationView
        let sim_view = canvas(SimulationView {
            color: Color::from_rgb(1.0, 0.0, 0.0),
        })
        .width(Length::FillPortion(3))
        .height(Length::Fill);
        //AgentView
        let agent_view = canvas(AgentView {
            color: Color::from_rgb(0.0, 1.0, 0.0),
        })
        .width(Length::Fill)
        .height(Length::Fill);
        //NNView
        let nn_view = canvas(NNView {
            color: Color::from_rgb(0.0, 0.0, 1.0),
        })
        .width(Length::Fill)
        .height(Length::Fill);

        let agent_nn_col = column!(agent_view, nn_view)
            .width(Length::FillPortion(1))
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
