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
        // 1) Compute world‐space min/max (same as before)…
        let mut min_x = f32::INFINITY;
        let mut max_x = f32::NEG_INFINITY;
        let mut min_y = f32::INFINITY;
        let mut max_y = f32::NEG_INFINITY;

        for agent in &self.agents {
            min_x = min_x.min(agent.x);
            max_x = max_x.max(agent.x);
            min_y = min_y.min(agent.y);
            max_y = max_y.max(agent.y);
        }

        for shape in &self.shapes {
            match shape {
                Shape::Circle { x, y, radius, .. } => {
                    min_x = min_x.min(x - radius);
                    max_x = max_x.max(x + radius);
                    min_y = min_y.min(y - radius);
                    max_y = max_y.max(y + radius);
                }
                Shape::Rectangle {
                    x,
                    y,
                    width,
                    height,
                    ..
                } => {
                    min_x = min_x.min(*x);
                    max_x = max_x.max(x + width);
                    min_y = min_y.min(*y);
                    max_y = max_y.max(y + height);
                }
                Shape::Triangle {
                    x1,
                    y1,
                    x2,
                    y2,
                    x3,
                    y3,
                    ..
                } => {
                    for &(xx, yy) in &[(*x1, *y1), (*x2, *y2), (*x3, *y3)] {
                        min_x = min_x.min(xx);
                        max_x = max_x.max(xx);
                        min_y = min_y.min(yy);
                        max_y = max_y.max(yy);
                    }
                }
                Shape::Line { x1, y1, x2, y2, .. } => {
                    min_x = min_x.min(*x1).min(*x2);
                    max_x = max_x.max(*x1).max(*x2);
                    min_y = min_y.min(*y1).min(*y2);
                    max_y = max_y.max(*y1).max(*y2);
                }
            }
        }

        let world_w = (max_x - min_x).max(1.0);
        let world_h = (max_y - min_y).max(1.0);

        // 2) Use fields, not methods:
        let sx = bounds.width / world_w;
        let sy = bounds.height / world_h;
        let scale = sx.min(sy);

        let extra_x = (bounds.width - world_w * scale) / 2.0;
        let extra_y = (bounds.height - world_h * scale) / 2.0;

        let world_to_canvas = |wx: f32, wy: f32| {
            let cx = (wx - min_x) * scale + extra_x;
            let cy = (wy - min_y) * scale + extra_y;
            Point::new(cx, cy)
        };

        // 3) Draw
        let mut geometries = Vec::new();

        // draw agents with a fixed radius
        for agent in &self.agents {
            let center = world_to_canvas(agent.x, agent.y);
            let r = 1.0 * scale; // or whatever base radius you want
            let circle = Path::circle(center, r);
            let mut frame = Frame::new(renderer, Size::new(bounds.width, bounds.height));
            frame.fill(&circle, get_color(agent.color.clone()));
            geometries.push(frame.into_geometry());
        }

        // draw shapes (same as before, but use fields and scale)
        for shape in &self.shapes {
            let mut frame = Frame::new(renderer, Size::new(bounds.width, bounds.height));
            match shape {
                Shape::Circle {
                    x,
                    y,
                    radius,
                    color,
                } => {
                    let c = world_to_canvas(*x, *y);
                    let circle = Path::circle(c, radius * scale);
                    frame.fill(&circle, get_color(color.clone()));
                }
                Shape::Rectangle {
                    x,
                    y,
                    width,
                    height,
                    color,
                } => {
                    let origin = world_to_canvas(*x, *y);
                    let rect = Path::rectangle(origin, Size::new(width * scale, height * scale));
                    frame.fill(&rect, get_color(color.clone()));
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
                    let tri = Path::new(|p| {
                        p.move_to(world_to_canvas(*x1, *y1));
                        p.line_to(world_to_canvas(*x2, *y2));
                        p.line_to(world_to_canvas(*x3, *y3));
                        p.close();
                    });
                    frame.fill(&tri, get_color(color.clone()));
                }
                Shape::Line {
                    x1,
                    y1,
                    x2,
                    y2,
                    color,
                } => {
                    let line = Path::line(world_to_canvas(*x1, *y1), world_to_canvas(*x2, *y2));
                    frame.stroke(
                        &line,
                        canvas::Stroke::default()
                            .with_color(get_color(color.clone()))
                            .with_width(1.0),
                    );
                }
            }
            geometries.push(frame.into_geometry());
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
