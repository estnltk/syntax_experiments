from estnltk import Layer, Text
from estnltk.taggers import Tagger

from .phrase_extractor import PhraseExtractor
from .time_loc_decorator import TimeLocDecorator

from typing import MutableMapping

class TimeLocTagger(Tagger):
    """Class for tagging time/location OBL phrases"""
    conf_param = ['decorator', 'extractor']

    def __init__(self,
                 output_layer="time_loc",
                 input_type="stanza_syntax",
                 syntax_layer="stanza_syntax",
                 morph_layer="morph_analysis"):
        self.output_layer = output_layer
        self.input_layers = [input_type, syntax_layer, morph_layer]
        self.output_attributes = ["obl_type", "root_id", "root"]
        self.decorator = TimeLocDecorator()
        self.extractor = PhraseExtractor(deprel="obl", decorator=self.decorator, input_type=self.input_layers[0],
                                         syntax_layer=self.input_layers[1], output_layer=self.output_layer,
                                         morph_layer=self.input_layers[2], output_attributes=self.output_attributes
                                         )

    def _make_layer(self, text: Text, layers: MutableMapping[str, Layer], status: dict) -> Layer:
        return self.extractor._make_layer(text, layers, status)
