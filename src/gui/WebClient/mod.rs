use tonic::{Request, Status};
use comms::comns_client::NeuroEvolutionClient;
use comms::Command;


pub mod json_transfer {
    tonic::include_proto!("comms");
}

//@TODO change the return type to the correct return type
async fn startSim() ->Result<(),Box<dyn std::error::Error>>{
    let mut client = NeuroEvolutionClient::connect("http://[::1]:50051").await?;
    let request = Request::new(Command{
       In:"start",
    });
    let mut stream = client.FetchEnvironmentStream(request).await?.into_inner();
    ()
}
