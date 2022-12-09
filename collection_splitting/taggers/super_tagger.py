import os
from collections import OrderedDict
from random import Random

from estnltk import Layer
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger
from estnltk.taggers import Tagger
from estnltk.converters.serialisation_modules import syntax_v0

from estnltk import Text

from taggers.syntax_tree import SyntaxTree 
from taggers.syntax_tree_operations import *
import networkx as nx
from estnltk import EnvelopingBaseSpan
import copy 


class SuperTagger(Tagger):
    """
    This is a deprel ignore tagger applied to stanza_syntax layer that creates a new layer 
    from the spans that should be removed if words with given deprels are removed.
    """
    
    conf_param = ['input_type',  "deprel", "ignore_layer", "model_path" ]

    def __init__(self,
                 output_layer='syntax_ignore_entity',
                 sentences_layer='sentences',
                 words_layer='words',
                 morph_layer='morph_analysis',
                 stanza_syntax_layer = "stanza_syntax",
                 input_type='stanza_syntax',  # or 'morph_extended', 'sentences'                
                 deprel = None,
                 ignore_layer = None,  # e.g "syntax_ignore_entity_advmod",
                 model_path = None
                 ):
        # Make an internal import to avoid explicit stanza dependency
        import stanza

        self.deprel = deprel
        if deprel == None:
            raise ValueError('Invalid deprel {}'.format(deprel))
            
        self.output_layer = output_layer+"_"+self.deprel 
        self.output_attributes = ('entity_type', 'free_entity', 'is_valid', "syntax_conservation_score")
        self.input_type = input_type
        self.deprel = deprel
        self.ignore_layer = output_layer+ "_" + self.deprel
    
        if self.input_type in ['morph_analysis', 'morph_extended', "stanza_syntax"]:
            self.input_layers = [sentences_layer, morph_layer, words_layer, stanza_syntax_layer]
        else:
            raise ValueError('Invalid input type {}'.format(input_type))
            
        self.model_path = model_path
        if not model_path:
            raise ValueError('Missing model path')


    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      enveloping=self.input_layers[1],
                      ambiguous=False )
        return layer


    def _make_layer(self, text, layers, status=None):
    
        from taggers.entity_tagger import EntityTagger
        from taggers.stanza_syntax_tagger import StanzaSyntaxTagger2
        from estnltk_neural.taggers.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger
    
        stanza_syntax_layer = layers[self.input_layers[3]]
        layer = self._make_layer_template()
        layer.text_object=text
        
        txt = copy.deepcopy(text)

        # layer with removable spans 
        entity_tagger = EntityTagger(deprel =self.deprel, input_type=self.input_type, morph_layer="morph_extended")
        entity_tagger.tag( txt )
        
        # shortened sentence layer 
        ignore_tagger = StanzaSyntaxTagger2( ignore_layer = self.ignore_layer, input_type="morph_extended", 
                                                    input_morph_layer="morph_extended",  add_parent_and_children=True, resources_path=self.model_path)
        ignore_tagger.tag( txt )
        
        without_entity_layer = "syntax_without_entity_" + self.deprel 
        # stanza for short sentence (for syntaxtree)
        short_sentence = " ".join(txt[without_entity_layer].text)
        short_sent = Text(short_sentence)
        stanza_tagger = StanzaSyntaxTagger(input_type="morph_extended", input_morph_layer="morph_extended", add_parent_and_children=True, resources_path=self.model_path)
        short_sent.tag_layer('morph_extended')
        stanza_tagger.tag( short_sent )
        
        # syntaxtrees to get edges 
        syntaxtree_orig = SyntaxTree(syntax_layer_sentence=txt.stanza_syntax)
        syntaxtree_short = SyntaxTree(syntax_layer_sentence=short_sent.stanza_syntax)

        print(syntaxtree_orig.edges(data=True))
        
        # get how many edges of short sentence tree are in the original tree
        total, in_graph, missing = get_graph_edge_difference(syntaxtree_orig, syntaxtree_short)
        
        LAS_score = None 
        if total != 0:
            LAS_score = round(in_graph*100/total, 1)
        
        print("in", in_graph, "\nmissing", missing)
        print(syntaxtree_short.edges(data=True))

        for span in txt[self.ignore_layer]:
            attributes = {'entity_type': span["entity_type"], 'free_entity': span['free_entity'], 'is_valid': span['is_valid'], 
                                            'syntax_conservation_score': LAS_score}               
            layer.add_annotation(span, **attributes)
        
       
        return layer
