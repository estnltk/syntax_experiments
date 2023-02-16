from estnltk import Layer
from estnltk_patches.syntax_tree_operations import *
from estnltk_patches.stanza_syntax_tagger import StanzaSyntaxTagger2


class ConsistencyDecorator:

    def __init__(self, input_type, model_path, output_layer, syntax_layer, morph_layer):
        self.resources_path = model_path
        if not self.resources_path:
            raise ValueError('Missing resources path for StanzaSyntaxTagger')

        self.output_layer = output_layer
        self.syntax_layer = syntax_layer
        self.morph_layer = morph_layer

        self.ignore_tagger = StanzaSyntaxTagger2(ignore_layer=self.output_layer, input_type=input_type,
                                                 input_morph_layer=self.morph_layer, add_parent_and_children=True,
                                                 resources_path=self.resources_path)

    def __call__(self, text_object, phrase_span, annotations):
        """
       Phrase extractor decorator. Adds conservation score and other attributes to the phrase extractor output layer.
        """
        # make phrase_spans to layer (for ignore_tagger, las calculation)
        phrases_layer = Layer(name=self.output_layer,
                              text_object=text_object,
                              attributes=['root_id', 'root'],
                              parent=None,
                              ambiguous=False,
                              enveloping=self.syntax_layer,
                              serialisation_module="syntax_v1"
                              )
        phrases_layer.add_annotation(phrase_span, **annotations)

        # make dict of layers
        layers = {layer: text_object[layer] for layer in text_object.layers}
        layers.update({self.output_layer: phrases_layer})
        # get shortened sentence layer 
        ignore_layer = self.ignore_tagger.make_layer(text_object, layers)

        las_score, uas, la = get_graph_edge_difference(text_object[self.syntax_layer],
                                                       ignore_layer,
                                                       phrases_layer,
                                                       False)
        attributes = {
            'syntax_conservation_score': las_score,
            "unlabelled_attachment_score": uas,
            "label_accuracy": la}

        annotations.update(attributes)

        return annotations
