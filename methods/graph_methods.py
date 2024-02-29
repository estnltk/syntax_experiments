# Methods for creating and visualizing different syntax graphs
#
# -- imports
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


# -- helper method, returns singular POS-tag or multiple POS-tags as string
def get_unique_POS(word):
    pos_list = word.morph_analysis['partofspeech']
    # if POS is ambiguous, only unique tags are kept, e.g. ['V', 'A', 'A'] -> ['V', 'A']
    if len(pos_list) > 1:
        char_unique = [char for indx, char in enumerate(pos_list) if char not in pos_list[:indx]]
        return '('+'|'.join(char_unique)+')'
    return pos_list[0]


# -- helper method, checks if current word is tagged as ner/timex entity and returns entity type or 0
def get_ner_timex(text_obj, stanza_word):
    ner = None
    if len(text_obj.ner) > 0:
        word = text_obj.words.get(stanza_word)
        for n in text_obj.ner:
            for part in n:
                if part==word:
                    ner=word
    timex = text_obj.timexes.get(stanza_word)
    if ner:
        return 'ner'
    if timex:
        return 'timex'
    return '0'


# -- graph with all syntax layer attributes, POS-tags and ner/timex entities
def create_graph(text_obj):
    graph = nx.DiGraph()
    
    for word in text_obj.stanza_syntax:
        graph.add_node(
            word['id'],
            id=word['id'],
            lemma=word['lemma'],
            pos=get_unique_POS(word),
            deprel=word['deprel'],
            form=word.text,
            feats=word['feats'],
            start=word.start,
            end=word.end,
            ner_timex=get_ner_timex(text_obj, word))
        graph.add_edge(word['id'] - word['id'] + word['head'], word['id'], deprel=word['deprel'])
            
    return graph


# -- graph with only word ID-s
def create_graph_with_ids(text_obj):
    graph = nx.DiGraph()
    
    for word in text_obj.stanza_syntax:
        graph.add_node(
            word['id'],
            id=word['id'])
        graph.add_edge(word['id'] - word['id'] + word['head'], word['id'], deprel=word['deprel'])
            
    return graph

        
# -- graph with word ID-s and POS-tags
def create_graph_with_POS(text_obj):
    graph = nx.DiGraph()
    
    for word in text_obj.stanza_syntax:
        graph.add_node(
            word['id'],
            id=word['id'],
            pos=get_unique_POS(word))
        graph.add_edge(word['id'] - word['id'] + word['head'], word['id'], deprel=word['deprel'])
            
    return graph


# -- graph with word ID-s and ner/timex entities
def create_graph_with_ner_timex(text_obj):
    graph = nx.DiGraph()
    
    for word in text_obj.stanza_syntax:
        graph.add_node(
            word['id'],
            id=word['id'],
            ner_timex=get_ner_timex(text_obj, word))
        graph.add_edge(word['id'] - word['id'] + word['head'], word['id'], deprel=word['deprel'])
            
    return graph


# -- method for constructing graph code string, includes node ID-s and edges with deprel by default, additional attributes can be included as list
def get_graph_code(graph, attribute_list=None):
    edges = sorted(graph.edges(data=True), key=lambda x: (x[0], x[1]))
    graph_code = ''
    
    edge_list = []
    for edge in edges:
        edge_list.append('('+str(edge[0])+', '+str(edge[1])+', '+edge[2]['deprel']+')')
    
    graph_code = ','.join(edge_list)
    
    if attribute_list != None:
        for attr in attribute_list:
            node_list = []
            for edge in edges:
                subgraph = graph.edge_subgraph([edge[:2]])
                node_list += [node for node in subgraph.nodes(data=True) if node not in node_list]
                
            attr_value_list = [node[1][attr] for node in node_list if len(node[1]) > 0]
            graph_code = '-'.join(attr_value_list)+','+graph_code
    
    return '('+graph_code+')'


# -- method for graph visualization, specific node label to be displayed has to be assigned as string
def draw_graph(graph, label):
    plt.rcParams["figure.figsize"] = (18.5, 10.5)
    pos = graphviz_layout(graph, prog='dot')
    labels = nx.get_node_attributes(graph, label)
    nx.draw(graph, pos, cmap=plt.get_cmap('jet'), labels=labels, with_labels=True, node_color='red')
    edge_labels = nx.get_edge_attributes(graph, 'deprel')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels)
    plt.show()
    plt.clf()