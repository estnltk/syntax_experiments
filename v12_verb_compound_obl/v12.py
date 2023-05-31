from estnltk.storage.postgres import LayerQuery


from datetime import datetime
from collect_functions import *

from data_helpers.db_reader import DbReader

collection_name = 'koondkorpus_sentences'
# collection_name = 'koondkorpus_sentences_test_5000_sg_thread'  #

TYPE = 'verb_compound_obl'
TABLENAME = f'{TYPE}'
BATCH_SIZE = 500000

date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
db_file_name = f"v12_{collection_name}_{TYPE}_collocations_{date_time}.db"
my_sqlite_db = DbMethods(db_file_name=db_file_name, table1_name=TYPE, table2_name=TYPE+'_examples')
my_sqlite_db.prep_coll_db()


my_db_reader = DbReader(
    pgpass_file='~/.pgpass',
    schema='estonian_text_corpora',
    role='estonian_text_corpora_read',
    temporary=False,
    collection_name=collection_name
)
my_db_reader.set_layers(['v171_named_entities', 'v172_stanza_syntax', 'v172_obl_phrases', 'v172_pre_timexes'])

# vaatame ainult neid lauseid, kus on mõni tegusõna ka
# NB! kas saab olla obl, kus ülemus ei ole tegusõna
additional_filters = [LayerQuery('morph_analysis', partofspeech='V')]
collocations = {}
for collection_id, text in my_db_reader.get_collections(shuffle=False, queries=additional_filters, progressbar=None):
    collocations, = extract_something(text, collection_id, collocations)
    if not collection_id == 0 and not collection_id % BATCH_SIZE:
        my_sqlite_db.save_coll_to_db(collocations, collection_id)
        collocations = {}

# saving last batch
my_sqlite_db.save_coll_to_db(collocations, collection_id)
my_sqlite_db.index_fields()
