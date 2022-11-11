import os
from collections import OrderedDict
from random import Random

from estnltk import Layer
from estnltk.taggers.standard.syntax.syntax_dependency_retagger import SyntaxDependencyRetagger
from estnltk.taggers.standard.syntax.ud_validation.deprel_agreement_retagger import DeprelAgreementRetagger
from estnltk.taggers.standard.syntax.ud_validation.ud_validation_retagger import UDValidationRetagger
from estnltk.taggers import Tagger
from estnltk.converters.serialisation_modules import syntax_v0
from estnltk.downloader import get_resource_paths

from estnltk import Text

class StanzaSyntaxRetagger(Tagger):
    """
    This is a retagger that creates a new layer where the spans that have None values in 
    the stanza_syntax_without_entity layer will have a negative id and head based on the original stanza_syntax layer. 
    """
    
    conf_param = ['add_parent_and_children', 'syntax_dependency_retagger', 'input_type',  
                  'mark_syntax_error', 'mark_agreement_error', 'agreement_error_retagger', 'ud_validation_retagger' ]

    def __init__(self,
                 output_layer='stanza_syntax_with_entity',
                 sentences_layer='sentences',
                 words_layer='words',
                 input_morph_layer='morph_analysis',
                 stanza_syntax_layer = "stanza_syntax",
                 stanza_deprel_ignore_layer = "stanza_syntax_without_entity",
                 input_type='morph_extended',  # or 'morph_extended', 'sentences'
                 add_parent_and_children=False,
                 mark_syntax_error=False,
                 mark_agreement_error=False,
                 ):
        # Make an internal import to avoid explicit stanza dependency
        import stanza

        self.add_parent_and_children = add_parent_and_children
        self.mark_syntax_error = mark_syntax_error
        self.mark_agreement_error = mark_agreement_error
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc', "status")
        self.input_type = input_type

        self.syntax_dependency_retagger = None
        if add_parent_and_children:
            self.syntax_dependency_retagger = SyntaxDependencyRetagger(conll_syntax_layer=output_layer)
            self.output_attributes += ('parent_span', 'children')

        self.ud_validation_retagger = None
        if mark_syntax_error:
            self.ud_validation_retagger = UDValidationRetagger(output_layer=output_layer)
            self.output_attributes += ('syntax_error', 'error_message')

        self.agreement_error_retagger = None
        if mark_agreement_error:
            if not add_parent_and_children:
                raise ValueError('`add_parent_and_children` must be True for marking agreement errors.')
            else:
                self.agreement_error_retagger = DeprelAgreementRetagger(output_layer=output_layer)
                self.output_attributes += ('agreement_deprel',)

        if self.input_type not in ['sentences', 'morph_analysis', 'morph_extended', "stanza_syntax"]:
            raise ValueError('Invalid input type {}'.format(input_type))

        # Check for illegal parameter combinations (mismatching input type and layer):
        if input_type=='morph_analysis' and input_morph_layer=='morph_extended':
            raise ValueError( ('Invalid parameter combination: input_type={!r} and input_morph_layer={!r}. '+\
                              'Mismatching input type and layer.').format(input_type, input_morph_layer))
        elif input_type=='morph_extended' and input_morph_layer=='morph_analysis':
            raise ValueError( ('Invalid parameter combination: input_type={!r} and input_morph_layer={!r}. '+\
                              'Mismatching input type and layer.').format(input_type, input_morph_layer))

        if self.input_type == 'sentences':
            self.input_layers = [sentences_layer, words_layer]

        elif self.input_type in ['morph_analysis', 'morph_extended', "stanza_syntax"]:
            self.input_layers = [sentences_layer, input_morph_layer, words_layer, stanza_syntax_layer, stanza_deprel_ignore_layer]


    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      parent=self.input_layers[3],
                      ambiguous=False )
        if self.add_parent_and_children:
            layer.serialisation_module = syntax_v0.__version__
        return layer


    def _make_layer(self, text, layers, status=None):
        # Make an internal import to avoid explicit stanza dependency
        
        rand = Random()
        rand.seed(4)
        
        stanza_syntax_layer = layers[self.input_layers[3]]
        stanza_deprel_ignore_layer = layers[self.input_layers[4]]

        layer = self._make_layer_template()
        layer.text_object=text

        
        for i, span in enumerate(stanza_deprel_ignore_layer.spans):
            if span.id == None:
                new_span = list(stanza_syntax_layer.spans)[i]
                if 'feats' in stanza_syntax_layer.attributes:
                    feats = new_span['feats']
                
                attributes = {'id': -new_span.id, 'lemma': new_span['lemma'], 'upostag': new_span['upostag'], 'xpostag': new_span['xpostag'], 'feats': feats,
                                'head': -new_span['head'], 'deprel': new_span['deprel'], "status": "removed", 'deps': '_', 'misc': '_'}
                
                layer.add_annotation(new_span, **attributes)
            else:
                if 'feats' in stanza_deprel_ignore_layer.attributes:
                    feats = span['feats']
                
                attributes = {'id': span.id, 'lemma': span['lemma'], 'upostag': span['upostag'], 'xpostag': span['xpostag'], 'feats': feats,
                                'head': span['head'], 'deprel': span['deprel'], "status": "remained", 'deps': '_', 'misc': '_'}
                
                layer.add_annotation(span, **attributes)
        
        
        
    
        if self.add_parent_and_children:
            # Add 'parent_span' & 'children' to the syntax layer.
            #print(self.output_layer, layer)
            self.syntax_dependency_retagger.change_layer(text, {self.output_layer: layer})

        if self.mark_syntax_error:
            # Add 'syntax_error' & 'error_message' to the layer.
            self.ud_validation_retagger.change_layer(text, {self.output_layer: layer})

        if self.mark_agreement_error:
            # Add 'agreement_deprel' to the layer.
            self.agreement_error_retagger.change_layer(text, {self.output_layer: layer})

        return layer


def feats_to_ordereddict(feats_str):
    """
    Converts feats string to OrderedDict (as in MaltParserTagger and UDPipeTagger)
    """
    feats = OrderedDict()
    if feats_str == '_':
        return feats
    feature_pairs = feats_str.split('|')
    for feature_pair in feature_pairs:
        key, value = feature_pair.split('=')
        feats[key] = value
    return feats