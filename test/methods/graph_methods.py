# Methods for creating and visualizing different syntax graphs
#
# -- imports
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


# -- graph with all syntax layer attributes
def create_graph_with_all_attributes(text_obj):
    graph = nx.DiGraph()
    
    for word in text_obj.stanza_syntax:
        graph.add_node(
            word['id'],
            id=word['id'],
            lemma=word['lemma'],
            pos=word['upostag'],
            deprel=word['deprel'],
            form=word.text,
            feats=word['feats'],
            start=word.start,
            end=word.end)
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


# -- helper method for create_graph_with_POS, returns singular POS tag or multiple POS tags as string
def get_unique_POS(word):
    pos_list = word.morph_analysis['partofspeech']
    # if POS is ambiguous, only unique tags are kept
    if len(pos_list) > 1:
        char_unique = [char for indx, char in enumerate(pos_list) if char not in pos_list[:indx]]
        return "|".join(char_unique)
    return pos_list[0]
        
# -- graph with word ID-s and POS tags
def create_graph_with_POS(text_obj):
    graph = nx.DiGraph()
    
    for word in text_obj.stanza_syntax:
        graph.add_node(
            word['id'],
            id=word['id'],
            pos=get_unique_POS(word))
        graph.add_edge(word['id'] - word['id'] + word['head'], word['id'], deprel=word['deprel'])
            
    return graph


# -- helper method for create_graph_with_ner_timex, checks if current word is tagged as ner or timex and returns entity type or None
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
    return None

# -- graph with word ID-s and ner or timex entities
def create_graph_with_ner_timex(text_obj):
    graph = nx.DiGraph()
    
    for word in text_obj.stanza_syntax:
        graph.add_node(
            word['id'],
            id=word['id'],
            ner_timex=get_ner_timex(text_obj, word))
        graph.add_edge(word['id'] - word['id'] + word['head'], word['id'], deprel=word['deprel'])
            
    return graph


# -- graph visualization
# method for graph visualization, specific node label to be displayed has to be assigned as string
def draw_graph(graph, label):
    plt.rcParams["figure.figsize"] = (18.5, 10.5)
    pos = graphviz_layout(graph, prog='dot')
    labels = nx.get_node_attributes(graph, label)
    nx.draw(graph, pos, cmap=plt.get_cmap('jet'), labels=labels, with_labels=True, node_color='red')
    edge_labels = nx.get_edge_attributes(graph, 'deprel')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels)
    plt.show()
    plt.clf()