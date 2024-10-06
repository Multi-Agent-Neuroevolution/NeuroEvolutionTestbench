use iced::widget::{button, column, text, Column, Text};

#[derive(Default, Clone, Copy)]
struct Counter {
    counter: i32,
}

#[derive(Debug, Clone, Copy)]
enum Message {
    IncrementPressed,
    DecrementPressed,
}

fn main() {
    let counter = Counter { counter: 0 };
    iced::run("Test App", Counter::update, Counter::view);
}

impl Counter {
    fn view(&self) -> Column<Message> {
        let increment_button = button("+").on_press(Message::IncrementPressed);
        let decrement_button = button("-").on_press(Message::DecrementPressed);
        let counter_value: Text = text(self.counter.to_string());
        let view = column!(increment_button, counter_value, decrement_button,);
        view
    }
    fn update(&mut self, message: Message) {
        match message {
            Message::IncrementPressed => self.counter += 1,
            Message::DecrementPressed => self.counter -= 1,
        }
    }
}
