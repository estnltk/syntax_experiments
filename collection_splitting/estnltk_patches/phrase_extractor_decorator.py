
from estnltk import Layer, Text
from estnltk_patches.syntax_tree_operations import *
import copy

def phrase_extractor_decorator(text_object, phrase_spans, annotations, ignore_tagger,stanza_tagger, ignore_layer, syntax_layer ):
    """
   Phrase extractor decorator. Adds attributes to the phrase extractor output layer.
    """
    # make phrase_spans to layer (for ignore_tagger, las etc)
    phrases_layer = make_layer_template(ignore_layer, 
                                                                ['entity_type', 'free_entity', 'is_valid', 'root_id', 'root'],
                                                                None, syntax_layer, "syntax_v1")
    phrases_layer.add_annotation(phrase_spans, **annotations)
    
    txt = copy.deepcopy(text_object)
    
    # shortened sentence layer
    txt.tag_layer("morph_extended")
    txt.add_layer(phrases_layer)
    ignore_tagger.tag(txt)
    
    # needed for las score
    stanza_tagger.tag( txt )
    
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