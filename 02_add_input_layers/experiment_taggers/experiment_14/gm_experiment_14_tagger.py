from estnltk import ElementaryBaseSpan, Annotation, Layer

from estnltk.taggers import Tagger
import numpy as np

class GMExperiment14Tagger(Tagger):
    def __init__(self, output_layer='gm_experiment_14', input_layers=None, output_attributes=None, collection=None):
        if output_attributes is None:
            output_attributes = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                                 'misc']
        if input_layers is None:
            input_layers = ['syntax_gold']
        self.conf_param = ['deleted_lemmas', 'collection']
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = output_attributes
        self.collection = collection
        self.deleted_lemmas = deleted_lemmas(self.collection)

    def _make_layer(self, text, layers, status=None):
        layer = Layer(self.output_layer, text_object=text, attributes=self.output_attributes)

        for basespan in text[self.input_layers[0]]:
            new_span = ElementaryBaseSpan(basespan.start, basespan.end)
            lemma = 'XX' if basespan.lemma in self.deleted_lemmas else basespan.lemma
            attributes = {'id': basespan.id, 'form': 'XX',
                          'lemma': lemma,
                          'upostag': basespan.upostag, 'xpostag': basespan.xpostag, 'feats': basespan.feats,
                          'head': basespan.head,
                          'deprel': basespan.deprel, 'deps': '_', 'misc': '_'}
            annotation = Annotation(new_span, **attributes)
            layer.add_annotation(new_span, **annotation)

        return layer

    def __doc__(self):
        print("Experiment 14: kustutatud tekstisõnad ja juhuslikult 42.3% lemmadest")


def deleted_lemmas(collection):

    lemmas = set()
    for i, text in collection.select(layers=['syntax_gold']):
        for span in text.syntax_gold:
            lemmas.add(span.lemma)

    del_lemmas = set()
    for lemma in lemmas:
        choice = np.random.choice([True, False], 1, p=[.423, .577])[0]
        if choice: del_lemmas.add(lemma)
    return del_lemmas
