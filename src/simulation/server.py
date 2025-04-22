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
from messenger import messageChannel
import comms_pb2
import comms_pb2_grpc
from collections import defaultdict

# Initialize logger
logger = logging.getLogger(__name__)

class CommunicationService(comms_pb2_grpc.CommunicationServicer):
    """This class implements the gRPC service for communication.
    
    Args:
        comms_pb2_grpc.CommunicationServicer: The gRPC service class.
    """
    def FetchEnvironmentStream(self, request, context):
        """Pulls data from the message channel and sends it to the client as JSON data.
        
        Args:
            request: The request object from the client.
            context: The gRPC context object.
    
        Yields:
            comms_pb2.JSONData: The JSON data to be sent to the client.
        """
        while messageChannel.empty() == False:
            data = messageChannel.get()

            try:
                print("trying json")
                json_str = json.dumps(data)
                print(f"{json_str}")
                yield comms_pb2.JSONData(json_data=json_str, success=True,
                                         message="Data sent successfully")
            except Exception as e:
                yield comms_pb2.JSONData(json_data="", success=False,
                                        message=f"Error processing data: {str(e)}")
                
            time.sleep(1)   # I moved this outside of the try-except since it seemed like it would always run anyway

class Simulation:
    def __init__(self, simulation_type="PRED_PREY", steps=200, bounds=[-200, 200, -200, 200], multi_model=False, food_amount=None, food_respawn_rate=None):
        self.simulation_type = simulation_type
        self.steps = steps
        self.bounds = bounds
        self.multi_model = multi_model
        self.food_amount = food_amount
        self.food_respawn_rate = food_respawn_rate
        self.config_path = constants.CONFIG_PATH
        self.environment = None
        self.pred_percent = None
    
    def _generate_configs(self, configs):
        """Generates NEAT configurations for each config-type specified prior
        
        Args:
            configs (dict): A dictionary of config names and their corresponding NEAT configurations.

        Returns:
            dict: A dictionary of NEAT configurations for each config-type.
        """
        for config in configs:
            configs[config] = neat.Config(
                neat.DefaultGenome,
                neat.DefaultReproduction,
                neat.DefaultSpeciesSet,
                neat.DefaultStagnation,
                self.config_path
            )

            if self.multi_model and "std" in config:
                configs[config].genome_config.__dict__['conn_add_prob'] = 0
                configs[config].genome_config.__dict__['conn_delete_prob'] = 0
                configs[config].genome_config.__dict__['node_add_prob'] = 0
                configs[config].genome_config.__dict__['node_delete_prob'] = 0
        
        return configs
    
    def _generate_populations(self, population):
        """Generates populations of agents based on the specified simulation type.
        
        Args:
            population (neat.Population): The NEAT population object.
            
        Returns:
            dict: A dictionary containing the populations of predators and prey.
        """
        if self.simulation_type == "PRED_PREY":
            agent_populations = {"pred_pop_neat": [], "prey_pop_neat": []}
            for agent in population.population.items():
                if len(agent_populations["pred_pop_neat"]) < int(len(population.population.items()) * self.pred_percent):
                    agent_populations["pred_pop_neat"].append(agent)
                else:
                    agent_populations["prey_pop_neat"].append(agent)
            
            # Print number of entries in agent_populatoins
            print(f"INFO:\tSize of population: {sum(len(population) for population in agent_populations.values())}")

        return agent_populations
    
    # 
    def _mutate(self):
        if self.simulation_type == "PRED_PREY":
            agent_groups = defaultdict(list)

            for agent in self.environment.agents:
                pop_key = (agent.__class__.__name__, agent.type)
                agent_groups[pop_key].append(agent)
            print(agent_groups)

            top_agents = {}
            new_agents = {}
            for key, agents in agent_groups.items():
                if key[0] == "Predator":
                    bounds = constants.PRED_SPAWN_BOUNDS
                elif key[0] == "Prey":
                    bounds = constants.PREY_SPAWN_BOUNDS
                
                if self.multi_model:
                    multi_model = True
                else:
                    multi_model = False
                top_agents[key] = sorted(agents, key=lambda x: x.fitness, reverse=True)[:max(1, int(len(agents) * constants.CUT_OFF))]
                num_offspring = int(len(agents) - len(top_agents[key]))
                new_agents[key] = breed_and_mutate(self.environment.configs[key[0]], top_agents[key], num_offspring=num_offspring, multi_model=multi_model, bounds=bounds)

            self.environment.add_agents(top_agents + new_agents)
            # predators_neat = [agent for agent in self.environment.agents if isinstance(agent, Predator) and agent.type == 1]
            # preys_neat = [agent for agent in self.environment.agents if isinstance(agent, Prey) and agent.type == 1]
            # predators_std = [agent for agent in self.environment.agents if isinstance(agent, Predator) and agent.type == 0]
            # preys_std = [agent for agent in self.environment.agents if isinstance(agent, Prey) and agent.type == 0]
            
            # logs.avg_agent_fitness(predators_neat, preys_neat, predators_std, preys_std)
            # for agent in self.environment.agents:
            #     if agent.neat_genome:
            #         agent.neat_genome.fitness = agent.fitness
            # logs.avg_agent_fitness(predators_neat, preys_neat, predators_std, preys_std)

            # top_predators_neat = sorted(predators_neat, key=lambda x: x.fitness, reverse=True)[:max(1, int(self.environment.pred_pop * constants.CUT_OFF))]
            # top_preys_neat = sorted(preys_neat, key=lambda x: x.fitness, reverse=True)[:max(1, int(self.environment.prey_pop * constants.CUT_OFF))]
            # top_predators_std = sorted(predators_std, key=lambda x: x.fitness, reverse=True)[:max(1, int(self.environment.pred_pop_no_neat * constants.CUT_OFF))]
            # top_preys_std = sorted(preys_std, key=lambda x: x.fitness, reverse=True)[:max(1, int(self.environment.prey_pop_no_neat * constants.CUT_OFF))]

            # num_offspring_predators_neat = int(self.environment.pred_pop - len(top_predators_neat))
            # num_offspring_preys_neat = int(self.environment.prey_pop - len(top_preys_neat))
            # num_offspring_predators_std = int(self.environment.pred_pop_no_neat - len(top_predators_std))
            # num_offspring_preys_std = int(self.environment.prey_pop_no_neat - len(top_preys_std))

            # new_predators_neat = breed_and_mutate(self.environment.configs["pred_neat"], top_predators_neat, num_offspring=num_offspring_predators_neat, multi_model=False, bounds=constants.PRED_SPAWN_BOUNDS)
            # new_preys_neat = breed_and_mutate(self.environment.configs["prey_neat"], top_preys_neat, num_offspring=num_offspring_preys_neat, multi_model=False, bounds=constants.PREY_SPAWN_BOUNDS)
            # if self.multi_model:
            #     new_predators_std = breed_and_mutate(self.environment.configs["pred_std"], top_predators_std, num_offspring=num_offspring_predators_std, multi_model=True, bounds=constants.PRED_SPAWN_BOUNDS)
            #     new_preys_std = breed_and_mutate(self.environment.configs["prey_std"], top_preys_std, num_offspring=num_offspring_preys_std, multi_model=True, bounds=constants.PREY_SPAWN_BOUNDS)

            # Replace the old population with the new one
            # Rework to use top_agents and new_agents dictionaries
            # self.environment.add_agents(top_predators_neat + top_preys_neat + new_predators_neat + new_preys_neat + new_predators_std + new_preys_std + top_predators_std + top_preys_std)

    def create_simulation(self):
        num_cores = multiprocessing.cpu_count()

        if self.simulation_type == "PRED_PREY":
            self.pred_percent = constants.PRED_PERCENT
            self.food_amount = constants.FOOD_AMOUNT
            self.food_respawn_rate = constants.FOOD_RESPAWN_RATE

            self.environment = Environment(self.simulation_type, self.steps, self.bounds, self.food_respawn_rate)
            self.environment.max_workers = max(1, num_cores - 1)
            print(f"INFO:\tUsing {self.environment.max_workers} workers for parallel processing.")
            
            # First, generate configs
            print("START:\tCreating NEAT config...")
            configs = {
                "generic": None,
                "pred_std": None,
                "pred_neat": None,
                "pred_hypr": None,
                "prey_std": None,
                "prey_neat": None,
                "prey_hypr": None
            }
            configs = self._generate_configs(configs)
            print("END:\tCreated configs.")

            # Next, generate agent populations
            print("START:\tCreating agent populations...")
            population = neat.Population(configs["generic"])
            agent_populations = self._generate_populations(population)
            print("END:\tCreated agent populations.")

            print("START:\tInitializing environment...")
            print(" length of agent_populations: ", sum(len(population ) for population in agent_populations.values()))
            self.environment.initialize_environment(
                config=configs,
                simulation_type=self.simulation_type,
                population=population,
                agent_populations=agent_populations,
                pred_spawn_bounds=constants.PRED_SPAWN_BOUNDS,
                prey_spawn_bounds=constants.PREY_SPAWN_BOUNDS,
                food_amount=self.food_amount,
                multi_model=self.multi_model
            )
            print("END:\tEnvironment initialized.")

            print("INFO:\tStarting Logger...")
            logger.info(f"Starting simulation with {configs['generic'].pop_size} agents...")
            logger.info(f"Using {self.environment.max_workers} Logical CPU cores for parallel processing.")

    def run_simulation(self):
        for i in range(constants.EPOCHS):
            start_time = time.time()
            print(self.environment.agents)
            self.environment.run()
            if i > constants.EPOCHS / 2 and constants.SWAP_BOUNDS:
                self._mutate()
            else:
                self._mutate()
            self.environment.reset()
            end_time = time.time()
            _update_progress_bar(i, start_time, end_time)
        

def serve():
    """Starts the gRPC server and adds the CommunicationService to it."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    comms_pb2_grpc.add_CommunicationServicer_to_server(CommunicationService(), server)
    
    server.add_insecure_port('[::1]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()


def mutate(genome, configList, env, population_size, pred_pop, prey_pop, pred_pop_no_neat, prey_pop_no_neat, pred_spawn_bounds,  prey_spawn_bounds, eliteism=0.1, crossover_rate=0.7, torunament_size=3):
    # Create separate lists for predators and prey
    predators = [agent for agent in env.agents if isinstance(
        agent, Predator) and agent.type == 1]
    preys = [agent for agent in env.agents if isinstance(
        agent, Prey) and agent.type == 1]
    no_neat_predators = [agent for agent in env.agents if isinstance(
        agent, Predator) and agent.type == 0]
    no_neat_preys = [agent for agent in env.agents if isinstance(
        agent, Prey) and agent.type == 0]
    logs.avg_agent_fitness(predators, preys, no_neat_predators, no_neat_preys)
    for agent in env.agents:
        if agent.neat_genome:
            agent.neat_genome.fitness = agent.fitness

    # Save the average fitness of both predator and prey populations to a CSV file
    logs.avg_agent_fitness(predators, preys, no_neat_predators, no_neat_preys)

    # Sort and retain the top 10% based on fitness
    top_predators = sorted(predators, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(pred_pop * eliteism))]
    top_preys = sorted(preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(prey_pop * eliteism))]
    top_predators_no_neat = sorted(no_neat_predators, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(pred_pop_no_neat * eliteism))]
    top_preys_no_neat = sorted(no_neat_preys, key=lambda x: x.fitness, reverse=True)[
        :max(1, int(prey_pop_no_neat * eliteism))]

    # Number of offspring to create for predators and prey
    num_pred_offspring = int(pred_pop - len(top_predators))
    num_prey_offspring = int(prey_pop - len(top_preys))
    num_pred_offspring_no_neat = int(pred_pop_no_neat - len(top_predators_no_neat))
    num_prey_offspring_no_neat = int(prey_pop_no_neat - len(top_preys_no_neat))

    # Breed and mutate predators and prey
    new_predators = breed_and_mutate(configList[2], top_predators, num_offspring=num_pred_offspring, multi_model=False,
                                     bounds=pred_spawn_bounds, crossover_rate=crossover_rate, torunament_size=torunament_size)
    new_preys = breed_and_mutate(configList[5], top_preys,  num_offspring=num_prey_offspring, multi_model=False,
                                 bounds=prey_spawn_bounds, crossover_rate=crossover_rate, torunament_size=torunament_size)

    if prey_pop_no_neat > 0 and pred_pop_no_neat > 0:
        new_no_neat_preys = breed_and_mutate(configList[4], top_preys_no_neat,  num_offspring=num_prey_offspring_no_neat, multi_model=True,
                                             bounds=prey_spawn_bounds, crossover_rate=crossover_rate, torunament_size=torunament_size)
        new_no_neat_preds = breed_and_mutate(configList[1], top_predators_no_neat, num_offspring=num_pred_offspring_no_neat, multi_model=True,
                                             bounds=pred_spawn_bounds, crossover_rate=crossover_rate, torunament_size=torunament_size)

    # Replace the old population with the new one
    env.add_agents(top_predators + top_preys + new_predators + new_preys +
                   new_no_neat_preys + new_no_neat_preds + top_predators_no_neat + top_preys_no_neat)

def _update_progress_bar(i, start_time, end_time):
    epoch_duration = end_time - start_time
    remaining_epochs = constants.EPOCHS - (i + 1)
    estimated_time_remaining = remaining_epochs * epoch_duration
    estimated_time_remaining_hours = estimated_time_remaining / 3600
    epoch_duration_hours = epoch_duration / 3600

    # Print statements to show the progress bar while epochs complete
    print(f"Epoch {i+1} completed, {constants.EPOCHS - i - 1} epochs remaining")
    print(f"Estimated time remaining: {estimated_time_remaining_hours:.2f} hours")
    logger.info(f"Epoch {i+1} completed in {epoch_duration_hours:.2f} hours")
    logger.info(f"Estimated time remaining: {estimated_time_remaining_hours:.2f} hours")

# def main():
#     # Start the gRPC server in a separate thread
#     serverThread = threading.Thread(target=serve, daemon=True)
#     serverThread.start()

#     try:
#         # scale bounds
#         constants.BOUNDS = [bound * constants.SCALE_FACTOR
#                             for bound in constants.BOUNDS]
#         constants.PREY_SPAWN_BOUNDS = [bound * constants.SCALE_FACTOR
#                                        for bound in constants.PREY_SPAWN_BOUNDS]
#         constants.PRED_SPAWN_BOUNDS = [bound * constants.SCALE_FACTOR
#                                        for bound in constants.PRED_SPAWN_BOUNDS]

#         # Creates simulation environment
#         print("START:\tCreating simulation environment...")
#         env, population, configList, populationSize, pred_pop, prey_pop, pred_pop_no_neat, prey_pop_no_neat = create_simulation(
#             simulation_type=constants.SIMULATION_TYPE,
#             config_path=constants.CONFIG_PATH,
#             steps=constants.STEPS,
#             bounds=constants.BOUNDS,
#             pred_percent=constants.PRED_PERCENT,
#             food_amount=constants.FOOD_AMOUNT,
#             prey_spawn_bounds=constants.PREY_SPAWN_BOUNDS,
#             pred_spawn_bounds=constants.PRED_SPAWN_BOUNDS,
#             food_respawn_rate=constants.FOOD_RESPAWN_RATE,
#             multi_model=constants.MULTI_MODEL,
#             model_split=constants.MODEL_SPLIT
#         )
#         print("END:\tSimulation environment created")

#         # Create log for the average network size
#         logs.log_avg_network_size(env.agents)

#         # Run simulation, looping according to the number of epochs specified
#         eliteism = constants.CUT_OFF  # Percentage of agents that will be used for breeding
#         crossover_rate = constants.CROSS_OVER_RATE  # Crossover rate for breeding
#         torunament_size = constants.TOURNAMENT_SIZE  # Tournament size for selection
#         prey_spawn_bounds = constants.PREY_SPAWN_BOUNDS  # Spawn bounds for prey
#         pred_spawn_bounds = constants.PRED_SPAWN_BOUNDS  # Spawn bounds for predators
#         logs.save_initial_genomes_json(env.agents)
#         for i in range(constants.EPOCHS):
#             start_time = time.time()  # Start timing the epoch
#             env.run()
#             if i > constants.EPOCHS / 2 and constants.SWAP_BOUNDS:
#                 mutate(population, configList, env, populationSize, pred_pop,
#                        prey_pop, pred_pop_no_neat, prey_pop_no_neat,
#                        prey_spawn_bounds, pred_spawn_bounds,
#                        eliteism, crossover_rate=crossover_rate,
#                        torunament_size=torunament_size)
#             else:
#                 mutate(population, configList, env, populationSize, pred_pop,
#                        prey_pop, pred_pop_no_neat, prey_pop_no_neat,
#                        pred_spawn_bounds, prey_spawn_bounds,
#                        eliteism, crossover_rate=crossover_rate,
#                        torunament_size=torunament_size)
#             env.reset()
#             end_time = time.time()  # End timing the epoch
#             _update_progress_bar(i, start_time, end_time)

#         # Create logs for genome information
#         logs.pickle_genomes(env.agents)
#         logs.save_genomes_json(env.agents)
#         logs.log_avg_network_size(env.agents)

#     # Error-handling for if the user manually stops the simulation or if an error occurs
#     except KeyboardInterrupt:
#         logger.info("\nSimulation terminated by user")
#     except Exception as e:
#         logger.info(f"Error during simulation: {str(e)}")
#         raise

def main2():
    # Start the gRPC server in a separate thread
    serverThread = threading.Thread(target=serve, daemon=True)
    serverThread.start()

    try:
        sim = Simulation()
        sim.create_simulation()
        logs.log_avg_network_size(sim.environment.agents)
        logs.save_initial_genomes_json(sim.environment.agents)

        sim.run_simulation()

        # Create logs for genome information
        logs.pickle_genomes(sim.environment.agents)
        logs.save_genomes_json(sim.environment.agents)
        logs.log_avg_network_size(sim.environment.agents)

    except KeyboardInterrupt:
        logger.info("\nSimulation terminated by user")
    except Exception as e:
        logger.info(f"Error during simulation: {str(e)}")
        raise

if __name__ == "__main__":
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

    # Setup handlers for different log files
    info_handler = logging.FileHandler('./Logs/sim.log', mode='w')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Set to lowest level you want to capture
    root_logger.addHandler(info_handler)

    main2()