#!/usr/bin/env python3
import neat
import multiprocessing
import grpc
from concurrent import futures
import json
import time
import threading
import constants
import logging
import logs
from environment import Environment
from agents import Predator, Prey
from evolution_utils import breed_and_mutate
from .generated import json_transfer_pb2, json_transfer_pb2_grpc
from messenger import messageChannel

# Initialize logger
logger = logging.getLogger(__name__)

class JsonTransferService(json_transfer_pb2_grpc.JsonTransferServicer):
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
    json_transfer_pb2_grpc.add_JsonTransferServicer_to_server(JsonTransferService(), server)
    server.add_insecure_port('[::1]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

def create_simulation(simulation_type="PRED_PREY", config_path=None, steps=1000, bounds=[-200, 200, -200, 200], pred_percent=0.25, food_amount=10, prey_spawn_bounds=[50, 150, 50, 150], pred_spawn_bounds=[-150, -50, -150, -50], food_respawn_rate=0.1):
    # Create the environment with optimal number of workers
    num_cores = multiprocessing.cpu_count()
    env = Environment(simulation_type, steps, bounds, food_respawn_rate)
    env.max_workers = max(1, num_cores - 1)

    # Variables to be sent to the environment initialization function
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    population = neat.Population(config)
    pred_pop = int(len(population.population.items())*pred_percent)
    print(pred_pop)
    print(len(population.population.items()))
    prey_pop = len(population.population.items()) - pred_pop
    env.initialize_environment(
        config=config,
        population=population,
        pred_pop=pred_pop,
        prey_pop=prey_pop,
        pred_spawn_bounds=pred_spawn_bounds,
        prey_spawn_bounds=prey_spawn_bounds,
        food_amount=food_amount
    )

    # Update logger with simulation start info and max CPU cores being used
    logger.info(f"Starting simulation with {config.pop_size} agents...")
    logger.info(
        f"Using {env.max_workers} Logical CPU cores for parallel processing")

    return env, population, config, len(population.population.items()), pred_pop, prey_pop

def mutate(genome, config, env, population_size, pred_pop, prey_pop):
    # Create separate lists for predators and prey
    predators = [agent for agent in env.agents if isinstance(agent, Predator)]
    preys = [agent for agent in env.agents if isinstance(agent, Prey)]

    for agent in predators + preys:
        if agent.neat_genome:
            # scale the fitness of the agent using like tanh (0-100)
            # agent.fitness = np.tanh(agent.fitness) * 100
            # Sync agent fitness with genome fitness
            agent.neat_genome.fitness = agent.fitness

    # Save the average fitness of both predator and prey populations to a CSV file
    logs.avg_agent_fitness(predators, preys)

    # Sort and retain the top 10% based on fitness
    top_predators = sorted(predators, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(predators) * 0.1))]
    top_preys = sorted(preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(len(preys) * 0.1))]

    # Number of offspring to create for predators and prey
    num_pred_offspring = int(pred_pop - len(top_predators))
    num_prey_offspring = int(prey_pop - len(top_preys))

    # Breed and mutate predators and prey
    new_predators = breed_and_mutate(
        config, top_predators, is_predator=True, num_offspring=num_pred_offspring, pred_bounds=constants.PRED_SPAWN_BOUNDS, prey_bounds=constants.PREY_SPAWN_BOUNDS)
    new_preys = breed_and_mutate(
        config, top_preys, is_predator=False, num_offspring=num_prey_offspring, pred_bounds=constants.PRED_SPAWN_BOUNDS, prey_bounds=constants.PREY_SPAWN_BOUNDS)

    # Replace the old population with the new one
    env.add_agents(top_predators + top_preys + new_predators + new_preys)

def main():

    serverThread= threading.Thread(target=serve,daemon=True)
    serverThread.start()

    try:
        # scale bounds
        constants.BOUNDS = [
            bound * constants.SCALE_FACTOR for bound in constants.BOUNDS]
        constants.PREY_SPAWN_BOUNDS = [
            bound * constants.SCALE_FACTOR for bound in constants.PREY_SPAWN_BOUNDS]
        constants.PRED_SPAWN_BOUNDS = [
            bound * constants.SCALE_FACTOR for bound in constants.PRED_SPAWN_BOUNDS
        ]

        # Creates simulation environment
        env, population, config, populationSize, pred_pop, prey_pop = create_simulation(
            simulation_type=constants.SIMULATION_TYPE,
            config_path=constants.CONFIG_PATH,
            steps=constants.STEPS,
            bounds=constants.BOUNDS,
            pred_percent=constants.PRED_PERCENT,
            food_amount=constants.FOOD_AMOUNT,
            prey_spawn_bounds=constants.PREY_SPAWN_BOUNDS,
            pred_spawn_bounds=constants.PRED_SPAWN_BOUNDS,
            food_respawn_rate=constants.FOOD_RESPAWN_RATE
        )

        # Create log for the average network size
        logs.log_avg_network_size(env.agents)

        # Run simulation, looping according to the number of epochs specified
        for i in range(constants.EPOCHS):
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
