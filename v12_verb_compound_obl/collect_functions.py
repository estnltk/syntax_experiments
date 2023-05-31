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
        'obl_pos',
        'obl_k',
        'ner_loc',
        'ner_per',
        'ner_org',
        'timex',
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
                        , `obl_pos` text
                        , `obl_k` text
                        , `ner_loc` text
                        , `ner_per` text
                        , `ner_org` text
                        , `timex` text
                        , `phrase_type` text
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
                , `obl_pos` 
                , `obl_k` 
                , `ner_loc` 
                , `ner_per` 
                , `ner_org` 
                , `timex` 
              );
          """)
        # loome näidete faili
        self._cursor.execute(f"""CREATE TABLE {self._TABLE2_NAME}
                        (row_id integer
                        , sentence_id integer
                        , root_id integer
                        , count integer);
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
            # total = some of cases + opposite case

            sql_colls.append((key[0],  # verb
                              key[1],  # verb_compound
                              key[2],  # obl_root
                              key[3],  # obl_root_compound
                              key[4],  # obl_case
                              key[5],  # obl_pos
                              key[6],  # obl_k
                              key[7],  # ner_loc
                              key[8],  # ner_per
                              key[9],  # ner_org
                              key[10],  # timex
                              collocations[key]['total']  # count
                              ))

            for example in collocations[key]['examples']:
                sql_examples.append((
                    key[0],  # verb
                    key[1],  # verb_compound
                    key[2],  # obl_root
                    key[3],  # obl_root_compound
                    key[4],  # obl_case
                    key[5],  # obl_pos
                    key[6],  # obl_k
                    key[7],  # ner_loc
                    key[8],  # ner_per
                    key[9],  # ner_org
                    key[10],  # timex
                    example[0],  # sentence_id
                    example[1],  # root_id
                    1
                ))

        self._cursor.executemany(f"""
        INSERT INTO {self._TABLE1_NAME} (
            verb
            , verb_compound
            , obl_root
            , obl_root_compound
            , obl_case
            , obl_pos
            , obl_k
            , ner_loc
            , ner_per
            , ner_org
            , timex
            , count )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(`verb`
                , `verb_compound` 
                , `obl_root` 
                , `obl_root_compound` 
                , `obl_case` 
                , `obl_pos` 
                , `obl_k` 
                , `ner_loc` 
                , `ner_per` 
                , `ner_org` 
                , `timex` )
            DO UPDATE SET
                `count` = `count` + excluded.`count`
                ;
        """, sql_colls)

        self._cursor.executemany(f"""
        INSERT INTO {self._TABLE2_NAME} (`row_id`, `sentence_id`, `root_id`, `count`)
            VALUES ( 
                (SELECT `id` FROM {self._TABLE1_NAME} WHERE 
                    `verb` = ? 
                    AND `verb_compound` = ? 
                    AND `obl_root` = ? 
                    AND `obl_root_compound` = ?
                    AND `obl_case` = ? 
                    AND `obl_pos` = ?
                    AND `obl_k` = ? 
                    AND `ner_loc` = ? 
                    AND `ner_per` = ? 
                    AND `ner_org` = ? 
                    AND `timex` = ? ),
                ?, ?, ?)
                ON CONFLICT(`row_id`, `sentence_id`, `root_id`)
            DO UPDATE SET
                `count` = `count` + excluded.`count`
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
        for field in list(self.key_fields) + ['count', 'phrase_type']:
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
    * v171_named_entities  - NER (types:  )
    * v172_obl_phrases - OBL
    * v172_pre_timexes - TIMEX
    * v172_stanza_syntax  - Stanza märgendus
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
    # print ('obl_data', obl_data)

    # ---
    # 4. collect NER info
    ner_data = []
    for ner in text['v171_named_entities']:
        start_nodes = [graph.get_nodes_by_attributes(attrname='start', attrvalue=s.start)[0] for s in ner.spans]
        end_nodes = [graph.get_nodes_by_attributes(attrname='end', attrvalue=s.end)[0] for s in ner.spans]
        if not start_nodes == end_nodes:
            print(ner, f'ner.start: {ner.start}', f'ner.end: {ner.end}')
            raise 'NER not start_nodes == end_nodes'

        ner_data.append({
            'tag': ner.nertag,
            'nodes': start_nodes

        })

    # print ('ner_data', ner_data)

    # ----
    # 5. collect TIMEX info
    timex_data = []
    for timex in text['v172_pre_timexes']:

        # timex span can begin and end in the middle of words
        # span.end and span.begin in some cases do not match end and start of word spans
        # first we try to find exact match and if it doesn't work we find nearest matched end and start of word spans
        #
        try:
            first_node = graph.get_nodes_by_attributes(attrname='start', attrvalue=timex.start)[0]
        except Exception as e:
            # last node that starts before timex span starts
            first_node = [n for n in graph.nodes if n and graph.nodes[n]['start'] < timex.start][-1]
            # display (text.words)
            # print ('timex', timex, f'timex.start: {timex.start}', f'timex.end: {timex.end}')
            # print ('first node', first_node)

        try:
            last_node = graph.get_nodes_by_attributes(attrname='end', attrvalue=timex.end)[0]
        except Exception as e:
            # fist node that ends after timex span ends
            last_node = [n for n in graph.nodes if n and graph.nodes[n]['end'] > timex.start][0]
            # display (text.words)
            # print ('timex', timex, f'timex.start: {timex.start}', f'timex.end: {timex.end}')
            # print ('last node', last_node)

        timex_data.append({
            'type': timex.type,
            'nodes': list(range(first_node, last_node + 1))
        })

    # iteratsioon üle verbide
    # kogume kokku compound järjestatud
    # itereerime üle obl fraaside, kui mõne fraasi juur on selle verbi alluv (siin tuleb optimeerida ?)
    # timex ja ner kohta pannakse tabelisse kõige prioriteetsem seos. Seoste prioriteet on paigas relations massiivis

    # key = (verb_lemma, verb_compound, obl_lemma, obl_case, ner_loc, ner_per, ner_org, timex)
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
            # key = (verb_lemma, verb_compound, obl_lemma, obl_case, obl_k,  ner_loc, ner_per, ner_org, timex)
            key = (v_lemma, verb_compound, '', '', '', '', '', '', '', '', '',)
            collocations = add_key_in_collocations(key, collocations)
            collocations[key]['total'] += 1

            # add to collacations
            continue

        for obl in obl_data:
            if not obl['root_id'] in kids:
                continue
            ner_relations = {'LOC': [], 'PER': [], 'ORG': []}
            for ner in ner_data:
                if ner['tag'] not in ner_relations:
                    ner_relations[ner['tag']] = []
                ner_relations[ner['tag']].append(ListUtils.get_relation_type(obl['nodes'], ner['nodes']))

            timex_relations = []
            for timex in timex_data:
                timex_relations.append(ListUtils.get_relation_type(obl['nodes'], timex['nodes']))

            key = (v_lemma,
                   verb_compound,
                   obl['root_lemma'],
                   obl['root_lemma_compound'],
                   obl['root_case'],
                   obl['root_pos'],
                   obl['k'],
                   ner_relations['LOC'][0] if len(ner_relations['LOC']) else '-',
                   ner_relations['PER'][0] if len(ner_relations['PER']) else '-',
                   ner_relations['ORG'][0] if len(ner_relations['ORG']) else '-',
                   timex_relations[0] if len(timex_relations) else '-',)
            collocations = add_key_in_collocations(key, collocations)
            collocations[key]['total'] += 1
            collocations[key]['examples'].append((collection_id, obl['root_id'],))

    return collocations,


def add_key_in_collocations(key, collocations):
    if key not in collocations:
        collocations[key] = {'total': 0, 'examples': []}
    return collocations


"""
def extract_obl_info(text, collection_id):
    graph = SyntaxGraph(text['v172_stanza_syntax'])

    table2_indexes_ = [
        'col_id',
        'root_id',
        'word_count',
        'consistent',
        'punctuation_count',
        'consistent_wo_punctuation',
        'verb_normal_count',
        'verb_unnormal_count',
    ]

    data = []
    punctuation_nodes = graph.get_nodes_by_attributes(attrname='deprel', attrvalue='punct')
    verb_nodes = graph.get_nodes_by_attributes(attrname='pos', attrvalue='V')

    for obl in graph.get_obl_info(text['v172_obl_phrases']):
        is_consistent = ListUtils.is_list_consecutive(obl['nodes'])
        # has_nested_obl =
        obl_verbs = ListUtils.list_intersection(verb_nodes, obl['nodes'])
        verb_normal_count = len([graph.is_verb_normal(v) for v in obl_verbs])

        obl_punctuation = ListUtils.list_intersection(punctuation_nodes, obl['nodes'])
        # contains_verb = len(ListUtils.list_intersection(verb_nodes, obl['nodes'])) > 0
        if not len(obl_punctuation):
            is_consistent_wo_punct = is_consistent
        else:
            obl_nodes_punct_removed = [n for n in obl['nodes'] if n not in obl_punctuation]
            is_consistent_wo_punct = ListUtils.is_list_consecutive(obl_nodes_punct_removed)

        r = {
            'col_id': collection_id,
            'root_id': obl['root_id'],
            'word_count': len(obl['nodes']),
            'consistent': int(is_consistent),
            'punctuation_count': len(obl_punctuation),
            'consistent_wo_punctuation': int(is_consistent_wo_punct),
            'verb_normal_count': verb_normal_count,
            'verb_unnormal_count': len(obl_verbs) - verb_normal_count,
        }
        data.append(r)
    return data
"""
