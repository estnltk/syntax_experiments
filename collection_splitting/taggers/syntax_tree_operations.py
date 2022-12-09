import networkx as nx
from collections import defaultdict

# TODO: clear this function up
def get_nodes_by_attributes(syntaxtree,  attrname, attrvalue ):
    """Tipu leidmine atribuudi väärtuse järgi"""
    nodes = defaultdict(list)
    {nodes[v].append(k) for k, v in nx.get_node_attributes(syntaxtree.graph, attrname).items()}
    if attrvalue in nodes:
        return dict(nodes)[attrvalue]
    return []


def get_all_decendants(graph, node):
    """Tagasta list tipu kõikidest lastest (tippude id-d)"""
    #return graph.successors(node) # annab ainult ühe otsese järglase
    return nx.nodes(nx.dfs_tree(graph, node))


def get_subtree_spans(syntaxtree, stanza_layer, node):
    """Tagasta list alampuu tippude base_span-idest"""
    sub_nodes = list(get_all_decendants(syntaxtree.graph, node))
    sub_spans = [spn.base_span for spn in stanza_layer for sn in sub_nodes if spn.id == sn]
    return sub_spans


def get_graph_edge_difference(syntaxtree_orig, syntaxtree_short):
    orig_edges = [edge for edge in syntaxtree_orig.edges(data=True)]
    short_edges = [edge for edge in syntaxtree_short.edges(data=True)]
    
    in_graph = 0
    missing = 0
    total = len(short_edges)
    for edge in short_edges:
        if edge in orig_edges:
            in_graph+= 1
        else:
            #print(edge)
            missing += 1
            
    return total, in_graph, missing



