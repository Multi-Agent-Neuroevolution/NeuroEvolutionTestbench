#!/usr/bin/env python3
import grpc
from concurrent import futures
import json
import time
import threading
from .generated import comms_pb2
from .generated import comms_pb2_grpc
from messenger import messageChannel


class CommunicationService(comms_pb2_grpc.CommunicationServicer):
    def FetchNeuralNet(slef,request,context):
        print("here")
    def FetchEnvironmentStream(self, request, context):
        while messageChannel.empty == False:
            data = messageChannel.get()
            try:
                json_str = json.dumps(data)
                yield json_transfer_pb2.JsonResponse(
                    json_data=json_str,
                    success=True,
                    message="Data sent successfully"
                )
                time.sleep(1)
            except Exception as e:
                yield json_transfer_pb2.JsonResponse(
                    json_data="",
                    success=False,
                    message=f"Error processing data: {str(e)}"
                )
                time.sleep(1)
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    json_transfer_pb2_grpc.add_JsonTransferServicer_to_server(
        JsonTransferService(), server
    )
    server.add_insecure_port('[::1]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

def main():

    serverThread= threading.Thread(target=serve,daemon=True)
    serverThread.start()

    try:
        # Configuration constants (parameters)
        SIMULATION_TYPE = "PRED_PREY"
        CONFIG_PATH = "./Config/balls.conf"  # Path to your NEAT config file
        STEPS = 1500
        EPOCHS = 20
        BOUNDS = [-200, 200, -200, 200]
        PREY_SPAWN_BOUNDS = [-150, 150, 50, 150]
        PRED_SPAWN_BOUNDS = [-150, 150, -150, -50]
        RATIO = 0.75
        FOODAMOUNT = 100
        FOOD_RESPAWN_RATE = 0.1
        pred_percent = 1 - RATIO

        # Creates simulation environment
        env, population, config, populationSize, pred_pop, prey_pop = create_simulation(
            simulation_type=SIMULATION_TYPE, config_path=CONFIG_PATH, steps=STEPS, bounds=BOUNDS, pred_percent=pred_percent, food_amount=FOODAMOUNT, prey_spawn_bounds=PREY_SPAWN_BOUNDS, pred_spawn_bounds=PRED_SPAWN_BOUNDS, food_respawn_rate=FOOD_RESPAWN_RATE)

        # Create log for the average network size
        logs.log_avg_network_size(env.agents)

        # Run simulation, looping according to the number of epochs specified
        for i in range(EPOCHS):
            env.run()
            mutate(population, config, env, populationSize, pred_pop, prey_pop)
            env.reset()
            print(f"Epoch {i+1} completed")
            logger.info(f"Epoch {i+1} completed")

        # Create logs for genome information
        logs.pickle_genomes(env.agents)
        logs.save_genomes_json(env.agents)
        logs.log_avg_network_size(env.agents)

    # Error-handling for if the user manually stops the simulation or if an error occurs
    except KeyboardInterrupt:
        logger.info("\nSimulation terminated by user")
    except Exception as e:
        logger.info(f"Error during simulation: {str(e)}")
        raise

if __name__ == '__main__':
    logging.basicConfig(filename='./Logs/sim.log', level=logging.INFO)
    logger.info('started')
    main()
