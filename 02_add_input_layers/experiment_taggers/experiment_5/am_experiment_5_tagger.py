from estnltk import ElementaryBaseSpan, Annotation, Layer
from estnltk.taggers import Tagger, VabamorfTagger, MorphExtendedTagger, VislTagger
import re


class AMExperiment5Tagger(Tagger):

    def __init__(self,
                 output_layer='am_experiment_5',
                 input_layers=None,
                 output_attributes=None
                 ):
        if input_layers is None:
            input_layers = ['syntax_gold', 'words', 'sentences', 'compound_tokens']
        if output_attributes is None:
            output_attributes = ['id', 'form', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps',
                                 'misc']
        self.output_layer = output_layer
        self.input_layers = input_layers
        self.output_attributes = output_attributes
        self.conf_param = ['morph_analysis_tagger', 'morph_extended_tagger', 'visl_tagger', 'visl_lemmas']
        self.morph_analysis_tagger = VabamorfTagger()
        self.morph_extended_tagger = MorphExtendedTagger()
        self.visl_tagger = VislTagger()
        self.visl_lemmas = self.visl_lemmas()

    def _make_layer(self, text, layers, status=None):
        layer = Layer(self.output_layer, text_object=text, attributes=self.output_attributes)
        self.morph_analysis_tagger.tag(text)
        self.morph_extended_tagger.tag(text)
        self.visl_tagger.tag(text)

        for basespan, visl_span in zip(text[self.input_layers[0]], text.visl):
            new_span = ElementaryBaseSpan(basespan.start, basespan.end)
            subtype = visl_span.subtype[0][0] if type(visl_span.subtype[0]) == list else visl_span.subtype[0]
            mood = visl_span.mood[0][0] if type(visl_span.mood[0]) == list else visl_span.mood[0]
            tense = visl_span.tense[0][0] if type(visl_span.tense[0]) == list else visl_span.tense[0]
            voice = visl_span.voice[0][0] if type(visl_span.voice[0]) == list else visl_span.voice[0]
            person = visl_span.person[0][0] if type(visl_span.person[0]) == list else visl_span.person[0]
            number = visl_span.number[0][0] if type(visl_span.number[0]) == list else visl_span.number[0]
            case = visl_span.case[0][0] if type(visl_span.case[0]) == list else visl_span.case[0]
            polarity = visl_span.polarity[0][0] if type(visl_span.polarity[0]) == list else visl_span.polarity[0]
            number_format = visl_span.number_format[0][0] if type(visl_span.number_format[0]) == list else \
                visl_span.number_format[0]

            feats = '|'.join(
                [subtype, mood, tense, voice, person,
                 number, case, polarity, number_format])

            feats = re.sub('_', '', feats)
            feats = re.sub('\|+', '|', feats)
            feats = re.sub('\|$', '', feats)
            feats = '_' if feats == '' else feats
            lemma = 'XX' if basespan.lemma not in self.visl_lemmas else basespan.lemma

            attributes = {'id': basespan.id, 'form': 'XX', 'lemma': lemma,
                          'upostag': basespan.upostag, 'xpostag': basespan.xpostag,
                          'feats': feats, 'head': basespan.head,
                          'deprel': basespan.deprel, 'deps': '_', 'misc': '_'}

            annotation = Annotation(new_span, **attributes)
            layer.add_annotation(new_span, **annotation)

        return layer

    def __doc__(self):
        print("Experiment 5: kõik sõnavormid kustutatud + kustutatud kõik lemmad, mis ei esine CG reeglites.")

    def visl_lemmas(self):
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
