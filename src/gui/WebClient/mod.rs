// src/main.rs
use tonic::{Request, Status};
use comms::comns_client::NeuroEvolutionClient;
use comms::Command;


pub mod json_transfer {
    tonic::include_proto!("comms");
}

async fn startSim() ->Result<(),Box<dyn std::error::Error>>{
    let mut client = NeuroEvolutionClient::connect("http://[::1]:50051").await?;

    ()

}
