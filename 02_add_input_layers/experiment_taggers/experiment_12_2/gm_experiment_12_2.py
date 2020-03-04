import pickle

from estnltk import ElementaryBaseSpan, Annotation, Layer
from estnltk.taggers import Tagger


class GMExperiment12_2Tagger(Tagger):
    def __init__(self,
                 output_layer='gm_experiment_12_2',
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
        self.conf_param = ('lemmas_to_keep')
        self.lemmas_to_keep = lemmas_to_keep()

    def _make_layer(self, text, layers, status=None):
        layer = Layer(self.output_layer, text_object=text, attributes=self.output_attributes)

        for basespan in text[self.input_layers[0]]:
            new_span = ElementaryBaseSpan(basespan.start, basespan.end)

            attributes = {'id': basespan.id, 'form': 'XX',
                          'lemma': 'XX' if basespan.lemma not in self.lemmas_to_keep else basespan.lemma,
                          'upostag': basespan.upostag, 'xpostag': basespan.xpostag, 'feats': basespan.feats,
                          'head': basespan.head,
                          'deprel': basespan.deprel, 'deps': '_', 'misc': '_'}
            annotation = Annotation(new_span, **attributes)
            layer.add_annotation(new_span, **annotation)

        return layer

    def __doc__(self):
        print("Experiment 12_2 : kustutatud tekstisõnad ja teatud lemmad (difficult constructions)")


def lemmas_to_keep():
    verbs = pickle.load(open("verbs_to_keep_for_subj_obj.pickle", "rb"))
    vpart_verbs = pickle.load(open("vpart_verbs.pickle", "rb"))
    vpart_adverbs = pickle.load(open("vpart_adverbs.pickle", "rb"))
    lemmas_to_keep = frozenset(verbs + vpart_verbs + vpart_adverbs)
    return lemmas_to_keep
