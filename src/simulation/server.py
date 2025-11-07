#!/usr/bin/env python3
import math
import random
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
from hyperneat import generate_hyperneat_offspring, create_schema_from_inputs_outputs
# from .generated import comms_pb2, comms_pb2_grpc
from messenger import messageChannel
import comms_pb2
import comms_pb2_grpc
from utils import FitnessHelper, build_configs
import copy
# Initialize logger
logger = logging.getLogger(__name__)


class CommunicationService(comms_pb2_grpc.CommunicationServicer):
    def __init__(self):
        self.current_env = None

    def set_environment(self, env):
        """Set the current environment to access agents"""
        self.current_env = env

    def FetchEnvironmentStream(self, request, context):
        for data in iter(messageChannel.get, None):
            json_str = json.dumps(data)
            yield comms_pb2.JSONData(
                json_data=json_str,
                success=True,
                message="Data sent successfully"
            )

    def FetchNeuralNet(self, request, context):
        """Fetch neural network data for a specific agent"""
        agent_id = request.id
        try:
            if self.current_env is None:
                return comms_pb2.JSONData(
                    json_data="{}",
                    success=False,
                    message="No environment available"
                )

            # Find agent by ID
            agent = None
            for a in self.current_env.agents:
                if a.id == agent_id:
                    agent = a
                    break

            if agent is None:
                return comms_pb2.JSONData(
                    json_data="{}",
                    success=False,
                    message=f"Agent with ID {agent_id} not found"
                )

            # Extract neural network structure
            if agent.brain is None:
                return comms_pb2.JSONData(
                    json_data="{}",
                    success=False,
                    message="Agent has no neural network"
                )

            # Get network structure from NEAT genome
            network_data = self._extract_network_structure(agent)

            return comms_pb2.JSONData(
                json_data=json.dumps(network_data),
                success=True,
                message="Neural network data retrieved successfully"
            )

        except Exception as e:
            return comms_pb2.JSONData(
                json_data="{}",
                success=False,
                message=f"Error fetching neural network: {str(e)}"
            )

    def _extract_network_structure(self, agent):
        """Extract neural network structure from NEAT agent"""
        try:
            genome = agent.neat_genome
            config = agent.neat_config

            # Get nodes and connections from genome
            nodes = {}
            for node_id, node in genome.nodes.items():
                nodes[str(node_id)] = {
                    "id": int(node_id),
                    "bias": float(node.bias),
                    "activation": str(node.activation),
                    "type": self._get_node_type(node_id, config)
                }

            connections = []
            for conn_key, conn in genome.connections.items():
                if conn.enabled:
                    connections.append({
                        "from": int(conn_key[0]),
                        "to": int(conn_key[1]),
                        "weight": float(conn.weight),
                        "enabled": bool(conn.enabled)
                    })

            # Organize into layers
            layers = self._organize_into_layers(nodes, connections, config)

            return {
                "agent_id": int(agent.id),
                "nodes": nodes,
                "connections": connections,
                "layers": layers,
                "fitness": float(agent.fitness),
                "age": int(agent.age)
            }

        except Exception as e:
            logger.error(f"Error extracting network structure: {str(e)}")
            return {}

    def _get_node_type(self, node_id, config):
        """Determine node type based on NEAT conventions"""
        if node_id < 0:
            return "input"
        elif node_id < config.genome_config.num_outputs:
            return "output"
        else:
            return "hidden"

    def _organize_into_layers(self, nodes, connections, config):
        """Organize nodes into layers for visualization"""
        layers = {
            "input": [],
            "hidden": [],
            "output": []
        }

        for node_id, node_data in nodes.items():
            node_type = node_data["type"]
            layers[node_type].append({
                "id": int(node_id),
                "value": node_data.get("bias", 0.0),
                "weights": self._get_outgoing_weights(int(node_id), connections)
            })

        return [
            {"nodes": layers["input"]},
            {"nodes": layers["hidden"]},
            {"nodes": layers["output"]}
        ]

    def _get_outgoing_weights(self, node_id, connections):
        """Get all outgoing connection weights for a node"""
        weights = []
        for conn in connections:
            if conn["from"] == node_id:
                weights.append(conn["weight"])
        return weights


def serve(env=None):
    communication_service = CommunicationService()
    if env:
        communication_service.set_environment(env)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    comms_pb2_grpc.add_CommunicationServicer_to_server(
        communication_service, server)
    server.add_insecure_port('[::1]:50051')
    server.start()
    print("Server started on port 50051")
    return server, communication_service


def create_simulation(simulation_type="PRED_PREY", config_path=None, steps=1000, bounds=[-200, 200, -200, 200], pred_percent=0.25, food_amount=10, prey_spawn_bounds=[50, 150, 50, 150], pred_spawn_bounds=[-150, -50, -150, -50], food_respawn_rate=0.1, neat_agents=True, non_neat=False, hyper_neat=False, neat_percent=0.0, hyper_neat_percent=0.0, non_neat_percent=0.0):
    """Creates the simulation environment and initializes the NEAT population.

    Args:
        simulation_type (str): Type of simulation to run.
        config_path (str): Path to the NEAT configuration file.
        steps (int): Number of steps to run the simulation.
        bounds (list): Bounds for the simulation environment.
        pred_percent (float): Percentage of predators in the population.
        food_amount (int): Amount of food in the environment.
        prey_spawn_bounds (list): Spawn bounds for prey.
        pred_spawn_bounds (list): Spawn bounds for predators.
        food_respawn_rate (float): Rate at which food respawns.
        multi_model (bool): Whether to use multiple models.
        model_split (float): Percentage of agents using the NEAT model.

    Returns:
        env (Environment): The simulation environment.
        population (neat.Population): The NEAT population.
        config (neat.Config): The NEAT configuration.
        populationSize (int): Size of the population.
        pred_pop (int): Number of predators in the population.
        prey_pop (int): Number of prey in the population.
        pred_pop_no_neat (int): Number of predators not using NEAT.
        prey_pop_no_neat (int): Number of prey not using NEAT.
    """
    # Create the environment with optimal number of workers
    num_cores = multiprocessing.cpu_count()
    env = Environment(simulation_type, steps, bounds, food_respawn_rate)
    env.max_workers = max(1, num_cores - 1)
    print(f"INFO:\tUsing {env.max_workers} workers for parallel processing")

    # Loads config data to be used in simulation
    print("START:\tCreating NEAT config...")

    configDict = build_configs(config_path=config_path)
    print("END:\tCreated configs")

    # Generates all relevant agent populations
    print("START:\tCreating population...")
    # Default population, all agents start with this config and resulting genome
    population = neat.Population(configDict["defConfig"])
    pred_pop = int(len(population.population.items())*pred_percent)
    prey_pop = len(population.population.items()) - pred_pop

    if not neat_agents and not non_neat and not hyper_neat:
        print("Must specify at least one of NEAT, non-NEAT, or HyperNEAT to be True.")
        exit(1)

    # Initialize all populations to 0
    pred_pop_neat = 0
    prey_pop_neat = 0
    pred_pop_no_neat = 0
    prey_pop_no_neat = 0
    pred_pop_hyper = 0
    prey_pop_hyper = 0

    if neat_agents:
        # Create NEAT predators and prey
        pred_pop_neat = math.floor(pred_pop * neat_percent)
        prey_pop_neat = math.floor(prey_pop * neat_percent)
    if non_neat:
        # Create non-NEAT predators and prey
        pred_pop_no_neat = math.floor(pred_pop * non_neat_percent)
        prey_pop_no_neat = math.floor(prey_pop * non_neat_percent)
    if hyper_neat:
        # Create HyperNEAT predators and prey
        pred_pop_hyper = math.floor(pred_pop * hyper_neat_percent)
        prey_pop_hyper = math.floor(prey_pop * hyper_neat_percent)

    print("END:\tCreated NEAT population")
    print(f"INFO:\tPredator population: {pred_pop}")
    print(f"INFO:\tPrey population: {prey_pop}")
    print(f"INFO:\tPredator NEAT population: {pred_pop_neat}")
    print(f"INFO:\tPredator STD population: {pred_pop_no_neat}")
    print(f"INFO:\tPredator HyperNEAT population: {pred_pop_hyper}")
    print(f"INFO:\tPrey NEAT population: {prey_pop_neat}")
    print(f"INFO:\tPrey STD population: {prey_pop_no_neat}")
    print(f"INFO:\tPrey HyperNEAT population: {prey_pop_hyper}")

    # Initializes the environment, whether the simulation will be run with multiple models or not
    print("START:\tInitializing environment...")

    env.initialize_environment(
        config=configDict,
        population=population,
        pred_pop_neat=pred_pop_neat,
        prey_pop_neat=prey_pop_neat,
        prey_pop_no_neat=prey_pop_no_neat,
        pred_pop_no_neat=pred_pop_no_neat,
        pred_pop_hyper=pred_pop_hyper,
        prey_pop_hyper=prey_pop_hyper,
        pred_spawn_bounds=pred_spawn_bounds,
        prey_spawn_bounds=prey_spawn_bounds,
        food_amount=food_amount
    )
    print("END:\tEnvironment initialized")

    # Initializes the logger
    print("INFO:\tStarting Logger...")
    logger.info(
        f"Starting simulation with {configDict["defConfig"].pop_size} agents...")
    logger.info(
        f"Using {env.max_workers} Logical CPU cores for parallel processing")

    return env, population, configDict, len(population.population.items()), pred_pop_neat, prey_pop_neat, pred_pop_no_neat, prey_pop_no_neat, pred_pop_hyper, prey_pop_hyper


def evolve_all(
    configList, env,
    pred_pop_neat, prey_pop_neat,
    pred_pop_no_neat, prey_pop_no_neat,
    pred_pop_hyper, prey_pop_hyper,
    pred_spawn_bounds, prey_spawn_bounds,
    eliteism=0.1, crossover_rate=0.7, tournament_size=3
):
    """
    Evolve all agent groups manually without NEAT speciation
    ConfigList indices: 1=pred_no_neat, 2=pred_neat, 3=pred_hyper,
                        4=prey_no_neat, 5=prey_neat, 6=prey_hyper
    """
    all_new_agents = []
    # Define groups: (Class, type_flag, cfg, pop_size, bounds, subclass)
    groups = [
        (Predator, 1, configList["predNeatConfig"], pred_pop_neat,
         pred_spawn_bounds, "predator"),
        (Prey,     1, configList["preyNeatConfig"],
         prey_pop_neat, prey_spawn_bounds, "prey"),
        (Predator, 0, configList["predStdConfig"], pred_pop_no_neat,
         pred_spawn_bounds, "predator"),
        (Prey,     0, configList["preyStdConfig"], prey_pop_no_neat,
         prey_spawn_bounds, "prey"),
        # hyperNEAT stubs if you ever implement them
        (Predator, 2, configList["predHyprConfig"], pred_pop_hyper,
         pred_spawn_bounds, "predator"),
        (Prey,     2, configList["preyHyprConfig"],
            prey_pop_hyper, prey_spawn_bounds, "prey"),
    ]
    for AgentCls, flag, cfg, popSize, bounds, subclass in groups:
        # Gather survivors
        survivors = [a for a in env.agents if isinstance(
            a, AgentCls) and a.type == flag]
        # Save fitness
        for agent in survivors:
            if agent.neat_genome:
                agent.neat_genome.fitness = agent.fitness
        # Select elites
        num_elites = max(1, int(popSize * eliteism))
        elites = sorted(survivors, key=lambda a: a.fitness,
                        reverse=True)[:num_elites]
        num_offspring = popSize - len(elites)
        # Breed offspring using existing helper
        offspring = []
        if flag in (0, 1):
            offspring = breed_and_mutate(
                cfg,
                elites,
                num_offspring,
                bounds,
                multi_model=(flag == 0),
                crossover_rate=crossover_rate,
                torunament_size=tournament_size,
                subclass=subclass
            )
        elif flag == 2:
            offspring = generate_hyperneat_offspring(
                configList["cppn_config"],
                num_offspring,
                bounds,
                substrate_schema=create_schema_from_inputs_outputs(),
                subclass=subclass
            )
        new_group = elites + offspring
        if len(new_group) < popSize:
            print(
                f"WARNING: Generated fewer agents ({len(new_group)}) than expected ({popSize}) for {AgentCls.__name__} type {flag}")
        # Sanity fill if mismatch
        while len(new_group) < popSize:
            # fallback random new genome
            genome = neat.DefaultGenome(random.randint(0, 1_000_000))
            genome.configure_new(cfg.genome_config)
            genome.mutate(cfg.genome_config)
            pos = [random.uniform(bounds[0], bounds[1]),
                   random.uniform(bounds[2], bounds[3])]
            new_group.append(AgentCls(id=genome.key, pos=pos,
                             neat_genome=genome, neat_config=cfg, type=flag))
        assert len(
            new_group) == popSize, f"Group {AgentCls.__name__} flag={flag} expected {popSize}, got {len(new_group)}"
        all_new_agents.extend(new_group)
    # Replace all agents
    env.add_agents(all_new_agents)


# Main function, configures simulation then runs through epochs
def main():
    # Initialize environment first (needed later)
    # check to see if the constants file has any strange numbers
    for name, value in vars(constants).items():
        if isinstance(value, (int, float)) and value <= 0:
            logger.warning(
                f"Constant {name} has a non-positive value: {value} that may cause strange behavior")
        if isinstance(value, float) and value > 999:
            logger.warning(
                f"Constant {name} has a large value: {value} that may cause strange behavior")
    env = None
    communication_service = None

    try:
        # scale bounds
        bounds = [
            bound * constants.SCALE_FACTOR for bound in constants.BOUNDS]
        prey_spawn = [
            bound * constants.SCALE_FACTOR for bound in constants.PREY_SPAWN_BOUNDS]
        pred_spawn = [
            bound * constants.SCALE_FACTOR for bound in constants.PRED_SPAWN_BOUNDS]

        # Creates simulation environment
        print("START:\tCreating simulation environment...")
        env, population, configList, populationSize, pred_pop_neat, prey_pop_neat, pred_pop_no_neat, prey_pop_no_neat, pred_pop_hyper, prey_pop_hyper = create_simulation(
            simulation_type=constants.SIMULATION_TYPE,
            config_path=constants.CONFIG_PATH,
            steps=constants.STEPS,
            bounds=bounds,
            pred_percent=constants.PRED_PERCENT,
            food_amount=constants.FOOD_AMOUNT,
            prey_spawn_bounds=prey_spawn,
            pred_spawn_bounds=pred_spawn,
            food_respawn_rate=constants.FOOD_RESPAWN_RATE,
            neat_agents=constants.NEAT,
            non_neat=constants.NON_NEAT,
            hyper_neat=constants.HYPERNEAT,
            neat_percent=constants.NEAT_PERCENT,
            hyper_neat_percent=constants.HYPERNEAT_PERCENT,
            non_neat_percent=constants.NON_NEAT_PERCENT
        )
        print("END:\tSimulation environment created")

        # Start server with environment access
        server, communication_service = serve(env)
        serverThread = threading.Thread(
            target=server.wait_for_termination, daemon=True)
        serverThread.start()

        logs.session_id = logs.generate_session_id()

        # Create log for the average network size
        # logs.log_avg_network_size(env.agents)
        # Run simulation, looping according to the number of epochs specified
        eliteism = constants.CUT_OFF  # Percentage of agents that will be used for breeding
        crossover_rate = constants.CROSS_OVER_RATE  # Crossover rate for breeding
        tournament_size = constants.TOURNAMENT_SIZE  # Tournament size for selection
        if constants.SAVE_INIT_NETWORKS:
            print("INFO:   Saving initial genomes... this will take a while")
            logs.save_initial_genomes_json(env.agents)
        # print total agents added of each type

        for i in range(constants.EPOCHS):
            agents = env.agents
            num_predators_stand = len(
                [agent for agent in agents if isinstance(agent, Predator) and agent.alive and agent.type == 0])
            num_predators_neat = len(
                [agent for agent in agents if isinstance(agent, Predator) and agent.alive and agent.type == 1])
            num_predators_hyper = len(
                [agent for agent in agents if isinstance(agent, Predator) and agent.alive and agent.type == 2])
            num_preys_stand = len(
                [agent for agent in agents if isinstance(agent, Prey) and agent.alive and agent.type == 0])
            num_preys_neat = len(
                [agent for agent in agents if isinstance(agent, Prey) and agent.alive and agent.type == 1])
            num_preys_hyper = len(
                [agent for agent in agents if isinstance(agent, Prey) and agent.alive and agent.type == 2])

            print(f"INFO:    Initialized Epoch with {num_predators_stand} standard predators, {num_predators_neat} NEAT predators, {num_predators_hyper} HyperNEAT predators, {num_preys_stand} standard preys, {num_preys_neat} NEAT preys, and {num_preys_hyper} HyperNEAT preys.")

            start_time = time.time()  # Start timing the epoch

            # Update communication service with current environment
            if communication_service:
                communication_service.set_environment(env)

            env.run()
            if (i > constants.EPOCHS / 2) and constants.SWAP_BOUNDS:
                pred_bounds = prey_spawn
                prey_bounds = pred_spawn
            else:
                pred_bounds = pred_spawn
                prey_bounds = prey_spawn
            logs.avg_agent_fitness(env.agents)
            evolve_all(
                configList,
                env,
                pred_pop_neat,       # number of neat predators
                prey_pop_neat,       # number of neat prey
                pred_pop_no_neat,    # number of non‑neat predators
                prey_pop_no_neat,    # number of non‑neat prey
                pred_pop_hyper,      # number of hyper‑neat predators
                prey_pop_hyper,      # number of hyper‑neat prey
                pred_bounds,         # spawn bounds for predators this epoch
                prey_bounds          # spawn bounds for prey this epoch
            )
            env.reset(constants.PRED_START_ENERGY, constants.PREY_START_ENERGY,
                      prey_spawn, pred_spawn)
            end_time = time.time()  # End timing the epoch

            epoch_duration = end_time - start_time
            remaining_epochs = constants.EPOCHS - (i + 1)
            estimated_time_remaining = remaining_epochs * epoch_duration

            print(
                f"Epoch {i+1} completed, {constants.EPOCHS - i - 1} epochs remaining")
            estimated_time_remaining_hours = estimated_time_remaining / 3600
            epoch_duration_hours = epoch_duration / 3600
            print(
                f"Estimated time remaining: {estimated_time_remaining_hours:.2f} hours")
            logger.info(
                f"Epoch {i+1} completed in {epoch_duration_hours:.2f} hours")
            logger.info(
                f"Estimated time remaining: {estimated_time_remaining_hours:.2f} hours")

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


if __name__ == "__main__":
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

    # Setup handlers for different log files
    info_handler = logging.FileHandler('./Logs/sim.log', mode='w')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    # # Comment this out when debugging log is unnecessary
    # debug_handler = logging.FileHandler('./Logs/debug.log')
    # debug_handler.setLevel(logging.DEBUG)
    # debug_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    # Set to lowest level you want to capture
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(info_handler)
    # root_logger.addHandler(debug_handler) # Comment this out when debugging log is unnecessary

    logger.info('started')
    main()
