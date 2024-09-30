from datetime import datetime

# functions for creating database and collecting collocations
from collect_functions import extract_something, DbMethods

from data_helpers.db_reader import DbReader

collection_name = "koondkorpus_sentences"
BATCH_SIZE = 50000

# collection_name = 'koondkorpus_sentences_test_5000_sg_thread'
# BATCH_SIZE = 50000

TYPE = "verb_pattern_obl"
TABLENAME = f"{TYPE}"

date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
db_file_name = f"v31_{collection_name}_{TYPE}_{date_time}.db"
my_sqlite_db = DbMethods(
    db_file_name=db_file_name, table1_name=TYPE, table2_name=TYPE + "_examples"
)
my_sqlite_db.prep_coll_db()


my_db_reader = DbReader(
    pgpass_file="~/.pgpass",
    schema="estonian_text_corpora",
    role="estonian_text_corpora_read",
    temporary=False,
    collection_name=collection_name,
)
my_db_reader.set_layers(["v172_stanza_syntax"])

data = []
count = 0
for collection_id, text in my_db_reader.get_collections(
    shuffle=False, progressbar=None
):
    count += 1
    (collocations,) = extract_something(
        text=text, collection_id=collection_id, data=data
    )

    if not count == 0 and not count % BATCH_SIZE:
        my_sqlite_db.save_coll_to_db(data, collection_id)
        data = []


# saving last batch
my_sqlite_db.save_coll_to_db(data, collection_id)
my_sqlite_db.index_fields()

my_sqlite_db._connection.close()

print("done.")
