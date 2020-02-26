from estnltk import ElementaryBaseSpan, Annotation, Layer
from estnltk.taggers import Tagger


class AMExperiment9Tagger(Tagger):
    def __init__(self,
                 output_layer='am_experiment_9',
                 input_layers=None,
                 output_attributes=None
                 ):
        if output_attributes is None:
            output_attributes = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                                 'misc']
        if input_layers is None:
            input_layers = ['syntax_gold', 'words', 'sentences', 'compound_tokens']
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = output_attributes
        self.conf_param = ()

    def _make_layer(self, text, layers, status=None):
        layer = Layer(self.output_layer, text_object=text, attributes=self.output_attributes)

        for basespan in text[self.input_layers[0]]:
            new_span = ElementaryBaseSpan(basespan.start, basespan.end)

            attributes = {'id': basespan.id, 'form': 'XX', 'lemma': 'XX',
                          'upostag': 'XX', 'xpostag': basespan.xpostag, 'feats': 'XX', 'head': basespan.head,
                          'deprel': basespan.deprel, 'deps': '_', 'misc': '_'}
            annotation = Annotation(new_span, **attributes)
            layer.add_annotation(new_span, **annotation)

        return layer

    def __doc__(self):
        print("Experiment 9: alles ainult postagid jm sünt märgendid")
