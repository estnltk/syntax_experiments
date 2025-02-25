import sqlite3
from estnltk.storage.postgres import LayerQuery
from datetime import datetime
from data_helpers.db_reader import DbReader
from data_helpers.syntax_graph import SyntaxGraph



TABLE_SQL = """
CREATE TABLE IF NOT EXISTS sentences (
    id INTEGER PRIMARY KEY, -- unikaalne ID
    text TEXT NOT NULL -- lause terviktekst
);
"""

INSERT_SQL = """
INSERT INTO sentences(id, text) VALUES(?,?)
"""

def save_batch(conn, data):
    conn.executemany(INSERT_SQL, data)
    conn.commit()
    
collection_name = 'koondkorpus_sentences'
BATCH_SIZE = 50000

date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
db_file_name = f"v33_{collection_name}_sentences_{date_time}.db"

conn = sqlite3.connect(db_file_name)
cursor = conn.cursor()

# Create table if not exists
cursor.execute(TABLE_SQL)
conn.commit()

my_db_reader = DbReader(pgpass_file='~/.pgpass',\
                          schema='estonian_text_corpora',\
                          role='estonian_text_corpora_read',\
                          temporary=False,\
                          collection_name=collection_name)
my_db_reader.set_layers(['v172_stanza_syntax'])




data = []
for collection_id, text in my_db_reader.get_collections(shuffle=False, progressbar='ascii'):
    # 1. make stanza syntax graph
    graph = SyntaxGraph(text["v172_stanza_syntax"])

    # matrix for node distances
    dpath = graph.get_distances_matrix()
    verb_nodes = graph.get_nodes_by_attributes(attrname="pos", attrvalue="V")
    add = 0
    for verb in verb_nodes:
        # do skip collocation if verb is "unusual"
        if not graph.is_verb_normal(verb):
            continue
        add = 1
        
    if add:
        data.append((collection_id, text.text,))

    if len(data) and len(data) % BATCH_SIZE == 0:
        print('saving', collection_id)
        save_batch(conn, data)
        data = []
        conn.commit()
        
if len(data):
    print('saving last batch ---', collection_id)
    save_batch(conn, data)
    conn.commit()
    data = []
conn.close()