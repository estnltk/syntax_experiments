import networkx as nx
from estnltk import Span
from estnltk import BaseSpan

from .syntax_tree import SyntaxTree

from typing import Any
from typing import List


def filter_nodes_by_attributes(tree: SyntaxTree, attribute: str, value: Any) -> List[int]:
    """Returns list of nodes in the syntax tree that have the desired attribute value"""
    return [node for node, data in tree.nodes.items() if attribute in data and data[attribute] == value]


def filter_spans_by_attributes(tree: SyntaxTree, attribute: str, value: Any) -> List[Span]:
    """Returns list of spans in the syntax tree that have the desired attribute value"""
    return [data['span'] for node, data in tree.nodes.items() if attribute in data and data[attribute] == value]


def extract_base_spans_of_subtree(tree: SyntaxTree, root: int) -> List[BaseSpan]:
    """Returns base-spans of the entire subtree from left to right in the text."""
    nodes = tree.graph.nodes
    return [nodes[idx]['span'].base_span for idx in sorted(nx.dfs_postorder_nodes(tree.graph, root))]
