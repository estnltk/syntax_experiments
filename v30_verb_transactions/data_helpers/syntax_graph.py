import networkx as nx
from collections import defaultdict

# needed for draw_graph function
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# from textwrap import wrap

from .utils import ListUtils


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
                    pos=data["upostag"],
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

    def get_obl_info(self, sentence_obl_layer):
        obl_data = []
        for obl in sentence_obl_layer:
            obl_data.append(
                {
                    "nodes": [
                        self.get_nodes_by_attributes(
                            attrname="start", attrvalue=s.start
                        )[0]
                        for s in obl.spans
                    ],
                    "root_id": obl.root_id,
                    "root_lemma": self.nodes[obl.root_id]["lemma"],
                    "root_case": self.get_node_case(obl.root_id),
                }
            )
        return obl_data

    def get_node_case(self, node_id):
        """
        https://github.com/EstSyntax/EstCG/ (käänded)
        """
        feats = self.nodes[node_id]["feats"]
        for attr in feats:
            if attr in (
                "nom",  # nimetav
                "gen",  # omastav
                "part",  # osastav
                "adit",  # lyh sisse
                "ill",  # sisse
                "in",  # sees
                "el",  # seest
                "all",  # alale
                "ad",  # alal
                "abl",  # alalt
                "tr",  # saav
                "term",  # rajav
                "es",  # olev
                "abes",  # ilma#
                "kom",  # kaasa#
            ):
                return attr
        return "<käändumatu>"

    def is_verb_normal(self, verb):
        """
        verb on "normaalne", kui:
            pole umbisikuline
            verbi aeg on 'past', 'impf', 'pres'
        """
        feats = self.nodes[verb]["feats"].keys()
        # kui on umbisikuline
        if "imps" in feats:
            return False

        # tense pole past, impf, pres
        if not len(ListUtils.list_intersection(["past", "impf", "pres"], feats)):
            return False
        return True

    def draw_graph2(
        self,
        display=False,
        filename=None,
        highlight=[],
    ):
        import pygraphviz as pgv

        # Create a default color for all nodes and a highlight color for selected nodes
        default_color = "lightskyblue"
        highlight_color = "red"

        # Create a new directed graph using pygraphviz
        G = pgv.AGraph(strict=True, directed=True)

        # Add nodes with 'label' attribute set to the 'lemma' from the original graph
        for node_id, data in self.nodes(data=True):
            label = data.get(
                "lemma", ""
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
                G.add_node(
                    node_id, label=label, shape="none", style="none", fillcolor=color
                )

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
        return
