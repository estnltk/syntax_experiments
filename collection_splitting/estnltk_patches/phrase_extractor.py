from estnltk import Layer
from estnltk.taggers import Tagger
from estnltk import EnvelopingBaseSpan
from estnltk.taggers.system.rule_taggers import Ruleset
from typing import Union
from estnltk_neural.taggers.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger
from estnltk_patches.stanza_syntax_tagger import StanzaSyntaxTagger2

from estnltk_patches.syntax_tree import SyntaxTree
from estnltk_patches.syntax_tree_operations import filter_nodes_by_attributes
from estnltk_patches.syntax_tree_operations import extract_base_spans_of_subtree

class PhraseExtractor(Tagger):
    """
    Extracts various types of phases based on UD-syntax. 
Creates layer syntax_ignore_entity by default or with given name.
By default search subtrees with specific dependency relations but there are other options.
User can specify decorator to filter out and annotate phrases. 
There are sensible decorators for each phrasetype. 
    """
    
    conf_param = ['input_type', "deprel", "decorator", "resources_path", "ignore_tagger", "stanza_tagger"]

    def __init__(self,
                 decorator: callable=None,
                 output_layer='syntax_ignore_entity',
                 sentences_layer='sentences',
                 words_layer='words',
                 morph_layer='morph_analysis',
                 syntax_layer="stanza_syntax",
                 input_type='stanza_syntax',  # or 'morph_extended', 'sentences'                
                 deprel=None,
                 output_attributes = ['root_id', 'root'],
                 
                 resources_path = None
                 ):
        
        self.decorator = decorator
        self.deprel = deprel
        self.output_layer = output_layer
        self.output_attributes = output_attributes
        self.input_type = input_type

        if self.input_type in ['morph_analysis', 'morph_extended', "stanza_syntax", "conll_syntax"]:
            self.input_layers = [sentences_layer, morph_layer, words_layer, syntax_layer]
        else:
            raise ValueError('Invalid input type {}'.format(input_type))
            
        if self.decorator:    
            self.resources_path = resources_path
            if not self.resources_path:
                raise ValueError('Missing resources path for StanzaSyntaxTagger')
            tagger_input_type = "morph_extended"
            self.stanza_tagger = StanzaSyntaxTagger(input_type=tagger_input_type, input_morph_layer=tagger_input_type, 
                                                add_parent_and_children=True, resources_path=self.resources_path)
            self.ignore_tagger = StanzaSyntaxTagger2(ignore_layer=self.output_layer, input_type="morph_extended",
                                                 input_morph_layer="morph_extended", add_parent_and_children=True,
                                                 resources_path=self.resources_path)

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      enveloping=self.input_layers[3],
                      ambiguous=False,
                      serialisation_module='syntax_v1')
        return layer

    def _make_layer(self, text, layers, status=None):
        stanza_syntax_layer = layers[self.input_layers[3]]
        layer = self._make_layer_template()
        layer.text_object = text
        
        syntax_layer = self.input_layers[3]
        text_word_idx = 0

        for sentence in text.sentences:       
            sent_end = text_word_idx + len(sentence)
            syntaxtree = SyntaxTree(syntax_layer_sentence=text[syntax_layer][text_word_idx:sent_end])
            ignore_nodes = filter_nodes_by_attributes(syntaxtree, 'deprel', self.deprel)
            for node in ignore_nodes:
                new_span = EnvelopingBaseSpan(sorted(extract_base_spans_of_subtree(syntaxtree, node)))
                annotations = {"root_id":syntaxtree.graph.nodes[node]['span']["id"],
                                     "root":syntaxtree.graph.nodes[node]['span']}
                if self.decorator:
                    annotations = self.decorator(text, new_span, annotations, self.ignore_tagger, self.stanza_tagger, self.output_layer, syntax_layer)
                    
                layer.add_annotation(new_span, **annotations)
                                     
            text_word_idx = sent_end

        return layer
