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

from scripts.syntax_tree import SyntaxTree 
from scripts.syntax_tree_operations import *
import networkx as nx



class StanzaSyntaxIgnoreDeprelTagger(Tagger):
    """
    This is a deprel ignore tagger applied to stanza_syntax layer that creates a new layer 
    from the spans that should be removed if words with given deprels are removed.
    """
    
    conf_param = ['model_path', 'add_parent_and_children', 'syntax_dependency_retagger',
                  'input_type', 'dir', 'mark_syntax_error', 'mark_agreement_error', 'agreement_error_retagger',
                  'ud_validation_retagger', 'use_gpu', 'nlp', "deprel"]

    def __init__(self,
                 output_layer='stanza_syntax_ignore_deprel',
                 sentences_layer='sentences',
                 words_layer='words',
                 input_morph_layer='morph_analysis',
                 input_stanza_syntax_layer = "stanza_syntax",
                 input_type='stanza_syntax',  # or 'morph_extended', 'sentences'
                 add_parent_and_children=False,
                 depparse_path=None,
                 resources_path=None,
                 mark_syntax_error=False,
                 mark_agreement_error=False,
                 use_gpu=False,
                 deprel = None,
                 ):
        # Make an internal import to avoid explicit stanza dependency
        import stanza

        self.add_parent_and_children = add_parent_and_children
        self.mark_syntax_error = mark_syntax_error
        self.mark_agreement_error = mark_agreement_error
        self.deprel = deprel
        self.output_layer = output_layer
        self.output_attributes = ('id', 'lemma', 'upostag', 'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc', "status")
        self.input_type = input_type
        self.use_gpu = use_gpu
        self.deprel = deprel 

        if not resources_path:
            # Try to get the resources path for stanzasyntaxtagger. Attempt to download resources, if missing
            self.dir = get_resource_paths("stanzasyntaxtagger", only_latest=True, download_missing=True)
        else:
            self.dir = resources_path
        # Check that resources path has been set
        if self.dir is None:
            raise Exception('Models of StanzaSyntaxTagger are missing. '+\
                            'Please use estnltk.download("stanzasyntaxtagger") to download the models.')

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

        if depparse_path and not os.path.isfile(depparse_path):
            raise ValueError('Invalid path: {}'.format(depparse_path))
        elif depparse_path and os.path.isfile(depparse_path):
            self.model_path = depparse_path
        else:
            if input_type == 'morph_analysis':
                self.model_path = os.path.join(self.dir, 'et', 'depparse', 'morph_analysis.pt')
            if input_type == 'morph_extended' or input_type == "stanza_syntax":
                self.model_path = os.path.join(self.dir, 'et', 'depparse', 'morph_extended.pt')
            if input_type == 'sentences':
                self.model_path = os.path.join(self.dir, 'et', 'depparse', 'stanza_depparse.pt')

        if not os.path.isfile(self.model_path):
            raise FileNotFoundError('Necessary models missing, download from https://entu.keeleressursid.ee/public-document/entity-9791 '
                             'and extract folders `depparse` and `pretrain` to root directory defining '
                             'StanzaSyntaxTagger under the subdirectory `stanza_resources/et (or set )`')

        if input_type == 'sentences':
            if not os.path.isfile(os.path.join(self.dir, 'et', 'pretrain', 'edt.pt')):
                raise FileNotFoundError(
                    'Necessary pretrain model missing, download from https://entu.keeleressursid.ee/public-document/entity-9791 '
                    'and extract folder `pretrain` to root directory defining '
                    'StanzaSyntaxTagger under the subdirectory `stanza_resources/et`')

        if self.input_type == 'sentences':
            self.input_layers = [sentences_layer, words_layer]
            self.nlp = stanza.Pipeline(lang='et', processors='tokenize,pos,lemma,depparse',
                                       dir=self.dir,
                                       tokenize_pretokenized=True,
                                       depparse_model_path=self.model_path,
                                       use_gpu=self.use_gpu,
                                       logging_level='WARN')  # Logging level chosen so it does not display
            # information about downloading model

        elif self.input_type in ['morph_analysis', 'morph_extended', "stanza_syntax"]:
            self.input_layers = [sentences_layer, input_morph_layer, words_layer, input_stanza_syntax_layer]
            self.nlp = stanza.Pipeline(lang='et', processors='depparse',
                                       dir=self.dir,
                                       depparse_pretagged=True,
                                       depparse_model_path=self.model_path,
                                       use_gpu=self.use_gpu,
                                       logging_level='WARN')
            
            

    def _make_layer_template(self):
        """Creates and returns a template of the layer."""
        #print(self.output_layer)
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
        from stanza.models.common.doc import Document
        
        rand = Random()
        rand.seed(4)
        
        input_stanza_syntax_layer = layers[self.input_layers[3]]
        
        layer = self._make_layer_template()
        layer.text_object=text
                
        if "stanza_syntax" not in text.layers:
            raise SystemExit('Text object is missing stanza_syntax layer.')
        if len(text.sentences) > 1:
            raise SystemExit('Input consist of more than 1 sentence.')
               
        # create syntax tree
        syntaxtree = SyntaxTree.make_graph_from_layer(input_stanza_syntax_layer)
        
        # remove deprel with children 
        tree_short = remove_deprel(syntaxtree, [self.deprel])
        
        #removed nodes' id-s
        nodes_diff = get_nodes_diff(syntaxtree, tree_short)

        # nodes that are after the removed nodes but remained (for fixing spans)
        if nodes_diff:                       
            # add spans that were removed and have to have the original data
            for span in input_stanza_syntax_layer:
                
                orig_id = span["id"] 
                if orig_id in nodes_diff:
                    id = orig_id 
                    status = "removed"
                    lemma = span['lemma'] 
                    upostag = span['upostag'] 
                    xpostag = span['xpostag'] 
                    feats = OrderedDict()  # Stays this way if word has no features.
                    if 'feats' in input_stanza_syntax_layer.attributes:
                        feats = span['feats']
                    head = span['head'] 
                    deprel = span['deprel']
                    
                    attributes = {'id': id, 'lemma': lemma, 'upostag': upostag, 'xpostag': xpostag, 'feats': feats,
                              'head': head, 'deprel': deprel, "status": status, 'deps': '_', 'misc': '_'}
                    
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