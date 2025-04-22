use std::vec;

//This file wil handle the simulation view, it will be responsible for rendering the simulation and handling user input
use iced::{
    widget::canvas::{self, Fill, Frame, Geometry, Path},
    Color, Point, Rectangle, Renderer, Size,
};
use serde::Deserialize;

use crate::Agent;
#[derive(Deserialize, Clone)]
#[serde(tag = "type")]
pub enum Shape {
    Circle {
        x: f32,
        y: f32,
        radius: f32,
        color: String,
    },
    Rectangle {
        x: f32,
        y: f32,
        width: f32,
        height: f32,
        color: String,
    },
    Triangle {
        x1: f32,
        y1: f32,
        x2: f32,
        y2: f32,
        x3: f32,
        y3: f32,
        color: String,
    },
    Line {
        x1: f32,
        y1: f32,
        x2: f32,
        y2: f32,
        color: String,
    },
}
#[derive(Default, Clone)]
pub struct Simulation {
    shapes: Vec<Shape>,
    agents: Vec<Agent>,
}

impl Simulation {
    pub fn new() -> Self {
        Self {
            shapes: Vec::new(),
            agents: Vec::new(),
        }
    }

    pub fn add_shapes(&mut self, vec: &Vec<Shape>) {
        self.shapes = vec.to_vec();
    }
    pub fn add_agents(&mut self, vec: &Vec<Agent>) {
        self.agents = vec.to_vec();
    }

    pub fn draw(&self, renderer: &Renderer, bounds: Rectangle) -> Vec<canvas::Geometry> {
        let mut geometries = Vec::new();
        for agent in self.agents.iter() {
            let circle = canvas::Path::circle(Point::new(agent.x + 200.0, agent.y + 200.0), 1.0);
            let color = get_color(agent.color.to_string());
            let mut frame = canvas::Frame::new(renderer, bounds.size());
            frame.fill(&circle, color);
            geometries.push(frame.into_geometry());
        }
        for shape in self.shapes.iter() {
            match shape {
                Shape::Circle {
                    x,
                    y,
                    radius,
                    color,
                } => {
                    let circle = canvas::Path::circle(Point::new(*x + 200.0, *y + 200.0), *radius);

                    let color = get_color(color.to_string());
                    let mut frame = canvas::Frame::new(renderer, bounds.size());
                    frame.fill(&circle, color);
                    geometries.push(frame.into_geometry());
                }
                Shape::Rectangle {
                    x,
                    y,
                    width,
                    height,
                    color,
                } => {
                    let rectangle = canvas::Path::rectangle(
                        Point::new(*x + 200.0, *y + 200.0),
                        Size::new(*height, *width),
                    );
                    let color = get_color(color.to_string());
                    let mut frame = canvas::Frame::new(renderer, bounds.size());
                    frame.fill(&rectangle, color);
                    geometries.push(frame.into_geometry());
                }
                Shape::Triangle {
                    x1,
                    y1,
                    x2,
                    y2,
                    x3,
                    y3,
                    color,
                } => {
                    let triangle = canvas::Path::new(|p| {
                        p.move_to(Point::new(*x1 + 200.0, *y1 + 200.0));
                        p.line_to(Point::new(*x2 + 200.0, *y2 + 200.0));
                        p.line_to(Point::new(*x3 + 200.0, *y3 + 200.0));
                        p.close();
                    });
                    let color = get_color(color.to_string());
                    let mut frame = canvas::Frame::new(renderer, bounds.size());
                    frame.fill(&triangle, color);
                    geometries.push(frame.into_geometry());
                }
                Shape::Line {
                    x1,
                    y1,
                    x2,
                    y2,
                    color,
                } => {
                    let line = canvas::Path::line(
                        Point::new(*x1 + 200.0, *y1 + 200.0),
                        Point::new(*x2, *y2),
                    );
                    let color = get_color(color.to_string());
                    let mut frame = canvas::Frame::new(renderer, bounds.size());
                    frame.fill(&line, color);
                    frame.stroke(
                        //Makes the line visible
                        &line,
                        canvas::Stroke::default().with_color(color).with_width(1.0),
                    );
                    geometries.push(frame.into_geometry());
                }
            }
        }
        geometries
    }
}

fn get_color(str: String) -> Color {
    let color = str.as_str();
    match color {
        "red" => Color::from_rgb(1.0, 0.0, 0.0),
        "green" => Color::from_rgb(0.0, 1.0, 0.0),
        "blue" => Color::from_rgb(0.0, 0.0, 1.0),
        "black" => Color::from_rgb(0.0, 0.0, 0.0),
        "white" => Color::from_rgb(1.0, 1.0, 1.0),
        "purple" => Color::from_rgb(0.5, 0.0, 0.5),
        "yellow" => Color::from_rgb(0.0, 1.0, 1.0),
        _ => Color::from_rgb(0.0, 0.0, 0.0),
    }
}
