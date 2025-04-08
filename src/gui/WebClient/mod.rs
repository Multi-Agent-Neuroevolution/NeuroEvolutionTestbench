use iced::futures::StreamExt;
use tonic::{Request, Status};
use comms::communication_client::CommunicationClient;
use comms::Command;
use comms::JsonData;
use comms::Id;
use tokio::sync::mpsc::Sender;
use tonic::transport::Channel;
pub mod comms {
    tonic::include_proto!("comms");
}
pub async fn getConnection()->Result<CommunicationClient<Channel>,tonic::transport::Error>{
    let client = CommunicationClient::connect("http://[::1]:50051").await?;
    println!("Successful connection");
    Ok(client)
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

pub async fn getSimStream(mut connection:CommunicationClient<Channel>,sender:Sender<JsonData>)->Result<(),Box<dyn std::error::Error>>{
    let request = Request::new(Command{
       r#in:"start".into(),
    });
    println!("fetching stream");
    let mut stream = connection.fetch_environment_stream(request).await.unwrap().into_inner();
    println!("stream fetched");
    while let Some(data) = stream.next().await{
        println!("got data");
        let data = data?;
        sender.send(data).await?;
    }
    Ok(())
}

pub async fn getNeuralNet(connection:&mut CommunicationClient<Channel>,agent:i32)->JsonData{
    let request = Request::new(Id{r#id:agent,});
    let netString = connection.fetch_neural_net(request).await.unwrap().into_inner();
    netString
}
