import os
import re

from estnltk import ElementaryBaseSpan, Annotation, Layer
from estnltk.taggers import Tagger


class GMExperiment5Tagger(Tagger):

    def __init__(self,
                 output_layer='gm_experiment_5',
                 input_layers=None,
                 output_attributes=None
                 ):
        if input_layers is None:
            input_layers = ['syntax_gold']
        if output_attributes is None:
            output_attributes = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                                 'misc']
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = output_attributes
        self.conf_param = ['visl_lemmas']
        self.visl_lemmas = self.visl_lemmas()

    def _make_layer(self, text, layers, status=None):
        layer = Layer(self.output_layer, text_object=text, attributes=self.output_attributes)

        for basespan in text[self.input_layers[0]]:
            new_span = ElementaryBaseSpan(basespan.start, basespan.end)
            lemma = 'XX' if basespan.lemma not in self.visl_lemmas else basespan.lemma

            attributes = {'id': basespan.id, 'form': 'XX', 'lemma': lemma,
                          'upostag': basespan.upostag, 'xpostag': basespan.xpostag,
                          'feats': basespan.feats, 'head': basespan.head,
                          'deprel': basespan.deprel, 'deps': '_', 'misc': '_'}

            annotation = Annotation(new_span, **attributes)
            layer.add_annotation(new_span, **annotation)

        return layer

    def __doc__(self):
        print("Experiment 5: kõik sõnavormid kustutatud + kustutatud kõik lemmad, mis ei esine CG reeglites.")

    def visl_lemmas(self):
        print(os.listdir())
        with open('experiment_taggers/experiment_5/visl_lemmas.txt', 'r', encoding='utf-8') as fin:
            lem = fin.readlines()
            lem = [l.strip() for l in lem]
        visl_regexes = []
        visl_lemmas_clean = []
        for i in lem:
            if re.search('[^-a-züõöäÜÕÖÄšžŽŠA-Z=_]', i):
                visl_regexes.append(i)
            else:
                visl_lemmas_clean.append(i)
        visl_lemmas_set = frozenset(visl_lemmas_clean)
        return visl_lemmas_set
