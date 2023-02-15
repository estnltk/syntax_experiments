
from estnltk import Layer, Text
from estnltk_patches.syntax_tree_operations import *
import copy
from estnltk_neural.taggers.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger
from estnltk_patches.stanza_syntax_tagger import StanzaSyntaxTagger2
import datetime


class ConsistencyDecorator:
    
    def __init__(self, input_type, model_path, output_layer, syntax_layer, morph_layer):
        self.resources_path = model_path
        if not self.resources_path:
            raise ValueError('Missing resources path for StanzaSyntaxTagger')
                       
        self.output_layer =  output_layer       
        self.syntax_layer = syntax_layer 
        self.morph_layer = morph_layer
        
        self.ignore_tagger = StanzaSyntaxTagger2(ignore_layer=self.output_layer, input_type=input_type,
                                             input_morph_layer=self.morph_layer , add_parent_and_children=True,
                                             resources_path=self.resources_path)

    
    
    def __call__(self, text_object, phrase_span, annotations):
        """
       Phrase extractor decorator. Adds attributes to the phrase extractor output layer.
        """
        # make phrase_spans to layer (for ignore_tagger, las etc)
        phrases_layer = Layer(name=self.output_layer,
              text_object=text_object,
              attributes=['root_id', 'root'],
              parent=None,
              ambiguous=False,
              enveloping = self.syntax_layer, 
              serialisation_module="syntax_v1"
              )                                                            
        phrases_layer.add_annotation(phrase_span, **annotations)
        
        # temporarily add phrases layer 
        text_object.add_layer(phrases_layer)
        ignore_layer = self.ignore_tagger.make_layer(text_object, text_object.layers)  
        
        las_score, uas, la = get_graph_edge_difference(text_object["stanza_syntax"], ignore_layer, phrases_layer, False)

        # remove the temporary phrases layer 
        text_object.pop_layer(self.output_layer)

        attributes = {
            'syntax_conservation_score': las_score, 
            "UnlabelledAttachmentScore":uas, 
            "LabelAccuracy":la }

        annotations.update(attributes)
        
        return annotations
    

