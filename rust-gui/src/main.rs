use iced::border::width;
use iced::widget::canvas::fill;
use iced::widget::{button, canvas, column, pane_grid, row, text, Column, PaneGrid, Row, Text};
use iced::{mouse, Color, Length, Rectangle, Renderer, Size, Theme};
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
    let _ = iced::run("Test App", View::update, View::view);
}

impl View {
    fn view(&self) -> Row<Message> {
        //SimulationView
        let sim_view = canvas(SimulationView {
            color: Color::from_rgb(1.0, 0.0, 0.0),
        })
        .width(Length::Fill)
        .height(Length::Fill);
        //AgentView
        let agent_view = canvas(AgentView {
            color: Color::from_rgb(1.0, 1.0, 0.0),
        })
        .width(Length::Fill)
        .height(Length::Fill);
        //NNView
        let nn_view = canvas(NNView {
            color: Color::from_rgb(1.0, 1.0, 1.0),
        })
        .width(Length::Fill)
        .height(Length::Fill);

        let agent_nn_col = column!(agent_view, nn_view)
            .width(Length::Fill)
            .height(Length::Fill);

        let container = row!(sim_view, agent_nn_col)
            .width(Length::Fill)
            .height(Length::Fill);

        container
    }
    fn update(&mut self, message: Message) {
        // match message {
        //     Message::IncrementPressed => self.counter += 1,
        //     Message::DecrementPressed => self.counter -= 1,
        // }
    }
}

impl<Message> canvas::Program<Message> for SimulationView {
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
        let rect = canvas::Path::rectangle(frame.center(), frame.size());
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
        let rect = canvas::Path::rectangle(frame.center(), frame.size());
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
        let rect = canvas::Path::rectangle(frame.center(), frame.size());
        frame.fill(&rect, self.color);
        vec![frame.into_geometry()]
    }
}
