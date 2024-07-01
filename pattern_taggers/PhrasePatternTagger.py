# - imports
#import sys
#sys.path.append("./helper_methods/")

from pattern_taggers.helper_methods.ner_and_pos_methods import get_ner, get_POS
from estnltk import Text
from estnltk import Layer
from estnltk.taggers import Tagger
from collections import defaultdict
import copy
import csv


class PhrasePatternTagger(Tagger):
    """Tags phrases that match given syntax, part-of-speech and ner pattern rules, and their corresponding patterns.""" 
    
    conf_param = ['rules_file', 'ruleset_map']
    
    def __init__(self, rules_file: str,
                       output_layer='phrase_patterns',
                       morph_analysis_layer='morph_analysis',
                       words_layer='words',
                       syntax_layer='stanza_syntax',
                       ner_layer='ner'):
        
        self.input_layers = [morph_analysis_layer, words_layer, syntax_layer, ner_layer]
        self.output_layer = output_layer
        self.output_attributes = ['extraction_pattern', 'ner_pattern', 'pattern_id', 'score', 'phrase_pattern_id', 'phrase_class']
        self.rules_file = rules_file

        ruleset_map = defaultdict(list)
        
        with open(rules_file, encoding='UTF-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                pieces = [wrd.split() for wrd in row['tree'].split(',')]
                syntax_tree = ''
                if len(pieces) > 1:
                    for piece in pieces:
                        if piece[2] == 'root':
                            piece[2] = '*'
                    for i in range(len(pieces)):
                        pieces[i] = ' '.join(pieces[i])
                    syntax_tree = ','.join(pieces)
                    
                info = [row['ID'], row['POS_pattern'], row['NER_pattern']]
                ruleset_map[syntax_tree].append(info)
                
        self.ruleset_map = ruleset_map

    def _make_layer_template(self):
        layer = Layer(name=self.output_layer,
                      text_object=None,
                      attributes=self.output_attributes,
                      enveloping=self.input_layers[1],
                      ambiguous=True)
        return layer
        
    def _make_layer(self, text, layers, status):
        layer = self._make_layer_template()
        layer.text_object = text
        
        for i in range(len(layers[self.input_layers[2]])): # Iterate over 'stanza_syntax' layer
            pattern_spans = []    
            ids = []

            pattern_spans.append(layers[self.input_layers[2]][i])
            ids.append([layers[self.input_layers[2]][i]['id'], layers[self.input_layers[2]][i]['head']])
                
            for j in range(i + 1, len(layers[self.input_layers[2]])):
                tree = []
                pos = []
                ner = []
                for k in range(len(pattern_spans)):
                    if layers[self.input_layers[2]][j] not in pattern_spans:
                        if layers[self.input_layers[2]][j] in pattern_spans[k]['children'] or pattern_spans[k] in layers[self.input_layers[2]][j]['children'] or layers[self.input_layers[2]][j]['parent_span'] != None and layers[self.input_layers[2]][j]['parent_span'] == pattern_spans[k]['parent_span']:
                            pattern_spans.append(layers[self.input_layers[2]][j])
                            ids.append([layers[self.input_layers[2]][j]['id'], layers[self.input_layers[2]][j]['head']])
                
                # fixing word and head ID values
                ids_for_pattern = copy.deepcopy(ids)
                for k in range(len(ids_for_pattern)):
                    temp = ids_for_pattern[k][0]
                    ids_for_pattern[k][0] = k+1
                    for l in range(len(ids)):
                        if ids[l][1] == temp:
                            ids_for_pattern[l][1] = ids_for_pattern[k][0]
            
                word_ids = [word_id[0] for word_id in ids_for_pattern]
                for k in range(len(ids_for_pattern)):
                    if ids_for_pattern[k][0] == ids_for_pattern[k][1]:
                        ids_for_pattern[k][1] = 0
                    elif ids_for_pattern[k][1] not in word_ids:
                        ids_for_pattern[k][1] = 0
                
                # finding the root of current pattern and setting its deprel value as wildcard symbol "*"
                for k in range(len(pattern_spans)):
                    deprel = pattern_spans[k].deprel
                    if ids_for_pattern[k][1] == 0:
                        deprel = '*'
                    tree.append([str(ids_for_pattern[k][0]), str(ids_for_pattern[k][1]), deprel])
                    # POS-tag is taken from morph_analysis layer
                    pos.append(get_POS(layers[self.input_layers[1]], pattern_spans[k]))
                    # nertag is taken from ner layer
                    ner.append(get_ner(layers[self.input_layers[-1]], layers[self.input_layers[1]], pattern_spans[k]))                     
                    
                pattern = [" ".join(word_info) for word_info in tree]
                # check if tree pattern exists in ruleset map
                if ",".join(pattern) in self.ruleset_map.keys():
                    pos_pattern = "-".join(pos)
                    ner_pattern = "-".join(ner)
                    # check if POS-sequence and NER-sequence exist in ruleset map with given tree pattern
                    for el in self.ruleset_map[",".join(pattern)]:
                        if el[1] == pos_pattern and el[2] == ner_pattern:
                            # add annotation
                            layer.add_annotation([span.base_span for span in pattern_spans], 
                                                 extraction_pattern=",".join([",".join(pattern), pos_pattern]),
                                                 ner_pattern=ner_pattern,
                                                 pattern_id=el[0],
                                                 score=None,
                                                 phrase_pattern_id=None,
                                                 phrase_class=None)     
                
        return layer