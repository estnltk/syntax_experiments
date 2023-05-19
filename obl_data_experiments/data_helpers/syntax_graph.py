import networkx as nx
from collections import defaultdict

# needed for draw_graph function
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
from textwrap import wrap

from .utils import ListUtils

class BaseDiGraph(nx.DiGraph):
	_distances_matrix = None  # matrix for node distances

	def __init__(self):
		super(BaseDiGraph, self).__init__()
		self._distances_matrix = {x[0]: x[1] for x in nx.all_pairs_shortest_path_length(self)}

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
			if isinstance(data['id'], int):
				# paneme graafi kokku
				self.add_node(
					data['id'],
					id=data['id'],
					lemma=data['lemma'],
					pos=data['upostag'],
					deprel=data['deprel'],
					form=data.text,
					feats=data['feats'],
					start=data.start,
					end=data.end)
				self.add_edge(data['id'] - data['id'] + data['head'], data['id'], deprel=data['deprel'])

	def get_obl_info(self, sentence_obl_layer):
		obl_data = []
		for obl in sentence_obl_layer:
			obl_data.append({
				'nodes': [self.get_nodes_by_attributes(attrname='start', attrvalue=s.start)[0] for s in obl.spans],
				'root_id': obl.root_id,
				'root_lemma': self.nodes[obl.root_id]['lemma'],
				'root_case': self.get_node_case(obl.root_id)
			})
		return obl_data

	def get_node_case(self, node_id):
		"""
		https://github.com/EstSyntax/EstCG/ (käänded)
		"""
		feats = self.nodes[node_id]['feats']
		for attr in feats:
			if attr in (
				'nom',  # nimetav
				'gen',  # omastav
				'part',  # osastav
				'adit',  # lyh sisse
				'ill',  # sisse
				'in',  # sees
				'el',  # seest
				'all',  # alale
				'ad',  # alal
				'abl',  # alalt
				'tr',  # saav
				'term',  # rajav
				'es',  # olev
				'abes',  # ilma#
				'kom',  # kaasa#
			):
				return attr
		return '<käändumatu>'

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
		if 'title' in kwargs:
			title = kwargs['title']

		if 'filename' in kwargs:
			filename = kwargs['filename']

		if 'highlight' in kwargs:
			highlight = kwargs['highlight']

		if 'custom_colors' in kwargs:
			custom_colors = kwargs['custom_colors']

		if not custom_colors:
			colors = ['lightskyblue' for node in self]
		else:
			colors = custom_colors
		# soovitud tipud punaseks

		color_map = ['red' if node in highlight else colors[i] for (i, node) in enumerate(self.nodes)]

		# print (color_map)
		# joonise suurus, et enamik puudest ära mahuks
		plt.rcParams["figure.figsize"] = (18.5, 10.5)

		# pealkiri
		if title:
			title = ("\n".join(wrap(title, 120)))
			plt.title(title)

		pos = graphviz_layout(self, prog='dot')
		labels = nx.get_node_attributes(self, 'lemma')
		nx.draw(self, pos, cmap=plt.get_cmap('jet'), labels=labels, with_labels=True, node_color=color_map)
		edge_labels = nx.get_edge_attributes(self, 'deprel')
		nx.draw_networkx_edge_labels(self, pos, edge_labels)

		# kui failinimi, siis salvestame faili
		# kui pole, siis joonistame väljundisse
		if filename:
			plt.savefig(f'{filename}.png', dpi=100)
		else:
			plt.show()
		plt.clf()

	def is_verb_normal(self, verb):
		"""
		verb on "normaalne", kui pole umbisikuline ja verbi aeg on 'past' või 'impf' või 'pres'
		"""
		feats = self.nodes[verb]['feats'].keys()
		# kui on umbisikuline
		if 'imps' in feats:
			return True

		# tense pole past, impf, pres
		if not len(ListUtils.list_intersection(['past', 'impf', 'pres'], feats)):
			return True
		return False

