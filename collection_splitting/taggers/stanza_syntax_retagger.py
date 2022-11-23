import os
from collections import OrderedDict
from random import Random

from estnltk import Layer
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger
from estnltk.taggers.standard.syntax.ud_validation.deprel_agreement_retagger import DeprelAgreementRetagger
from estnltk.taggers.standard.syntax.ud_validation.ud_validation_retagger import UDValidationRetagger
from estnltk.taggers import Retagger
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.downloader import get_resource_paths

from estnltk import Text

class StanzaSyntaxRetagger(Retagger):
    """
    This is a retagger that creates a new layer where the spans that have None values in 
    the stanza_syntax_without_entity layer will have a negative id and head based on the original stanza_syntax layer. 
    """
    
    conf_param = [ 'stanza_syntax_layer', 'without_entity_layer', 'ignore_layer']

    def __init__(self,
                 output_layer='stanza_syntax_with_entity',                 
                 stanza_syntax_layer = None, # e.g "stanza_syntax", 
                 without_entity_layer = None, # e.g "stanza_syntax_without_entity",
                 ignore_layer = None, # e.g "stanza_syntax_ignore_entity",                 
                 ):
        
        self.stanza_syntax_layer = stanza_syntax_layer
        self.without_entity_layer = without_entity_layer
        self.ignore_layer = ignore_layer
        if self.ignore_layer!=None:
            self.output_layer = output_layer+"_"+self.ignore_layer.split("_")[-1:][0]
        else:
            self.output_layer=output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc', 'parent_span', 'children',  "status")
                
        self.input_layers = [stanza_syntax_layer, without_entity_layer, ignore_layer]


    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      parent=self.input_layers[0], #stanza_syntax_layer
                      ambiguous=False )
        return layer


    def _make_layer(self, text, layers, status=None):
        
        stanza_syntax_layer = layers[self.input_layers[0]]
        without_entity_layer = layers[self.input_layers[1]]
        ignore_layer = layers[self.input_layers[2]]

        layer = self._make_layer_template()
        layer.text_object=text

        for span in without_entity_layer.spans:              
            attributes = {'id': span.id, 'lemma': span['lemma'], 'upostag': span['upostag'], 'xpostag': span['xpostag'], 'feats': span['feats'], 'head': span['head'], 
                            'deprel': span['deprel'], "status": "remained", 'deps': '_', 'misc': '_', 'parent_span':span['parent_span'], 'children':span['children']}            
            layer.add_annotation(span, **attributes)
        
        
        ignored_tokens = [word for span in ignore_layer for word in span.words]
        for span in ignored_tokens:
            stanza_span = stanza_syntax_layer.get(span)            
            attributes = {'id': -stanza_span.id, 'lemma': stanza_span['lemma'], 'upostag': stanza_span['upostag'], 'xpostag': stanza_span['xpostag'], 'feats': stanza_span['feats']  ,
                            'head': -stanza_span['head'], 'deprel': stanza_span['deprel'], "status": "removed", 'deps': '_', 'misc': '_', 'parent_span':stanza_span['parent_span'], 'children':stanza_span['children']}            
            layer.add_annotation(stanza_span, **attributes)


        return layer
