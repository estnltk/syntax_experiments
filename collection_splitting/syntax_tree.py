import networkx as nx
from collections import defaultdict


from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
from textwrap import wrap

from estnltk import Text

from scripts.syntax_tree_operations import *


class SyntaxTree(nx.DiGraph):

    """Defineerib süntaksipuu networkx suunamata graafina."""

    def __init__(self, syntax_layer_sentence):
        #super(SyntaxTree, self).__init__()
        """stanza stanza_syntax objektist graafi tegemine"""
        #self.graph = nx.DiGraph()
        self.syntax_layer_sentence = syntax_layer_sentence
        self.nodes = []
        self.edges = []
        self.graph = None
        G = nx.DiGraph()
        for data in self.syntax_layer_sentence:
            #print (data)
            if isinstance(data['id'], int):
                #paneme graafi kokku
                G.add_node(data['id'], id=data['id'], lemma=data['lemma'], pos=data['upostag'], deprel=data['deprel'], form=data.text)
                G.add_edge(data['id'] - data['id'] + data['head'], data['id'], deprel = data['deprel'])
        #return G
        self.nodes = G.nodes 
        self.edges = G.edges 
        self.graph = G
        #print(list(self.nodes))

        

    #TODO params to
    def drawGraph(self, figure_size=(18.5, 10.5), title_wrap_char=120, fig_dpi=100, **kwargs):
        """Puu/graafi joonistamine
        tipp - lemma
        serv - deprel
        """

        # joonise suurus, et enamik puudest ära mahuks
        plt.rcParams["figure.figsize"] = figure_size

        pos = graphviz_layout(self, prog='dot')
        labels = nx.get_node_attributes(self, 'text') # lemma
        nx.draw(self, pos, cmap = plt.get_cmap('jet'),labels=labels, with_labels=True)
        edge_labels = nx.get_edge_attributes(self, 'deprel')
        nx.draw_networkx_edge_labels(self, pos, edge_labels)

        return plt

    
    #def make_graph_from_layer(syntax_layer): 
        

