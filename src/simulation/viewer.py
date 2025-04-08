import json
import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class GenomeViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("NEAT Genome Viewer")
        self.root.geometry("1000x800")
        
        # Load genomes
        try:
            with open('./Data/final_genomes.json', 'r') as file:
                self.genomes = json.load(file)
            self.total_genomes = len(self.genomes)
            if self.total_genomes == 0:
                raise ValueError("No genomes found in the file")
        except FileNotFoundError:
            messagebox.showerror("Error", "Could not find ./Data/final_genomes.json")
            self.root.destroy()
            return
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in the genome file")
            self.root.destroy()
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load genomes: {str(e)}")
            self.root.destroy()
            return
            
        # Initialize current genome index
        self.current_index = 0
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create top controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation controls
        nav_frame = ttk.Frame(controls_frame)
        nav_frame.pack(side=tk.LEFT)
        
        self.prev_button = ttk.Button(nav_frame, text="Previous", command=self.show_previous)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(nav_frame, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.jump_label = ttk.Label(nav_frame, text="Jump to:")
        self.jump_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.jump_var = tk.StringVar()
        self.jump_entry = ttk.Entry(nav_frame, textvariable=self.jump_var, width=8)
        self.jump_entry.pack(side=tk.LEFT, padx=5)
        
        self.jump_button = ttk.Button(nav_frame, text="Go", command=self.jump_to)
        self.jump_button.pack(side=tk.LEFT, padx=5)
        
        # Status info
        info_frame = ttk.Frame(controls_frame)
        info_frame.pack(side=tk.RIGHT)
        
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(info_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Create genome info frame
        info_frame = ttk.LabelFrame(main_frame, text="Genome Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Genome details
        self.genome_key_var = tk.StringVar()
        self.genome_fitness_var = tk.StringVar()
        self.node_count_var = tk.StringVar()
        self.conn_count_var = tk.StringVar()
        
        details_frame = ttk.Frame(info_frame)
        details_frame.pack(fill=tk.X)
        
        ttk.Label(details_frame, text="Genome Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(details_frame, textvariable=self.genome_key_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(details_frame, text="Fitness:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Label(details_frame, textvariable=self.genome_fitness_var).grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(details_frame, text="Nodes:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(details_frame, textvariable=self.node_count_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(details_frame, text="Connections:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Label(details_frame, textvariable=self.conn_count_var).grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Create visualization frame
        viz_frame = ttk.LabelFrame(main_frame, text="Network Visualization", padding="10")
        viz_frame.pack(fill=tk.BOTH, expand=True)
        
        # Matplotlib figure
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Display the first genome
        self.display_current_genome()
        
    def classify_nodes(self, genome):
        """Classify nodes into input, output, bias, and hidden nodes based on connectivity"""
        nodes = {int(k): v for k, v in genome['nodes'].items()}
        connections = genome['connections']
        
        # Extract nodes from connections
        input_candidates = set()
        output_candidates = set()
        for conn_key, conn_data in connections.items():
            # Parse connection key
            if isinstance(conn_data['key'], list):
                in_node, out_node = conn_data['key']
            else:
                # Parse from string if needed
                conn_parts = conn_key.strip('()').split(', ')
                if len(conn_parts) == 2:
                    in_node = int(conn_parts[0])
                    out_node = int(conn_parts[1])
                else:
                    continue
            
            # Collect inputs (sources) and outputs (targets)
            input_candidates.add(in_node)
            output_candidates.add(out_node)
        
        # Input nodes are typically sources that aren't targets
        # (except bias node which is special)
        input_nodes = [node for node in input_candidates if node not in output_candidates or node == -1]
        
        # Output nodes are typically targets that aren't sources
        output_nodes = [node for node in output_candidates if node not in input_candidates]
        
        # If that doesn't work well, we use the alternate approach based on IDs
        if not output_nodes:
            # Determine nodes by IDs - NEAT usually uses small IDs (0-10) for input/output
            input_nodes = [node_id for node_id in nodes.keys() if 0 <= node_id < 10]
            output_nodes = [node_id for node_id in nodes.keys() if 10 <= node_id < 20]
        
        # Bias node is always -1 in NEAT
        bias_nodes = [node_id for node_id in nodes.keys() if node_id < 0]
        
        # Hidden nodes are everything else
        hidden_nodes = [node_id for node_id in nodes.keys() 
                      if node_id not in input_nodes 
                      and node_id not in output_nodes 
                      and node_id not in bias_nodes]
        
        return bias_nodes, input_nodes, output_nodes, hidden_nodes
        
    def display_current_genome(self):
        """Display the current genome"""
        # Update status info
        self.status_var.set(f"Showing genome {self.current_index + 1} of {self.total_genomes}")
        
        # Get current genome
        genome = self.genomes[self.current_index]
        
        # Update genome info
        self.genome_key_var.set(str(genome['key']))
        self.genome_fitness_var.set(f"{genome['fitness']:.2f}" if genome['fitness'] is not None else "None")
        self.node_count_var.set(str(len(genome['nodes'])))
        self.conn_count_var.set(str(len(genome['connections'])))
        
        # Clear the figure
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Create graph
        G = nx.DiGraph()
        
        # Extract nodes
        nodes = {int(node_id): node_data for node_id, node_data in genome['nodes'].items()}
        for node_id, node_data in nodes.items():
            # Initialize node attributes
            G.add_node(node_id, bias=node_data.get('bias', 0.0),
                       activation=node_data.get('activation', 'unknown'),
                       aggregation=node_data.get('aggregation', 'unknown'))
        
        # Extract connections
        for conn_key, conn_data in genome['connections'].items():
            # Check how the connection key is stored
            if isinstance(conn_data['key'], list):
                in_node, out_node = conn_data['key']
            else:
                # Parse from string if needed
                conn_parts = conn_key.strip('()').split(', ')
                if len(conn_parts) == 2:
                    in_node = int(conn_parts[0])
                    out_node = int(conn_parts[1])
                else:
                    continue
            
            # Add edge
            G.add_edge(in_node, out_node, 
                      weight=conn_data.get('weight', 0.0),
                      enabled=conn_data.get('enabled', True))
        
        # Classify nodes into types
        bias_nodes, input_nodes, output_nodes, hidden_nodes = self.classify_nodes(genome)
        
        # Assign colors to nodes by type
        for node in G.nodes():
            if node in bias_nodes:
                G.nodes[node]['color'] = 'purple'
                G.nodes[node]['type'] = 'bias'
            elif node in input_nodes:
                G.nodes[node]['color'] = 'skyblue'
                G.nodes[node]['type'] = 'input'
            elif node in output_nodes:
                G.nodes[node]['color'] = 'lightgreen'
                G.nodes[node]['type'] = 'output'
            else:
                G.nodes[node]['color'] = 'orange'
                G.nodes[node]['type'] = 'hidden'
        
        # Determine node positioning using a layered approach
        pos = {}
        
        # Create layers
        layers = []
        
        # Layer 0: Bias node
        layers.append(bias_nodes)
        
        # Layer 1: Input nodes
        layers.append(input_nodes)
        
        # Determine intermediate hidden layers by traversing the graph
        remaining_hidden = set(hidden_nodes)
        current_layer = set(input_nodes + bias_nodes)
        while remaining_hidden:
            next_layer = set()
            for node in remaining_hidden:
                # Check if all predecessors are already in previous layers
                predecessors = set(G.predecessors(node))
                if predecessors and all(pred in set().union(*layers) for pred in predecessors):
                    next_layer.add(node)
            
            # If can't find any more nodes for the next layer but still have remaining hidden nodes
            if not next_layer and remaining_hidden:
                # Just add nodes with minimal incoming edges
                node_scores = {n: sum(1 for _ in G.predecessors(n)) for n in remaining_hidden}
                min_score = min(node_scores.values()) if node_scores else 0
                next_layer = {n for n, s in node_scores.items() if s == min_score}
            
            if next_layer:
                layers.append(list(next_layer))
                remaining_hidden -= next_layer
                current_layer = next_layer
            else:
                # If we can't determine any more layers, put all remaining in the last layer
                if remaining_hidden:
                    layers.append(list(remaining_hidden))
                    remaining_hidden = set()
        
        # Last layer: Output nodes
        layers.append(output_nodes)
        
        # Position nodes by layer
        num_layers = len(layers)
        for layer_idx, layer_nodes in enumerate(layers):
            x_pos = layer_idx / max(1, num_layers - 1)  # Normalize to [0, 1]
            num_nodes = len(layer_nodes)
            
            for i, node_id in enumerate(sorted(layer_nodes)):
                # Evenly distribute nodes vertically in each layer
                if num_nodes > 1:
                    y_pos = 1.0 - i / (num_nodes - 1)
                else:
                    y_pos = 0.5
                
                pos[node_id] = (x_pos, y_pos)
        
        # Adjust positions to separate bias node from inputs
        for node_id in bias_nodes:
            if node_id in pos:
                x, y = pos[node_id]
                pos[node_id] = (x, 0.1)  # Place bias at the bottom
        
        # Make sure all nodes have positions
        for node in G.nodes():
            if node not in pos:
                # Assign a fallback position for any node without a position
                pos[node] = (0.5, 0.5)
        
        # Draw the nodes
        node_colors = [G.nodes[n].get('color', 'red') for n in G.nodes]
        node_types = [G.nodes[n].get('type', 'unknown') for n in G.nodes]
        
        # Create node labels with activation info
        node_labels = {}
        for n in G.nodes:
            node_type = G.nodes[n].get('type', '')
            if node_type == 'bias':
                node_labels[n] = f"Bias\n({n})"
            elif node_type == 'input':
                node_labels[n] = f"In\n({n})"
            elif node_type == 'output':
                node_labels[n] = f"Out\n({n})"
            else:
                node_labels[n] = f"H{n}"
                
            # Add activation function if available
            activation = G.nodes[n].get('activation', '')
            if activation and activation != 'unknown':
                node_labels[n] += f"\n{activation}"
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=300, node_color=node_colors)
        
        # Draw the node labels
        nx.draw_networkx_labels(G, pos, ax=ax, labels=node_labels, font_size=8)
        
        # Draw the edges with width proportional to weight
        for u, v, data in G.edges(data=True):
            if data.get('enabled', True):
                # Calculate edge width based on weight
                weight = data.get('weight', 0.0)
                width = 1 + abs(weight) * 1.25
                
                # Choose edge color based on weight sign
                edge_color = 'green' if weight > 0 else 'red'
                
                # Draw the edge
                nx.draw_networkx_edges(
                    G, pos, ax=ax,
                    edgelist=[(u, v)],
                    width=width,
                    edge_color=edge_color,
                    arrowsize=10
                )
                
                # Add weight labels to edges
                edge_labels = {(u, v): f"{weight:.2f}"}
                nx.draw_networkx_edge_labels(
                    G, pos, ax=ax,
                    edge_labels=edge_labels,
                    font_size=7
                )
            else:
                # Draw disabled edges as dotted gray lines
                nx.draw_networkx_edges(
                    G, pos, ax=ax,
                    edgelist=[(u, v)],
                    width=0.5,
                    edge_color='gray',
                    style='dotted',
                    arrowsize=5
                )
        
        # Add a legend
        ax.plot([], [], 'o', color='purple', label='Bias Node')
        ax.plot([], [], 'o', color='skyblue', label='Input Nodes')
        ax.plot([], [], 'o', color='lightgreen', label='Output Nodes')
        ax.plot([], [], 'o', color='orange', label='Hidden Nodes')
        ax.plot([], [], '-', color='green', label='Positive Connection')
        ax.plot([], [], '-', color='red', label='Negative Connection')
        ax.plot([], [], ':', color='gray', label='Disabled Connection')
        ax.legend(loc='upper right', fontsize=8)
        
        # Add title with genome info
        ax.set_title(f"Genome {genome['key']} - Fitness: {genome['fitness']:.2f}")
        
        # Remove axis
        ax.set_axis_off()
        
        # Update the canvas
        self.canvas.draw()
    
    def show_next(self):
        """Show the next genome"""
        if self.current_index < self.total_genomes - 1:
            self.current_index += 1
            self.display_current_genome()
    
    def show_previous(self):
        """Show the previous genome"""
        if self.current_index > 0:
            self.current_index -= 1
            self.display_current_genome()
    
    def jump_to(self):
        """Jump to a specific genome index"""
        try:
            idx = int(self.jump_var.get()) - 1  # Convert to 0-based index
            if 0 <= idx < self.total_genomes:
                self.current_index = idx
                self.display_current_genome()
            else:
                messagebox.showwarning("Invalid Index", f"Please enter a number between 1 and {self.total_genomes}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number")

if __name__ == "__main__":
    root = tk.Tk()
    app = GenomeViewer(root)
    root.mainloop()
