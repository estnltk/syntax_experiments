
from estnltk import Layer, Text
from estnltk_patches.syntax_tree_operations import *
import copy
from estnltk_neural.taggers.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger
from estnltk_patches.stanza_syntax_tagger import StanzaSyntaxTagger2
import datetime


class ConsistencyDecorator:
    
    def __init__(self, model_path, output_layer, syntax_layer):
        self.resources_path = model_path
        if not self.resources_path:
            raise ValueError('Missing resources path for StanzaSyntaxTagger')
        tagger_input_type = "morph_extended"
        self.stanza_tagger = StanzaSyntaxTagger(input_type=tagger_input_type, input_morph_layer=tagger_input_type, 
                                            add_parent_and_children=True, resources_path=self.resources_path)
                                            
        self.output_layer =  output_layer                               
        self.ignore_tagger = StanzaSyntaxTagger2(ignore_layer=self.output_layer, input_type="morph_extended",
                                             input_morph_layer="morph_extended", add_parent_and_children=True,
                                             resources_path=self.resources_path)
                                             
        self.syntax_layer = syntax_layer                                     
    
    
    
    def __call__(self, text_object, phrase_spans, annotations):
        """
       Phrase extractor decorator. Adds attributes to the phrase extractor output layer.
        """
        # make phrase_spans to layer (for ignore_tagger, las etc)
        phrases_layer = make_layer_template(self.output_layer, 
                                                                    ['entity_type', 'free_entity', 'is_valid', 'root_id', 'root'],
                                                                    None, self.syntax_layer, "syntax_v1")
        phrases_layer.add_annotation(phrase_spans, **annotations)
        
        txt = copy.deepcopy(text_object)
        
        # shortened sentence layer
        txt.tag_layer("morph_extended")
        txt.add_layer(phrases_layer)
        self.ignore_tagger.tag(txt)
        
        # needed for las score
        self.stanza_tagger.tag( txt )
        
        without_entity_layer = "syntax_without_entity"
        
        las_score, uas, la = get_graph_edge_difference(txt.stanza_syntax, txt[without_entity_layer], phrases_layer, False)

        for span in phrases_layer:
            attributes = {'entity_type': span["entity_type"], 'free_entity': span["free_entity"],
                          'is_valid': span['is_valid'],
                          'syntax_conservation_score': las_score, "UnlabelledAttachmentScore":uas, "LabelAccuracy":la }

            annotations.update(attributes)
        return annotations
    
    

def make_layer_template(name, attributes, parent, enveloping, module):
        """Creates and returns a template of the layer."""
        layer = Layer(name=name,
                      text_object=None,
                      attributes=attributes,
                      parent=parent, 
                      ambiguous=False ,
                      enveloping = enveloping, 
                      serialisation_module=module)
        return layer
