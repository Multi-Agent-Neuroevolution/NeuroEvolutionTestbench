use tonic::{Request, Status};
use comms::communication_client::CommunicationClient;
use comms::Command;
use comms::JsonData;
use tokio::mpsc::Sender;
use tonic::transport::Channel;
pub mod comms {
    tonic::include_proto!("comms");
}

//@TODO change the return type to the correct return type
/*async fn startSim() ->Result<(),Box<dyn std::error::Error>>{
    let mut client = CommunicationClient::connect("http://[::1]:50051").await?;
    let request = Request::new(Command{
       r#in:"start".into(),
    });
    let mut stream = client.FetchEnvironmentStream(request).await?.into_inner();
    Ok(())
}*/

async fn getSimStream(connection:Channel,sender:Sender){
    let request = Request::new(Command{
       r#in:"start".into(),
    });
    let mut stream = connection.FetchEnvironmentStream(request).await.unwrap().into_inner();



}

async fn getNeuralNet(connection:Channel,sender:Sender,agent:i32){

    let netString = connection.FetchNeuralNet().await.unwrap().into_inner();

}
