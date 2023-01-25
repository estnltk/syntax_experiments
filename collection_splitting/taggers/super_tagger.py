
from estnltk import Layer
from estnltk.taggers import Tagger
from taggers.phrase_extractor import PhraseExtractor
from taggers.stanza_syntax_tagger import StanzaSyntaxTagger2
from taggers.syntax_tree import SyntaxTree
from taggers.syntax_tree_operations import *
import copy

class SuperTagger(Tagger):
    """
    This is a deprel ignore tagger applied to stanza_syntax layer that creates a new layer
    from the spans that should be removed if words with given deprels are removed.
    """

    conf_param = ['input_type', "deprel", "ignore_layer", "model_path", "phrase_extractor", "ignore_tagger"]

    def __init__(self,
                 output_layer='syntax_ignore_entity',
                 sentences_layer='sentences',
                 words_layer='words',
                 morph_layer='morph_analysis',
                 stanza_syntax_layer="stanza_syntax",
                 input_type='stanza_syntax',  # or 'morph_extended', 'sentences'
                 deprel=None,
                 model_path=None,
                 ignore_layer = None
                 ):
        # Make an internal import to avoid explicit stanza dependency
        import stanza

        if deprel is None:
            raise ValueError('Invalid deprel {}'.format(deprel))
        self.deprel = deprel

        self.input_type = input_type
        if self.input_type not in ['morph_analysis', 'morph_extended', "stanza_syntax"]:
            raise ValueError('Invalid input type {}'.format(input_type))
        self.input_layers = [sentences_layer, morph_layer, words_layer, stanza_syntax_layer]

        if not model_path:
            raise ValueError('Missing model path')
        self.model_path = model_path

        self.output_layer = ignore_layer 
        self.output_attributes = ('entity_type', 'free_entity', 'is_valid', "syntax_conservation_score", "UnlabelledAttachmentScore", "LabelAccuracy")
        self.ignore_layer = ignore_layer

        self.phrase_extractor = PhraseExtractor(deprel=self.deprel, input_type=self.input_type, morph_layer="morph_extended", output_layer=self.output_layer)
        self.ignore_tagger = StanzaSyntaxTagger2(ignore_layer=self.ignore_layer, input_type="morph_extended",
                                                 input_morph_layer="morph_extended", add_parent_and_children=True,
                                                 resources_path=self.model_path)

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      enveloping=self.input_layers[1],
                      ambiguous=False)
        return layer

    def _make_layer(self, text, layers, status=None):

        layer = self._make_layer_template()
        layer.text_object = text

        txt = copy.deepcopy(text)

        # layer with removable spans
        self.phrase_extractor.tag(txt)
        # shortened sentence layer
        self.ignore_tagger.tag(txt)

        without_entity_layer = "syntax_without_entity" #+ "_" + self.deprel

        #las_score, uas, la  = get_las_score(txt.stanza_syntax, txt[without_entity_layer])
        las_score, uas, la = get_graph_edge_difference(txt.stanza_syntax, txt[without_entity_layer], txt[self.ignore_layer])
        for span in txt[self.ignore_layer]:
            attributes = {'entity_type': span["entity_type"], 'free_entity': span["free_entity"],
                          'is_valid': span['is_valid'],
                          'syntax_conservation_score': las_score, "UnlabelledAttachmentScore":uas, "LabelAccuracy":la }
            layer.add_annotation(span, **attributes)

        return layer
