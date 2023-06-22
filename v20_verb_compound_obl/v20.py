from estnltk.storage.postgres import LayerQuery

from datetime import datetime
# functions for creating database and collecting collocations
from collect_functions import *

from data_helpers.db_reader import DbReader

collection_name = 'koondkorpus_sentences'
BATCH_SIZE = 500000

#collection_name = 'koondkorpus_sentences_test_5000_sg_thread'
#BATCH_SIZE = 10

TYPE = 'verb_compound_obl'
TABLENAME = f'{TYPE}'

date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
db_file_name = f"v20_{collection_name}_{TYPE}_collocations_{date_time}.db"
my_sqlite_db = DbMethods(db_file_name=db_file_name, table1_name=TYPE, table2_name=TYPE+'_examples')
my_sqlite_db.prep_coll_db()


my_db_reader = DbReader(pgpass_file='~/.pgpass',\
                          schema='estonian_text_corpora',\
                          role='estonian_text_corpora_read',\
                          temporary=False,\
                          collection_name=collection_name)
my_db_reader.set_layers(['v172_stanza_syntax', 'v172_obl_phrases'])

# vaatame ainult neid lauseid, kus on mõni tegusõna ka
# NB! kas saab olla obl, kus ülemus ei ole tegusõna
additional_filters = [LayerQuery('morph_analysis', partofspeech='V')]
# sisaldab OBL fraasi
additional_filters.append(LayerQuery('v172_stanza_syntax', deprel='obl'))

collocations = {}
for collection_id, text in my_db_reader.get_collections(shuffle=False, queries=additional_filters, progressbar=None):
    collocations, = extract_something(text, collection_id, collocations )
    if not collection_id == 0 and not collection_id % BATCH_SIZE:
        my_sqlite_db.save_coll_to_db(collocations, collection_id)
        collocations = {}

# saving last batch
my_sqlite_db.save_coll_to_db(collocations, collection_id)
my_sqlite_db.index_fields()
