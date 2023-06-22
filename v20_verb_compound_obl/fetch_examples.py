import pandas as pd
import json
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

# takes ca 2 mins
collection_name = 'koondkorpus_sentences'

my_db_reader = DbReader(
    pgpass_file='~/.pgpass',
    schema='estonian_text_corpora',
    role='estonian_text_corpora_read',
    temporary=False,
    collection_name=collection_name
)

INPUT_FILE = '20230616-230803_base_for_example_sentence_ids.csv'
df_final = pd.read_csv(INPUT_FILE)
df_final.astype({'compound_ids': 'str'}).dtypes
df_final = df_final.fillna('')
df_final['verb_span'] = ''
df_final['obl_span'] = ''
df_final['obl_lemma'] = ''
df_final['sentence'] = ''


print(df_final.shape)

# Fetching from database
sentence_ids = [int(sent_id) for sent_id in list(df_final['sentence_id'].unique())]
uniq_sentences_total = len(sentence_ids)
print(f'sentences to fetch: {uniq_sentences_total}')


my_db_reader.set_layers(['v172_stanza_syntax'])

BATCH = 1000 # batch for reading sentences

first = 0
all_sentence_ids = df_final['sentence_id'].tolist()
all_sentence_ids = [int(sent_id) for sent_id in all_sentence_ids]

for batch_nr in range(round(df_final.shape[0]/BATCH)):
    date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    print(f'{date_time} fetching batch {batch_nr}')
    first = batch_nr * BATCH
    last = first + BATCH
    #print(first, last, batch_nr)
    if last > df_final.shape[0]:
        last = df_final.shape[0]
    

    batch_sentence_ids = all_sentence_ids[first:last]
    
    batch_sentences = {}
    for collection_id, text in my_db_reader.get_collections(shuffle=False, progressbar='ascii', col_ids=batch_sentence_ids):
        batch_sentences[collection_id] = text
    
    for row_nr in range(first, last):
        
        sentence_id = df_final['sentence_id'][row_nr]
        verb_id = int(df_final['verb_id'][row_nr])
        obl_root = int(df_final['root_id'][row_nr])

        compound_ids = [int(n) for n in df_final['compound_ids'][row_nr].split(',') if n.isdigit()]
        obl_ids = [int(n) for n in df_final['obl_ids'][row_nr].split(',') if n.isdigit()]
        text = batch_sentences[sentence_id].text

        g = SyntaxGraph(batch_sentences[sentence_id]['v172_stanza_syntax'])

        df_final.loc[row_nr, 'obl_lemma'] = g.nodes[obl_root]['lemma']

        # g.draw_graph(highlight=[verb_id])

        df_final.loc[row_nr, 'sentence'] = str(text)
        # print(collection_id, text)

        df_final.loc[row_nr, 'verb_span'] = json.dumps(get_span(g, [verb_id], 'V'), ensure_ascii=False)
        df_final.loc[row_nr, 'obl_span'] = json.dumps(get_span(g, [obl_root], 'OBL'), ensure_ascii=False)
        df_final.loc[row_nr, 'compound_spans'] = json.dumps(get_spans(g, compound_ids, 'COMPOUND'), ensure_ascii=False)
        df_final.loc[row_nr, 'oblp_spans'] = json.dumps(get_spans(g, obl_ids, 'OBLP'), ensure_ascii=False)
    date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    print(f'{date_time} saving result {first}, {last}')
    df_final.to_csv(f'FINAL{INPUT_FILE}', index=False)