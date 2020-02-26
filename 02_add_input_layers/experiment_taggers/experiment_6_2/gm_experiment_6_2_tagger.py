import re

import numpy as np
from estnltk import ElementaryBaseSpan, Annotation, Layer
from estnltk.taggers import Tagger

class GMExperiment6_2Tagger(Tagger):
    def __init__(self,
                 output_layer='gm_experiment_6_2',
                 input_layers=None,
                 output_attributes=None
                 ):
        if output_attributes is None:
            output_attributes = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                                 'misc']
        if input_layers is None:
            input_layers = ['syntax_gold']
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = output_attributes
        self.conf_param = ()

    def _make_layer(self, text, layers, status=None):
        layer = Layer(self.output_layer, text_object=text, attributes=self.output_attributes)

        for basespan in text[self.input_layers[0]]:
            new_span = ElementaryBaseSpan(basespan.start, basespan.end)
            feats = basespan.feats.split('|')
            new_feats = []
            cases = (
            'nom', 'gen', 'part', 'ill', 'in', 'el', 'all', 'ad', 'abl', 'tr', 'term', 'es', 'abes', 'kom', 'adit')
            for feat in feats:
                if feat in cases:
                    new_feats.append('XX')
                else:
                    new_feats.append(feat)
            feats = '|'.join(new_feats)
            attributes = {'id': basespan.id, 'form': 'XX', 'lemma': basespan.lemma,
                          'upostag': basespan.upostag, 'xpostag': basespan.xpostag,
                          'feats': feats,
                          'head': basespan.head,
                          'deprel': basespan.deprel, 'deps': '_', 'misc': '_'}
            annotation = Annotation(new_span, **attributes)
            layer.add_annotation(new_span, **annotation)

        return layer

    def __doc__(self):
        print("Experiment 6_2: kõik käänded ja sõnavormid kustutatud")