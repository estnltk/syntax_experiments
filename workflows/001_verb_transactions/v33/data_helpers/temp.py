import networkx as nx
from collections import defaultdict
import pygraphviz as pgv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from networkx.drawing.nx_agraph import graphviz_layout

# from textwrap import wrap


class BaseDiGraph(nx.DiGraph):
    _distances_matrix = None  # matrix for node distances

    def __init__(self):
        super(BaseDiGraph, self).__init__()

    def init_distances_matrix(self):
        self._distances_matrix = {
            x[0]: x[1] for x in nx.all_pairs_shortest_path_length(self)
        }

    def get_distances_matrix(self):
        return self._distances_matrix

    def get_nodes_by_attributes(self, attrname, attrvalue):
        nodes = defaultdict(list)
        {nodes[v].append(k) for k, v in nx.get_node_attributes(self, attrname).items()}
        if attrvalue in nodes:
            return dict(nodes)[attrvalue]
        return []


class SyntaxGraph(BaseDiGraph):

    def __init__(self, stanza_syntax_layer):
        super(SyntaxGraph, self).__init__()
        for data in stanza_syntax_layer:
            if isinstance(data["id"], int):
                # paneme graafi kokku
                self.add_node(
                    data["id"],
                    id=data["id"],
                    lemma=data["lemma"],
                    POS=data["upostag"],
                    deprel=data["deprel"],
                    form=data.text,
                    feats=data["feats"],
                    start=data.start,
                    end=data.end,
                )
                self.add_edge(
                    data["id"] - data["id"] + data["head"],
                    data["id"],
                    deprel=data["deprel"],
                )
        self.init_distances_matrix()

    def draw_graph2(
        self,
        display=False,
        filename=None,
        node_label="lemma",
        highlight=[],
    ):

        # Create a default color for all nodes and a highlight color for selected nodes
        default_color = "lightskyblue"
        highlight_color = "red"

        # Create a new directed graph using pygraphviz
        G = pgv.AGraph(strict=True, directed=True)

        # Add nodes with 'label' attribute set to the 'lemma' from the original graph
        for node_id, data in self.nodes(data=True):
            label = data.get(
                node_label, ""
            )  # Default to empty string if lemma is not present
            color = highlight_color if node_id in highlight else default_color
            if node_id:
                G.add_node(
                    node_id,
                    label=label,
                    shape="ellipse",
                    style="filled",
                    fillcolor=color,
                )
            else:
                G.add_node(node_id, label=label, shape="none", fillcolor=color)

        # Add edges with 'label' attribute set to the 'deprel' from the original graph
        for source, target, data in self.edges(data=True):
            label = data.get(
                "deprel", ""
            )  # Default to empty string if deprel is not present
            G.add_edge(source, target, label=label)

        # Generate layout and draw the graph
        G.layout(prog="dot")

        # Set filename to default if not provided
        if not filename:
            filename = "graph.png"

        # Draw graph to the specified file
        G.draw(filename)

        if display:
            # Display the graph image if we're in a Jupyter notebook environment
            img = mpimg.imread(filename)

            plt.figure(figsize=(10, 10))
            plt.imshow(img)
            plt.axis("off")
            plt.show()

            # Clear the current figure
            plt.clf()

    def draw_graph3(
        self,
        display=False,
        filename=None,
        node_label="lemma",
        highlight=[],
    ):

        # Create a default color for all nodes and a highlight color for selected nodes
        default_color = "lightskyblue"
        highlight_color = "red"

        # Create a new directed graph using pygraphviz
        G = pgv.AGraph(strict=True, directed=True)

        # Add nodes with 'label' attribute set to the 'lemma' from the original graph
        for node_id, data in self.nodes(data=True):
            label = data.get(
                node_label, ""
            )  # Default to empty string if lemma is not present
            color = highlight_color if node_id in highlight else default_color
            if node_id:
                G.add_node(
                    node_id,
                    label=label,
                    shape="none",
                    fillcolor=color,
                )
            else:
                G.add_node(node_id, label=label, shape="none", fillcolor=color)

        # Add edges with 'label' attribute set to the 'deprel' from the original graph
        for source, target, data in self.edges(data=True):
            label = data.get(
                "deprel", ""
            )  # Default to empty string if deprel is not present
            G.add_edge(source, target, label=label)

        # Generate layout and draw the graph
        G.layout(prog="dot")

        # Set filename to default if not provided
        if not filename:
            filename = "graph.png"

        # Draw graph to the specified file
        G.draw(filename)

        if display:
            # Display the graph image if we're in a Jupyter notebook environment
            img = mpimg.imread(filename)

            plt.figure(figsize=(10, 10))
            plt.imshow(img)
            plt.axis("off")
            plt.show()

            # Clear the current figure
            plt.clf()

    def draw_graph(self, **kwargs):
        """
        Puu/graafi joonistamine
        tipp - lemma
        serv - deprel

        title string    Graafi pealkiri
        filename string Failinimi kuhu joonis salvestatakse
        highlight array of integers     tippude id, d mis värvitakse joonisel punaseks
        """
        title = None
        filename = None
        custom_colors = None
        highlight = []
        if "title" in kwargs:
            title = kwargs["title"]

        if "filename" in kwargs:
            filename = kwargs["filename"]

        if "highlight" in kwargs:
            highlight = kwargs["highlight"]

        if "custom_colors" in kwargs:
            custom_colors = kwargs["custom_colors"]

        if not custom_colors:
            colors = ["lightskyblue" for node in self]
        else:
            colors = custom_colors
        # soovitud tipud punaseks

        color_map = [
            "red" if node in highlight else colors[i]
            for (i, node) in enumerate(self.nodes)
        ]

        # print (color_map)
        # joonise suurus, et enamik puudest ära mahuks
        plt.rcParams["figure.figsize"] = (18.5, 10.5)

        # pealkiri
        if title:
            title = "\n".join(wrap(title, 120))
            plt.title(title)

        pos = graphviz_layout(self, prog="dot")
        labels = nx.get_node_attributes(self, "lemma")
        nx.draw(self, pos, labels=labels, with_labels=True, node_color=color_map)
        edge_labels = nx.get_edge_attributes(self, "deprel")
        nx.draw_networkx_edge_labels(self, pos, edge_labels)

        # kui failinimi, siis salvestame faili
        # kui pole, siis joonistame väljundisse
        if filename:
            plt.savefig(f"{filename}.png", dpi=100)
        else:
            plt.show()
        plt.clf()
