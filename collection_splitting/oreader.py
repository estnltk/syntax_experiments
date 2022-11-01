
from estnltk.storage.postgres import PostgresStorage
#import sys
import networkx as nx
from scripts.sentence import Sentence
from scripts.reader import Reader
import os
from scripts.read_config import read_config
from estnltk import Text

class oReader(Reader):

    __stanza_layer = None

    def __init__(self, stanza_layer, ):
        super().__init__()
        self.__stanza_layer = stanza_layer
        
        
    def get_sentences_generator(self, mode='graph'):

        if mode not in ['graph', 'text']:
            raise Exception("Unknown mode %s", mode)
        word_id = 0
        sentences_counter = 0
        start = None
        text_sentences_counter = 0

        analysed = Text(" ".join(self.__stanza_layer.text)).tag_layer(['sentences','morph_extended'])
        sentences_start = [span.start for span in analysed.sentences]
        sentences_end = [span.end for span in analysed.sentences]
        #print(sentences_end)
        for span in self.__stanza_layer.spans:
            #print(span, "\n", span.start, span.end)
            word_id +=1
            #lause algus
            if span.start in sentences_start:
                #print("START")
                start = span.start
                current_sentence = []
                word_id +=1
                #G = sentence.Sentence()
                G = Sentence()


            G.add_node(span.id, id=span.id, lemma=span.lemma, form=span.text.replace('\n',''), 
                       pos=span.upostag, deprel=span.deprel, feats='|||'.join(span.feats.keys()))
            G.add_edge(span.head, span.id, deprel = span.deprel)
            
            current_sentence.append(span)
            
            #lause lõpp
            if span.end in sentences_end or span.end+1 in sentences_end:
                current_sentence_text = ' '.join([s.text for s in current_sentence])
                #print (current_sentence_text)
                #print (str(G.nodes))
                sentences_counter += 1
                text_sentences_counter +=1
                global_sent_id = f'{text_sentences_counter}_{start}'
                
                #print(global_sent_id, G, current_sentence_text)
                if mode == 'graph':
                    yield global_sent_id, G
                else:
                    yield global_sent_id, current_sentence_text

