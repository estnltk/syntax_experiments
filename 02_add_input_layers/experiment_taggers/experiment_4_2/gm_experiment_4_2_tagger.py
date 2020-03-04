from estnltk import ElementaryBaseSpan, Annotation, Layer
from estnltk.taggers import Tagger


class GMExperiment4_2Tagger(Tagger):
    def __init__(self,
                 output_layer='gm_experiment_4_2',
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
            lemma = 'XX' if basespan.upostag in ('V', 'K', 'VERB', 'ADP') else basespan.lemma

            attributes = {'id': basespan.id, 'form': 'XX', 'lemma': lemma,
                          'upostag': basespan.upostag, 'xpostag': basespan.xpostag,
                          'feats': basespan.feats, 'head': basespan.head,
                          'deprel': basespan.deprel, 'deps': '_', 'misc': '_'}

            annotation = Annotation(new_span, **attributes)
            layer.add_annotation(new_span, **annotation)

        return layer

    def __doc__(self):
        print("Experiment 4_2: kõik sõnavormid kustutatud + verbide ja kaassõnade lemmad kustutatud")
