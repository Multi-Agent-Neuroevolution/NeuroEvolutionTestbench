import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import configparser


class GenomeViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("NEAT Genome Viewer")
        self.root.geometry("1000x800")

        # Prompt user to select a genome file
        filepath = filedialog.askopenfilename(
            title="Select genome file",
            initialdir=os.path.join(os.getcwd(), "Data"),
            filetypes=[("JSON files", "*.json")]
        )
        if not filepath:
            messagebox.showerror("Error", "No file selected")
            self.root.destroy()
            return

        # Load genomes
        try:
            with open(filepath, 'r') as file:
                self.genomes = json.load(file)
            self.total_genomes = len(self.genomes)
            if self.total_genomes == 0:
                raise ValueError("No genomes found in the file")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find {filepath}")
            self.root.destroy()
            return
        except json.JSONDecodeError:
            messagebox.showerror(
                "Error", f"Invalid JSON format in the genome file: {filepath}")
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

        self.prev_button = ttk.Button(
            nav_frame, text="Previous", command=self.show_previous)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.next_button = ttk.Button(
            nav_frame, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.jump_label = ttk.Label(nav_frame, text="Jump to:")
        self.jump_label.pack(side=tk.LEFT, padx=(20, 5))

        self.jump_var = tk.StringVar()
        self.jump_entry = ttk.Entry(
            nav_frame, textvariable=self.jump_var, width=8)
        self.jump_entry.pack(side=tk.LEFT, padx=5)

        self.jump_button = ttk.Button(
            nav_frame, text="Go", command=self.jump_to)
        self.jump_button.pack(side=tk.LEFT, padx=5)

        # Max fitness button
        self.max_button = ttk.Button(
            nav_frame, text="Max Fitness", command=self.goto_max_fitness)
        self.max_button.pack(side=tk.LEFT, padx=10)

        # Status info
        info_frame = ttk.Frame(controls_frame)
        info_frame.pack(side=tk.RIGHT)

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(info_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT, padx=5)

        # Create genome info frame
        info_frame = ttk.LabelFrame(
            main_frame, text="Genome Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # Genome details
        self.genome_key_var = tk.StringVar()
        self.genome_fitness_var = tk.StringVar()
        self.node_count_var = tk.StringVar()
        self.conn_count_var = tk.StringVar()

        details_frame = ttk.Frame(info_frame)
        details_frame.pack(fill=tk.X)

        ttk.Label(details_frame, text="Genome Key:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(details_frame, textvariable=self.genome_key_var).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(details_frame, text="Fitness:").grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Label(details_frame, textvariable=self.genome_fitness_var).grid(
            row=0, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(details_frame, text="Nodes:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(details_frame, textvariable=self.node_count_var).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(details_frame, text="Connections:").grid(
            row=1, column=2, sticky=tk.W, padx=5, pady=2)
        ttk.Label(details_frame, textvariable=self.conn_count_var).grid(
            row=1, column=3, sticky=tk.W, padx=5, pady=2)

        # Create visualization frame
        viz_frame = ttk.LabelFrame(
            main_frame, text="Network Visualization", padding="10")
        viz_frame.pack(fill=tk.BOTH, expand=True)

        # Matplotlib figure
        self.figure = plt.Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Display the first genome
        self.display_current_genome()

    def _load_configs(self):
        """Load IO/hidden counts from Config/neat.conf and Config/hypr.conf if present."""
        results = []
        for name in ("neat.conf", "hypr.conf"):
            path = os.path.join(os.getcwd(), "Config", name)
            if not os.path.exists(path):
                continue
            try:
                cp = configparser.ConfigParser()
                cp.optionxform = str
                cp.read(path)
                nin = cp.getint('DefaultGenome', 'num_inputs', fallback=None)
                nout = cp.getint('DefaultGenome', 'num_outputs', fallback=None)
                nhid = cp.getint('DefaultGenome', 'num_hidden', fallback=0)
                if nin and nout:
                    results.append({
                        'path': path,
                        'num_inputs': nin,
                        'num_outputs': nout,
                        'num_hidden': nhid,
                    })
            except Exception:
                continue
        return results

    def _choose_config_for_genome(self, genome, configs):
        """Pick a config by matching number of negative id inputs observed in connections."""
        neg_ids = set()
        conns = genome.get('connections', {})
        for ck, cd in conns.items():
            u = v = None
            if isinstance(cd, dict) and isinstance(cd.get('key'), list) and len(cd['key']) == 2:
                u, v = cd['key']
            elif isinstance(ck, str):
                parts = ck.strip('()').split(',')
                if len(parts) == 2:
                    try:
                        u = int(parts[0].strip())
                        v = int(parts[1].strip())
                    except Exception:
                        pass
            if isinstance(u, int) and u < 0:
                neg_ids.add(u)
            if isinstance(v, int) and v < 0:
                neg_ids.add(v)
        if not configs:
            return None
        if not neg_ids:
            # fallback to first config
            return configs[0]
        neg_count = len(neg_ids)
        return min(configs, key=lambda c: abs(c['num_inputs'] - neg_count))

    def classify_nodes(self, G, config):
        """Classify nodes into input, output, and hidden using NEAT/neat-python conventions."""
        all_node_ids = [n for n in G.nodes() if isinstance(n, int)]
        input_nodes = sorted([n for n in all_node_ids if n < 0])
        non_input_ids = sorted([n for n in all_node_ids if n >= 0])

        output_nodes = []
        if config and config.get('num_outputs') is not None:
            num_outputs = config['num_outputs']
            output_nodes = [n for n in non_input_ids if n < num_outputs]
        else:
            # Fallback if no config: guess that outputs have no enabled outgoing edges
            H = nx.DiGraph()
            H.add_nodes_from(G.nodes())
            H.add_edges_from([(u, v) for u, v, d in G.edges(
                data=True) if d.get('enabled', True) and u != v])
            output_nodes = sorted(
                [n for n in non_input_ids if H.out_degree(n) == 0])
            # If still no outputs, guess the first few non-negative IDs are outputs
            if not output_nodes and non_input_ids:
                output_nodes = non_input_ids[:min(5, len(non_input_ids))]

        hidden_nodes = sorted(
            [n for n in non_input_ids if n not in output_nodes])
        # No explicit bias node type
        return [], input_nodes, output_nodes, hidden_nodes

    def display_current_genome(self):
        """Display the current genome"""
        # Update status info
        self.status_var.set(
            f"Showing genome {self.current_index + 1} of {self.total_genomes}")

        # Get current genome
        genome = self.genomes[self.current_index]

        # Update genome info
        self.genome_key_var.set(str(genome['key']))
        self.genome_fitness_var.set(
            f"{genome['fitness']:.2f}" if genome['fitness'] is not None else "None")
        self.node_count_var.set(str(len(genome.get('nodes', {}))))
        self.conn_count_var.set(str(len(genome.get('connections', {}))))

        # Clear the figure
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Create graph from connections FIRST, so nodes that only appear in edges are included
        G = nx.DiGraph()

        # 1. Add all nodes from the genome's 'nodes' dictionary
        node_attrs = {int(nid): nd for nid,
                      nd in genome.get('nodes', {}).items()}
        for nid, data in node_attrs.items():
            G.add_node(nid, **data)

        # 2. Add all nodes that might only appear in connections (inputs)
        connections = genome.get('connections', {})
        for conn_key, conn_data in connections.items():
            u, v = None, None
            if isinstance(conn_data, dict) and 'key' in conn_data and len(conn_data['key']) == 2:
                u, v = conn_data['key']
            elif isinstance(conn_key, str):
                try:
                    u, v = map(int, conn_key.strip('()').split(','))
                except ValueError:
                    continue

            if u is not None and not G.has_node(u):
                G.add_node(u)
            if v is not None and not G.has_node(v):
                G.add_node(v)

        # 3. Add edges from connections
        for conn_key, conn_data in connections.items():
            u, v = None, None
            if isinstance(conn_data, dict) and 'key' in conn_data and len(conn_data['key']) == 2:
                u, v = conn_data['key']
            elif isinstance(conn_key, str):
                try:
                    u, v = map(int, conn_key.strip('()').split(','))
                except ValueError:
                    continue

            if u is None or v is None or u == v:
                continue

            G.add_edge(u, v, weight=conn_data.get('weight', 0.0),
                       enabled=conn_data.get('enabled', True))

        # Get config for classification
        configs = getattr(self, '_configs_cache', None)
        if configs is None:
            self._configs_cache = self._load_configs()
            configs = self._configs_cache
        chosen_config = self._choose_config_for_genome(genome, configs)

        # Classify nodes
        _, input_nodes, output_nodes, hidden_nodes = self.classify_nodes(
            G, chosen_config)

        # Assign colors and types
        for node in G.nodes():
            if node in input_nodes:
                G.nodes[node]['type'] = 'input'
                G.nodes[node]['color'] = 'skyblue'
            elif node in output_nodes:
                G.nodes[node]['type'] = 'output'
                G.nodes[node]['color'] = 'lightgreen'
            elif node in hidden_nodes:
                G.nodes[node]['type'] = 'hidden'
                G.nodes[node]['color'] = 'orange'
            else:
                G.nodes[node]['type'] = 'unknown'
                G.nodes[node]['color'] = 'grey'

        # Simple layered positioning
        pos = {}
        layer_map = {
            'input': sorted(input_nodes),
            'hidden': sorted(hidden_nodes),
            'output': sorted(output_nodes)
        }

        # Filter out empty layers and define order
        layer_order = ['input', 'hidden', 'output']
        layers = [layer_map[name] for name in layer_order if layer_map[name]]

        num_layers = len(layers)
        for layer_idx, layer_nodes in enumerate(layers):
            x_pos = 0.5
            if num_layers > 1:
                x_pos = layer_idx / (num_layers - 1)

            count = len(layer_nodes)
            for i, nid in enumerate(layer_nodes):
                y_pos = 0.5
                if count > 1:
                    y_pos = 1.0 - (i / (count - 1))
                pos[nid] = (x_pos, y_pos)

        # Handle unclassified nodes if any
        unclassified = [n for n in G.nodes() if n not in pos]
        for i, nid in enumerate(unclassified):
            pos[nid] = (0.5, -0.1 * (i + 1))  # Place below

        # Drawing logic...
        node_colors = [G.nodes[n].get('color', 'red') for n in G.nodes]
        node_labels = {}
        for n in G.nodes:
            node_type = G.nodes[n].get('type', '')
            label_text = str(n)
            if node_type:
                label_text = f"{node_type[0].upper()}{n}"

            activation = G.nodes[n].get('activation')
            if activation and activation != 'unknown':
                label_text += f"\n{activation[:4]}"
            node_labels[n] = label_text

        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_size=500, node_color=node_colors)
        nx.draw_networkx_labels(G, pos, ax=ax, labels=node_labels, font_size=8)

        for u, v, data in G.edges(data=True):
            if u == v:
                continue
            style = 'solid' if data.get('enabled', True) else 'dotted'
            color = 'gray'
            width = 0.5
            if data.get('enabled', True):
                weight = data.get('weight', 0.0)
                color = 'green' if weight > 0 else 'red'
                width = 1 + abs(weight)

            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(
                u, v)], width=width, edge_color=color, style=style, arrowsize=15)
            if data.get('enabled', True):
                nx.draw_networkx_edge_labels(G, pos, ax=ax, edge_labels={
                                             (u, v): f"{data['weight']:.2f}"}, font_size=7)

        # Dynamic legend
        legend_handles = []
        node_types_present = {G.nodes[n].get('type') for n in G.nodes}

        type_colors = {'input': 'skyblue', 'output': 'lightgreen',
                       'hidden': 'orange', 'unknown': 'grey'}
        for ntype in sorted(type_colors.keys()):
            if ntype in node_types_present:
                legend_handles.append(plt.Line2D(
                    [0], [0], marker='o', color='w', label=f'{ntype.capitalize()} Node', markersize=10, markerfacecolor=type_colors[ntype]))

        enabled_edges = [(u, v, d) for u, v, d in G.edges(
            data=True) if d.get('enabled', True) and u != v]
        has_pos = any(d.get('weight', 0.0) > 0 for _, _, d in enabled_edges)
        has_neg = any(d.get('weight', 0.0) < 0 for _, _, d in enabled_edges)
        has_disabled = any(not d.get('enabled', True)
                           for _, _, d in G.edges(data=True) if d)

        if has_pos:
            legend_handles.append(plt.Line2D(
                [0], [0], color='green', lw=2, label='Positive Weight'))
        if has_neg:
            legend_handles.append(plt.Line2D(
                [0], [0], color='red', lw=2, label='Negative Weight'))
        if has_disabled:
            legend_handles.append(plt.Line2D(
                [0], [0], color='gray', lw=1, ls=':', label='Disabled'))

        if legend_handles:
            ax.legend(handles=legend_handles, loc='best')

        ax.set_title(
            f"Genome {genome['key']} - Fitness: {self.genome_fitness_var.get()}")
        ax.set_axis_off()
        self.canvas.draw()

    def goto_max_fitness(self):
        """Jump to the genome with the highest non-None fitness."""
        best_idx = None
        best_fit = None
        for i, g in enumerate(self.genomes):
            fit = g.get('fitness', None)
            if fit is None:
                continue
            if best_fit is None or fit > best_fit:
                best_fit = fit
                best_idx = i
        if best_idx is None:
            messagebox.showinfo(
                "Max Fitness", "No genomes with fitness available.")
            return
        self.current_index = best_idx
        self.display_current_genome()

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
                messagebox.showwarning(
                    "Invalid Index", f"Please enter a number between 1 and {self.total_genomes}")
        except ValueError:
            messagebox.showwarning(
                "Invalid Input", "Please enter a valid number")


if __name__ == "__main__":
    root = tk.Tk()
    app = GenomeViewer(root)
    root.mainloop()
