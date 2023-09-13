import pandas as pd
import json
import os
import re
from datetime import datetime

from data_helpers.syntax_graph import SyntaxGraph
from data_helpers.db_reader import DbReader


def get_span(graph, nodes, label):
    spans = get_spans(graph, nodes, label)
    if len(spans) == 1:
        return spans[0]
    return spans


def get_spans(graph, nodes, label):
    spans = []
    for n in nodes:
        spans.append({
            'start': graph.nodes[n]['start'],
            'end': graph.nodes[n]['end'],
            'text': graph.nodes[n]['form'],
            'labels': [label]})
    
    return spans

def get_first(string, sep=','):
    if not string: return string
    return string.split(sep)[0]

def get_last(string, sep=','):
    if not string: return string
    return string.split(sep)[-1]


# init db
# takes ca 2 mins
collection_name = 'koondkorpus_sentences'
#collection_name = 'koondkorpus_sentences_test_5000_sg_thread'

my_db_reader = DbReader(
    pgpass_file='~/.pgpass',
    schema='estonian_text_corpora',
    role='estonian_text_corpora_read',
    temporary=False,
    collection_name=collection_name
)

# collect files
datestamp = '20230824-103951'
directory = 'result/'
files = []
# get all files inside a specific folder
for path in os.scandir(directory):
    if path.is_file() and re.match(r'^' + datestamp + '_sentence_ids_for_[a-z_]+.csv$', path.name):
        print(path.name)
        files.append(path.name)
print(len(files))


for f in files:
    print(datetime.now().strftime("%Y%m%d-%H%M%S"), 'Start', directory+f)
    df_final = pd.read_csv(directory+f, dtype = {'compound_ids': str})
    
    df_final['verb_span'] = ''
    
    df_final['obl_case1'] = df_final['cases_list'].apply(get_first)
    df_final['obl_case2'] = df_final['cases_list'].apply(get_last)
    df_final['obl_root1'] = df_final['oblroot_list'].apply(get_first)
    df_final['obl_root2'] = df_final['oblroot_list'].apply(get_last)
    df_final['obl_ids1'] = df_final['oblids_list'].apply(get_first, ':')
    df_final['obl_ids2'] = df_final['oblids_list'].apply(get_last, ':')
    
    df_final['obl_span1'] = ''
    df_final['obl_span2'] = ''
    df_final['obl_lemma2'] = ''
    df_final['obl_lemma1'] = ''
    df_final['sentence'] = ''
    df_final['oblp_spans1'] = ''
    df_final['oblp_spans2'] = ''
    df_final = df_final.fillna('')
    
    # Fetching from database
    sentence_ids = [int(sent_id) for sent_id in list(df_final['sentence_id'].unique())]
    uniq_sentences_total = len(sentence_ids)
    print(f'sentences to fetch: {uniq_sentences_total}')


    my_db_reader.set_layers(['v172_stanza_syntax'])

    BATCH = 100 # batch for reading sentences

    first = 0
    all_sentence_ids = df_final['sentence_id'].tolist()
    all_sentence_ids = [int(sent_id) for sent_id in all_sentence_ids]

   
    for batch_nr in range(round(df_final.shape[0]/BATCH)+1):
       
        date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        print(f'{date_time} fetching batch {batch_nr}')
        first = batch_nr * BATCH
        last = first + BATCH
        
        if last > df_final.shape[0]:
            last = df_final.shape[0]

        # print(first, last, batch_nr)
        batch_sentence_ids = all_sentence_ids[first:last]

        batch_sentences = {}
        
        print('sentences in batch', len(batch_sentence_ids))
        if not len(batch_sentence_ids): break
        for collection_id, text in my_db_reader.get_collections(shuffle=False, progressbar=None, col_ids=batch_sentence_ids):
            batch_sentences[collection_id] = text

        for row_nr in range(first, last):

            sentence_id = df_final['sentence_id'][row_nr]
            verb_id = int(df_final['verb_id'][row_nr])
            obl_root1 = int(df_final['obl_root1'][row_nr])
            obl_root2 = int(df_final['obl_root2'][row_nr])
            compound_ids = [int(n) for n in df_final['compound_ids'][row_nr].split(',') if n.isdigit()]
            obl_ids1 = [int(n) for n in df_final['obl_ids1'][row_nr].split(',') if n.isdigit()]
            obl_ids2 = [int(n) for n in df_final['obl_ids2'][row_nr].split(',') if n.isdigit()]
            text = batch_sentences[sentence_id].text

            g = SyntaxGraph(batch_sentences[sentence_id]['v172_stanza_syntax'])

            df_final.loc[row_nr, 'obl_lemma1'] = g.nodes[obl_root1]['lemma']
            df_final.loc[row_nr, 'obl_lemma2'] = g.nodes[obl_root2]['lemma']

            # g.draw_graph(highlight=[verb_id])

            df_final.loc[row_nr, 'sentence'] = str(text)
            # print(collection_id, text)

            df_final.loc[row_nr, 'verb_span'] = json.dumps(get_span(g, [verb_id], 'V'), ensure_ascii=False)
            df_final.loc[row_nr, 'obl_span1'] = json.dumps(get_span(g, [obl_root1], 'OBL'), ensure_ascii=False)
            df_final.loc[row_nr, 'obl_span2'] = json.dumps(get_span(g, [obl_root2], 'OBL'), ensure_ascii=False)
            
            df_final.loc[row_nr, 'compound_spans'] = json.dumps(get_spans(g, compound_ids, 'COMPOUND'), ensure_ascii=False)
            df_final.loc[row_nr, 'oblp_spans1'] = json.dumps(get_spans(g, obl_ids1, 'OBLP'), ensure_ascii=False)
            df_final.loc[row_nr, 'oblp_spans2'] = json.dumps(get_spans(g, obl_ids2, 'OBLP'), ensure_ascii=False)
        date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        print(f'{date_time} fetched anf modified result {first}, {last}')
    date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    outputfile = f.replace('sentence_ids', 'sentences')
    print(f'{date_time} saving result for {outputfile}')
    df_final.to_csv(directory+outputfile, index=False)

print('done.')
