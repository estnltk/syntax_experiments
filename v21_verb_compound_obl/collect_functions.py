import sys
import sqlite3
from data_helpers.utils import ListUtils
from data_helpers.syntax_graph import SyntaxGraph


class DbMethods:
    """
    Class for creating and storing data in sqlite database
    """
    _cursor = None
    _connection = None

    _DB_NAME = None
    _TABLE1_NAME = None
    _TABLE2_NAME = None

    key_fields = (
        'verb',
        'verb_compound',
        'obl_root',
        'obl_root_compound',
        'obl_case',
      )

    def __init__(self, db_file_name, table1_name, table2_name):
        self._TABLE1_NAME = table1_name
        self._TABLE2_NAME = table2_name
        self._DB_NAME = db_file_name
        self._connection = sqlite3.connect(db_file_name)  #
        self._cursor = self._connection.cursor()

    """
     functions to save script specific data to sqlite data tables
    """
    def prep_coll_db(self, do_truncate=True):
        self._cursor.execute(f"""CREATE TABLE IF NOT EXISTS collections_processed
                        (tablename text, lastcollection integer);
                        """)

        self._cursor.execute(f"""
        CREATE UNIQUE INDEX IF NOT EXISTS collections_processed_uniq ON collections_processed(tablename);
      """)

        # tsv failist lugemise korral loome tabeli alati nullist
        self._cursor.execute(f"""
          INSERT INTO collections_processed VALUES (?,?)
          ON CONFLICT(tablename) DO UPDATE SET lastcollection=?;""", (self._TABLE1_NAME, 0, 0,))

        self._cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self._TABLE1_NAME}
                        (`id` INTEGER PRIMARY KEY AUTOINCREMENT
                        , `verb` text
                        , `verb_compound` text
                        , `obl_root` text
                        , `obl_root_compound` text
                        , `obl_case` text
                        , `count` int
                        );
                       """)

        # add uniq_index on all fields beside id and total
        INDEXNAME = f'{self._TABLE1_NAME}_unique'
        self._cursor.execute(f"""CREATE UNIQUE INDEX IF NOT EXISTS {INDEXNAME}
          ON {self._TABLE1_NAME}(
                `verb`
                , `verb_compound` 
                , `obl_root` 
                , `obl_root_compound` 
                , `obl_case` 
              );
          """)
        # loome näidete faili
        self._cursor.execute(f"""CREATE TABLE {self._TABLE2_NAME}
                        (row_id integer
                        , sentence_id integer
                        , root_id integer
                        , verb_id integer
                        , compound_ids text
                        , obl_ids text
                        , clauses_count int);
                        """)

        # tsv failist lugemise korral loome tabeli alati nullist
        self._cursor.execute(f"""DELETE FROM {self._TABLE1_NAME};""")

        INDEXNAME = f'{self._TABLE1_NAME}_unique'
        self._cursor.execute(f"""CREATE UNIQUE INDEX IF NOT EXISTS {INDEXNAME}_examples
          ON {self._TABLE2_NAME}(
              row_id, sentence_id, root_id
              );
          """)

        if do_truncate:
            self._cursor.execute(f"DELETE FROM {self._TABLE1_NAME} WHERE 1;")

        self._connection.commit()

    def save_coll_to_db(self, collocations, lastcollection):
        sql_colls = []
        sql_examples = []
        for key in collocations.keys():
            sql_colls.append((key[0],  # verb
                              key[1],  # verb_compound
                              key[2],  # obl_root
                              key[3],  # obl_root_compound
                              key[4],  # obl_case
                              collocations[key]['total']  # count
                              ))

            for example in collocations[key]['examples']:
                sql_examples.append((
                    key[0],  # verb
                    key[1],  # verb_compound
                    key[2],  # obl_root
                    key[3],  # obl_root_compound
                    key[4],  # obl_case
                    example[0],  # sentence_id
                    example[1],  # root_id
                    example[2],  # verb_id
                    ','.join(example[3]),  # compound_ids tuple
                    ','.join(example[4]),  # obl_ids tuple
                    example[5], # clauses_count int
                ))

        self._cursor.executemany(f"""
        INSERT INTO {self._TABLE1_NAME} (
            verb
            , verb_compound
            , obl_root
            , obl_root_compound
            , obl_case
            , count )

            VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(`verb`
                , `verb_compound` 
                , `obl_root` 
                , `obl_root_compound` 
                , `obl_case` )
            DO UPDATE SET
                `count` = `count` + excluded.`count`
                ;
        """, sql_colls)

        self._cursor.executemany(f"""
        INSERT INTO {self._TABLE2_NAME} (
            `row_id`, 
            `sentence_id`, 
            `root_id`, 
            `verb_id`, 
            `compound_ids`,
            `obl_ids`,
            `clauses_count`
            )
            VALUES ( 
                (SELECT `id` FROM {self._TABLE1_NAME} WHERE 
                    `verb` = ? 
                    AND `verb_compound` = ? 
                    AND `obl_root` = ? 
                    AND `obl_root_compound` = ?
                    AND `obl_case` = ?  ),
                ?, ?, ?, ?, ?, ?)
                ;
        """, sql_examples)

        self._cursor.execute(f"""
          INSERT INTO collections_processed VALUES (?,?)
          ON CONFLICT(tablename) DO UPDATE SET lastcollection=?;""", (
            self._TABLE1_NAME,
            lastcollection,
            lastcollection,
        ))

        self._connection.commit()
        eprint(f'andmebaasi salvestatud kollokatsioonid kollektsioonidest: 0 - {lastcollection}')

    def index_fields(self):
        indexesQ = []
        for field in list(self.key_fields) + ['count']:
            direction = 'ASC' if field not in ['count'] else 'DESC'
            indexesQ.append(f'CREATE INDEX IF NOT EXISTS "`{field}`" ON "{self._TABLE1_NAME}" ("`{field}`" {direction});')
        for q in indexesQ:
            self._cursor.execute(q)


def eprint(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)


def extract_something(text, collection_id, collocations):
    """
    Collects custom data from text layers
    One sentence per text.
    # text should contain following layers:
    * v172_obl_phrases - OBL
    * v172_stanza_syntax  - Stanza märgendus
    * v172_clauses - osalaused
    * morph_analysis
    """

    # 1. make stanza syntax graph
    graph = SyntaxGraph(text['v172_stanza_syntax'])

    # graph.draw_graph()
    # matrix for node distances
    dpath = graph.get_distances_matrix()

    # ---
    # 2. collect verbs, compounds node ids

    # verb nodes
    verb_nodes = graph.get_nodes_by_attributes(attrname='pos', attrvalue='V')
    # print ('verb_nodes', verb_nodes)

    # compound:prt
    compound_nodes = graph.get_nodes_by_attributes(attrname='deprel', attrvalue='compound:prt')

    # ---
    # 3. collect OBL info
    # obl['root_lemma_compound'],
    # obl['root_case'],

    obl_data = []
    for obl in text['v172_obl_phrases']:
        obl_kids = [k for k in dpath[obl.root_id] if dpath[obl.root_id][k] == 1]
        obl_data.append({
            'nodes': [graph.get_nodes_by_attributes(attrname='start', attrvalue=s.start)[0] for s in obl.spans],
            'root_id': obl.root_id,
            'root_lemma': graph.nodes[obl.root_id]['lemma'],
            'root_lemma_compound': text['morph_analysis'][obl.root_id-1]['root'][0],
            'root_case': graph.get_node_case(obl.root_id),
            'root_pos':  graph.nodes[obl.root_id]['pos'],
            'k': ','.join(sorted([graph.nodes[k]['lemma'] for k in obl_kids if
                                  graph.nodes[k]['pos'] == 'K' and graph.nodes[k]['deprel'] == 'case']))
        })
        
    # ----
    # 4. count clauses
    clauses_count = len(text['v172_clauses'])
   
    
    # print ('obl_data', obl_data)

    # iteratsioon üle verbide
    # kogume kokku compound järjestatud
    # itereerime üle obl fraaside, kui mõne fraasi juur on selle verbi alluv (siin tuleb optimeerida ?)

    for verb in verb_nodes:

        # do skip collocation if verb is "unusual"
        if not graph.is_verb_normal(verb):
            continue

        # childnodes
        kids = [k for k in dpath[verb] if dpath[verb][k] == 1]
        v_lemma = graph.nodes[verb]['lemma']

        # compound children
        n_compounds = ListUtils.list_intersection(kids, compound_nodes)
        if not len(n_compounds):
            verb_compound = ''
            n_compounds.append(None)
        else:
            verb_compound = ', '.join([graph.nodes[n]['lemma'] for n in sorted(n_compounds) if n])

        # if obl_data is empty, there is no need to further check
        if not len(obl_data):
            continue
            # ei kogu andmeid verbide kohta, mille alluvuses ei ole OBL fraasi
            # c# key = (verb_lemma, verb_compound, obl_lemma, obl_case, obl_k,  ner_loc, ner_per, ner_org, timex)
            # key = (v_lemma, verb_compound, '', '', '',)
            # collocations = add_key_in_collocations(key, collocations)
            # collocations[key]['total'] += 1
            # add to collocations
            # continue

        for obl in obl_data:
            if not obl['root_id'] in kids:
                continue

            key = (v_lemma,
                   verb_compound,
                   obl['root_lemma'],
                   obl['root_lemma_compound'],
                   obl['root_case'],)
            collocations = add_key_in_collocations(key, collocations)
            collocations[key]['total'] += 1
            collocations[key]['examples'].append((
                collection_id,
                obl['root_id'],
                verb,
                [str(n) for n in n_compounds if n],  # compound_ids
                [str(n) for n in obl['nodes']],  # obl_ids
                clauses_count, # clauses count in sentence
            ))

    return collocations,


def add_key_in_collocations(key, collocations):
    if key not in collocations:
        collocations[key] = {'total': 0, 'examples': []}
    return collocations
