
from estnltk.storage.postgres import PostgresStorage
#import sys
import networkx as nx
from .. sentence import sentence
from .. reader import reader


class Reader(reader.Reader):

    __collection = None

    def __init__(self, pgpass_file, schema,role, temporary, collectionName, ):
        super().__init__()
        storage = PostgresStorage(pgpass_file=pgpass_file,
                                  schema=schema,
                                  role=role,
                                  temporary=temporary)

        self.__collection = storage[collectionName]

    def get_sentences_generator(self, mode='graph'):

        if mode not in ['graph', 'text']:
            raise Exception("Unknown mode %s", mode)
        word_id = 0
        sentences_counter = 0
        start = None
        text_sentences_counter = 0

        for (colId, text) in self.__collection.select ( progressbar="ascii", layers=['v166_sentences', 'v168_stanza_ensemble_syntax'], return_index=True ):
            sentences_start = [span.start for span in text.v166_sentences]
            sentences_end = [span.end for span in text.v166_sentences]

            for span in text.v168_stanza_ensemble_syntax:
                word_id +=1
                #lause algus
                if span.start in sentences_start:
                    start = span.start
                    current_sentence = []
                    word_id +=1
                    G = sentence.Sentence()


                G.add_node(span.id, id=span.id, lemma=span.lemma, form=span.text.replace('\n',''), pos=span.upostag, deprel=span.deprel, feats='|||'.join(span.feats.keys()))
                G.add_edge(span.head, span.id, deprel = span.deprel)

                current_sentence.append(span)
                #lause lõpp
                if span.end in sentences_end:
                    current_sentence_text = ' '.join([s.text for s in current_sentence])
                    #print (current_sentence_text)
                    #print (str(G.nodes))
                    sentences_counter += 1
                    text_sentences_counter +=1
                    global_sent_id = f'{colId}_{text_sentences_counter}_{start}'
                    if mode == 'graph':
                        yield global_sent_id, G
                    else:
                        yield global_sent_id, current_sentence_text
