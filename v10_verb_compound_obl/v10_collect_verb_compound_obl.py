from __future__ import print_function
from collections import defaultdict
import random
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import sqlite3
import sys
from textwrap import wrap
from datetime import datetime

import sys
# estnltk_patches teegi asukoht
# https://github.com/estnltk/syntax_experiments/tree/adverbials/adverbials/estnltk_patches
# sys.path.append('/Users/rabauti/repos/syntax_experiments_adverbial/syntax_experiments/adverbials')
# for hpc (copy estnltk_patches to that location)
sys.path.append('/gpfs/space/home/zummy/v10_verb_compound_obl')
from estnltk_patches import EntityTagger
from estnltk.storage.postgres import PostgresStorage

# serialisation_registry fail 
# https://github.com/estnltk/syntax_experiments/blob/syntax_consistency/collection_splitting/serialisation_module/syntax_v1.py
from estnltk_core.converters.serialisation_registry import SERIALISATION_REGISTRY
from estnltk_patches import syntax_v1 

if 'syntax_v1' not in SERIALISATION_REGISTRY:
    SERIALISATION_REGISTRY['syntax_v1'] = syntax_v1



def eprint(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)


class GraphMethods:
    # kahe listi ühisosa
    @staticmethod
    def intersection(a, b):
        return list(set(a).intersection(b))

    # tipu leidmine atribuudi väärtuse järgi
    @staticmethod
    def get_nodes_by_attributes(graph, attrname, attrvalue):
        nodes = defaultdict(list)
        {nodes[v].append(k) for k, v in nx.get_node_attributes(graph, attrname).items()}
        if attrvalue in nodes:
            return dict(nodes)[attrvalue]
        return []

    # graafi joonistamine
    # tipp - lemma
    # serv - deprel
    @staticmethod
    def draw_graph(graph, **kwargs):
        """Puu/graafi joonistamine
        tipp - lemma
        serv - deprel
        title string    Graafi pealkiri
        filename string Failinimi kuhu joonis salvestatakse
        highlight array of integers     tippude id, d mis värvitakse joonisel punaseks
        """
        title = None
        filename = None
        custom_colors = None
        highlight = []
        if 'title' in kwargs:
            title = kwargs['title']

        if 'filename' in kwargs:
            filename = kwargs['filename']

        if 'highlight' in kwargs:
            highlight = kwargs['highlight']

        if 'custom_colors' in kwargs:
            custom_colors = kwargs['custom_colors']

        if not custom_colors:
            colors = ['lightskyblue' for node in graph]
        else:
            colors = custom_colors
        # soovitud tipud punaseks

        color_map = ['red' if node in highlight else colors[i] for (i,node) in enumerate(graph.nodes)]

        #print (color_map)
        # joonise suurus, et enamik puudest ära mahuks
        plt.rcParams["figure.figsize"] = (18.5, 10.5)

        #pealkiri
        if title:
            title = ("\n".join(wrap( title, 120)))
            plt.title(title)

        pos = graphviz_layout(graph, prog='dot')
        labels = nx.get_node_attributes(graph, 'lemma')
        nx.draw(graph, pos, cmap = plt.get_cmap('jet'),labels=labels, with_labels=True, node_color=color_map)
        edge_labels = nx.get_edge_attributes(graph, 'deprel')
        nx.draw_networkx_edge_labels(graph, pos, edge_labels)

        #kui failinimi, siis salvestame faili
        #kui pole, siis joonistame väljundisse
        if filename:
            plt.savefig(f'{filename}.png', dpi=100)
        else:
            plt.show()
        plt.clf()

    @staticmethod
    def stanza_syntax_to_graph(sentence_syntax_layer):
        """ stanza stanza_syntax objektist graafi tegemine """
        g_sentence = nx.DiGraph()
        for data in sentence_syntax_layer:
            if isinstance(data['id'], int):
                # paneme graafi kokku
                g_sentence.add_node(data['id'], id=data['id'], lemma=data['lemma'], pos=data['upostag'],
                                    deprel=data['deprel'],
                                    form=data.text, feats=data['feats'], start=data.start, end=data.end)

                g_sentence.add_edge(data['id'] - data['id'] + data['head'], data['id'], deprel=data['deprel'])
        return g_sentence


class DbMethods:

    @staticmethod
    def prep_coll_db(do_truncate = True):
        global TABLENAME, cursor, conn

        cursor.execute(f"""CREATE TABLE IF NOT EXISTS collections_processed
                        (tablename text, lastcollection integer);
                        """)

        cursor.execute(f"""
        CREATE UNIQUE INDEX IF NOT EXISTS collections_processed_uniq ON collections_processed(tablename);
      """)

        # tsv failist lugemise korral loome tabeli alati nullist
        cursor.execute(f"""
          INSERT INTO collections_processed VALUES (?,?)
          ON CONFLICT(tablename) DO UPDATE SET lastcollection=?;""", (TABLENAME, 0, 0,))

        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {TABLENAME}
                        (`id` INTEGER PRIMARY KEY AUTOINCREMENT
                        , `verb` text
                        , `verb_compound` text
                        , `obl_root` text
                        , `obl_case` text
                        , `ner_loc` text
                        , `ner_per` text
                        , `ner_org` text
                        , `timex` text
                        
                        , `phrase_type`
                        , `count` int
                        );
                       """)
        
        # add uniq_index on all fields beside id and total
        INDEXNAME = f'{TABLENAME}_unique'
        cursor.execute(f"""CREATE UNIQUE INDEX IF NOT EXISTS {INDEXNAME}
          ON {TABLENAME}(
                `verb`
                , `verb_compound` 
                , `obl_root` 
                , `obl_case` 
                , `ner_loc` 
                , `ner_per` 
                , `ner_org` 
                , `timex` 
              );
          """)
        # loome näidete faili
        cursor.execute(f"""CREATE TABLE {TABLENAME}_examples
                        (colloc_id integer
                        , sentences text);
                        """)

        # tsv failist lugemise korral loome tabeli alati nullist
        cursor.execute(f"""DELETE FROM {TABLENAME};""")

       
        
        INDEXNAME = f'{TABLENAME}_unique'
        cursor.execute(f"""CREATE UNIQUE INDEX IF NOT EXISTS {INDEXNAME}_examples
          ON {TABLENAME}_examples(
              colloc_id
              );
          """)
        
        if do_truncate: cursor.execute(f"DELETE FROM {TABLENAME} WHERE 1;")

        conn.commit()

    @staticmethod
    def save_coll_to_db(collocations, lastcollection):
        
        global TABLENAME, cursor, conn, cases
        sql_colls = []
        sql_examples = []
        for key in collocations.keys():
            #total = some of cases + opposite case 
            
            sql_colls.append((key[0], # verb
                              key[1], # verb_compound
                              key[2], # obl_root
                              key[3], # obl_case
                              key[4], # ner_loc
                              key[5], # ner_per
                              key[6], # ner_org
                              key[7], # timex
                              collocations[key]['total'] # count
                              ))
            
            if len(collocations[key]['examples']):
                sql_examples.append((key[0], # verb
                                      key[1], # verb_compound
                                      key[2], # obl_root
                                      key[3], # obl_case
                                      key[4], # ner_loc
                                      key[5], # ner_per
                                      key[6], # ner_org
                                      key[7], # timex
                                        ','.join([str(example) for example in collocations[key]['examples']])
                                        ))
                
        cursor.executemany(f"""
        INSERT INTO {TABLENAME} (
            verb
            , verb_compound
            , obl_root
            , obl_case
            , ner_loc
            , ner_per
            , ner_org
            , timex
            , count )
            
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(`verb`
                , `verb_compound` 
                , `obl_root` 
                , `obl_case` 
                , `ner_loc` 
                , `ner_per` 
                , `ner_org` 
                , `timex` )
            DO UPDATE SET
                `count` = `count` + excluded.`count`
                ;
        """, sql_colls)
        
        cursor.executemany(f"""
        INSERT INTO {TABLENAME}_examples (colloc_id, sentences)
            VALUES ( 
                (SELECT id FROM {TABLENAME} WHERE 
                    verb = ? AND verb_compound = ? AND obl_root = ? AND obl_case = ? AND ner_loc = ? AND ner_per = ? AND ner_org = ? AND timex = ? ),
                ?)
        ON CONFLICT(colloc_id)
            DO UPDATE SET
                sentences = sentences || ',' || excluded.sentences
                ;
        """, sql_examples)

        cursor.execute(f"""
          INSERT INTO collections_processed VALUES (?,?)
          ON CONFLICT(tablename) DO UPDATE SET lastcollection=?;""", (TABLENAME, lastcollection, lastcollection,))

        conn.commit()
        eprint(f'andmebaasi salvestatud kollokatsioonid kollektsioonidest: 0 - {lastcollection}')


# helping functions
def feats_get_case(arr):
    for attr in arr:
        if attr in ('nom',  # nimetav
                    'gen',  # omastav
                    'part',  # osastav
                    'adit',  # lyh sisse
                    'ill',  # sisse
                    'in',  # sees
                    'el',  # seest
                    'ad',  # alale
                    'all',  # alal
                    'abl',  # alalt
                    'tr',  # saav
                    'term',  # rajav
                    'es',  # olev
                    'abes',  # ilma#
                    'kom',  # kaasa#
                    ):
            return attr
    return '<käändumatu>'


def do_skip_verb(graph, verb):
    
    feats = graph.nodes[verb]['feats'].keys()
    
    # kui on umbisikuline
    if 'imps' in feats:
        #GraphMethods.draw_graph(graph, title=' '.join([graph.nodes[n]['form'] for n in sorted(graph.nodes) if n ]), highlight=[verb])
        return True
    
    #tense pole past, impf, pres
    if not len(GraphMethods.intersection(['past', 'impf', 'pres'], feats)):
        #print(graph.nodes[verb])
        return True
    
    #GraphMethods.draw_graph(graph, title=' '.join([graph.nodes[n]['form'] for n in sorted(graph.nodes) if n ]), highlight=[verb])
    #if 'mod' in feats:
    #    print(graph.nodes[verb])
    #    GraphMethods.draw_graph(graph, title=' '.join([graph.nodes[n]['form'] for n in graph.nodes if n ]), highlight=[verb])
    #if len(GraphMethods.intersection(['ps1', 'ps2', 'ps3'], feats)):
    #    print(graph.nodes[verb])
    #    GraphMethods.draw_graph(graph, title=' '.join([graph.nodes[n]['form'] for n in graph.nodes if n ]), highlight=[verb])
    #    return True
    
    return False
    
key_fields = ('verb'
                , 'verb_compound'
                , 'obl_root'
                , 'obl_case'
                , 'ner_loc'
                , 'ner_per'
                , 'ner_org'
                , 'timex' ,
                )

# required for ordering
relations = ['match', 'contains', 'inside', 'intersects', '-']


"""
-:            OBL ei ole kautud ühegi spaniga
match:       OBL span langeb kokku NER/TIMEX spaniga
contains:    OBL spani sees on NER/TIMEX span
inside:        OBL span on  NER/TIMEX spani sees
intersects:  OBL span lõikub NER/TIMEX spaniga

"""
def get_relation_type(obl_nodes, other_nodes):
    
    obl_nodes = sorted(obl_nodes)
    other_nodes = sorted(other_nodes)
    
    # kui obl_nodes tühi, ei tohiks tegelikult olla sellist olukorda
    if not len(obl_nodes) or not len(other_nodes):
        return '-'
    
    # match: OBL span langeb kokku NER/TIMEX spaniga
    if len(obl_nodes) and obl_nodes == other_nodes:
        return 'match'
    
    # ühisosa
    intersection = sorted(GraphMethods.intersection(obl_nodes, other_nodes))
    
    # contains:    OBL spani sees on NER/TIMEX span
    if intersection == other_nodes and len(obl_nodes)>len(other_nodes):
        return 'contains'
    
    # inside:        OBL span on  NER/TIMEX spani sees
    if intersection == obl_nodes and len(other_nodes)>len(obl_nodes):
        return 'inside'
    
    # intersects:  OBL span lõikub NER/TIMEX spaniga
    if len(intersection):
        return 'intersects'
    
    # -: OBL ei ole kautud ühegi spaniga
    return '-'
    

examples_combinations = []
def extract_something(text, colId, collocations):
    """
       

    """
    
    keys = []
    # sentence should contain layers: 'v171_named_entities', 'v172_stanza_syntax', 'v172_obl_phrases', 'v172_pre_timexes'
    # * v171_named_entities  - NER (types:  )
    # * v172_obl_phrases - OBL
    # * v172_pre_timexes - TIMEX
    # * v172_stanza_syntax  - Stanza märgendus
    
    # ---
    # 1. make directed networx graph 
    graph = GraphMethods.stanza_syntax_to_graph(text.v172_stanza_syntax)
    
    # shortest path between nodes
    path = nx.all_pairs_shortest_path_length(graph)
    
    # matrix for node distances 
    dpath = {x[0]: x[1] for x in path}
    
    # ---
    # 2. collect verbs, compounds node ids
    
    # verb nodes
    verb_nodes = GraphMethods.get_nodes_by_attributes(graph, attrname='pos', attrvalue='V')
    #print ('verb_nodes', verb_nodes)
    
    # compound:prt
    compound_nodes = GraphMethods.get_nodes_by_attributes(graph, attrname='deprel', attrvalue='compound:prt')
    
    # ---
    # 3. collect OBL info
    obl_data = []
    for obl in text['v172_obl_phrases']:
        obl_data.append ({
            'nodes': [GraphMethods.get_nodes_by_attributes(graph, attrname='start', attrvalue=s.start)[0] for s in obl.spans],
            'root_id': obl.root_id,
            'root_lemma': graph.nodes[obl.root_id]['lemma'],
            'root_case': feats_get_case(graph.nodes[obl.root_id]['feats'])
        })
        
        
    #print ('obl_data', obl_data)
       
        
    # ---
    # 4. collect NER info
    ner_data = []
    for ner in text['v171_named_entities']:
        start_nodes = [GraphMethods.get_nodes_by_attributes(graph, attrname='start', attrvalue=s.start)[0] for s in ner.spans]
        end_nodes = [GraphMethods.get_nodes_by_attributes(graph, attrname='end', attrvalue=s.end)[0] for s in ner.spans]
        if not start_nodes == end_nodes:
            display (text.words)
            print (ner,  f'ner.start: {ner.start}', f'ner.end: {ner.end}' )
            raise ('NER not start_nodes == end_nodes')
            
        ner_data.append( {
            'tag': ner.nertag, 
            'nodes': start_nodes
            
        })
        
    #print ('ner_data', ner_data)
    
    #----
    # 5. collect TIMEX info
    timex_data = []
    for timex in text['v172_pre_timexes']:
        
        # timex span can begin and end in the middle of words
        # span.end and span.begin in some cases do not match end and start of word spans
        # first we try to find exact match and if it doesn't work we find nearest matched end and start of word spans
        # 
        try:
            first_node = GraphMethods.get_nodes_by_attributes(graph, attrname='start', attrvalue=timex.start)[0]
        except:
            # last node that starts before timex span starts
            first_node = [n for n in graph.nodes if n and graph.nodes[n]['start']<timex.start][-1]
            #display (text.words)
            #print ('timex', timex, f'timex.start: {timex.start}', f'timex.end: {timex.end}')
            #print ('first node', first_node)
        
        try:
            last_node = GraphMethods.get_nodes_by_attributes(graph, attrname='end', attrvalue=timex.end)[0]
        except:
            # fist node that ends after timex span ends
            last_node = [n for n in graph.nodes if n and graph.nodes[n]['end']>timex.start][0]
            #display (text.words)
            #print ('timex', timex, f'timex.start: {timex.start}', f'timex.end: {timex.end}')
            #print ('last node', last_node)
            

        timex_data.append({
            'type': timex.type, 
            'nodes': list(range(first_node, last_node+1))
        })
        

    
    # iteratsioon üle verbide
    # kogume kokku compound järjestatud
    # itereerime üle obl fraaside, kui mõne fraasi juur on selle verbi alluv (siin tuleb optimeerida ?)
    # timex ja ner kohta pannakse tabelisse kõige prioriteetsem seos. Seoste prioriteet on paigas relations massiivis
    
    #key = (verb_lemma, verb_compound, obl_lemma, obl_case, ner_loc, ner_per, ner_org, timex)
    for verb in verb_nodes:
        
        # do skip collocation if verb is "unusual"
        
        if do_skip_verb(graph, verb): continue
        
        # childnodes
        kids = [k for k in dpath[verb] if dpath[verb][k] == 1]
        v_lemma = graph.nodes[verb]['lemma']
        
        # compound children
        n_compounds = GraphMethods.intersection(kids, compound_nodes)
        if not len(n_compounds):
            verb_compound = ''
            n_compounds.append(None)
        else: 
            verb_compound = ', '.join([graph.nodes[n]['lemma'] for n in sorted(n_compounds) if n ])
        
        # if obl_data is empty, there is no need to further check
        if not len(obl_data):
            #key = (verb_lemma, verb_compound, obl_lemma, obl_case, ner_loc, ner_per, ner_org, timex)
            keys.append( (v_lemma , verb_compound, '' , '', '', '', '', '', ))
            
            #add to collacations
            continue
        
        for obl in obl_data:
            if not obl['root_id'] in kids: continue
            ner_relations = {'LOC':[], 'PER':[], 'ORG':[]}
            for ner in ner_data:
                if ner['tag'] not in ner_relations:
                    ner_relations[ner['tag']] = []
                ner_relations[ner['tag']].append(get_relation_type( obl['nodes'], ner['nodes']))
            
            timex_relations = []
            for timex in timex_data:
               
                timex_relations.append(get_relation_type( obl['nodes'], timex['nodes']))
            
            key = (v_lemma, 
                   verb_compound, 
                   obl['root_lemma'], 
                   obl['root_case'], 
                   ner_relations['LOC'][0] if len(ner_relations['LOC']) else '-' , 
                   ner_relations['PER'][0] if len(ner_relations['PER']) else '-', 
                   ner_relations['ORG'][0] if len(ner_relations['ORG']) else '-', 
                   timex_relations[0] if len(timex_relations) else '-' , ) 
            keys.append( key)
            
            #  code to save example trees for debugging
            if 0:
                img_key = key[4:]
                if not img_key in examples_combinations:

                    try:
                        key_string = ' || '.join( [f'{key_fields[i]}: {k}' for i, k in enumerate(key)])
                        GraphMethods.draw_graph(graph=graph, 
                                        filename='./examples/'+str(colId)+'__'+str(key), 
                                        highlight=obl['nodes'], 
                                        title=' '.join( [graph.nodes[n]['form'] for n in sorted(graph.nodes) if n ])
                                                    + '\t\t\n' + str(key_string) 
                                                    + '\t\t\n NER: ' + str(text['v171_named_entities']) 
                                                    + '\t\t\n TIMEX: ' + str(text['v172_pre_timexes']) 
                                       )
                        examples_combinations.append(img_key)

                    except:
                        pass

            #print ('ner_relations', ner_relations)
            #print ('timex_relations', timex_relations, sorted(timex_relations, key=relations.index))
            #print (key)
        


    for key in keys:
        if not key in collocations:
            collocations[key] = {'total': 0, 'examples': []}
        collocations[key]['total'] += 1
        collocations[key]['examples'].append(colId)
   
    

    return collocations,
    


date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
eprint(f'{date_time} Start.')
collectionName = 'koondkorpus_sentences' 
#collectionName = 'koondkorpus_sentences_test_5000_sg_thread'  # 


TYPE = 'verb_compound_obl'
TABLENAME = f'{TYPE}_{collectionName}'
BATCH_SIZE = 100000

date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
conn = sqlite3.connect(f"v10_{collectionName}_{TYPE}_collocations_{date_time}.db")  #

cursor = conn.cursor()
DbMethods.prep_coll_db()

storage = PostgresStorage(pgpass_file='~/.pgpass',
                          schema='estonian_text_corpora',
                          role='estonian_text_corpora_read',
                          temporary=False)

collection = storage[collectionName]

# print (collection)

collocations = {}


collection.selected_layers = ['v171_named_entities', 'v172_stanza_syntax', 'v172_obl_phrases', 'v172_pre_timexes']
for (colId, text) in collection.select(progressbar=None, layers=['v171_named_entities', 'v172_stanza_syntax', 'v172_obl_phrases', 'v172_pre_timexes'], return_index=True):

    # viimane lause
    collocations,  = extract_something(text, colId, collocations )
    if not colId == 0 and not colId % BATCH_SIZE:
        DbMethods.save_coll_to_db(collocations, colId)
        collocations = {}

# saving last batch
DbMethods.save_coll_to_db(collocations , colId)

indexesQ = []

for field in list(key_fields) + ['count', 'phrase_type']:
    direction = 'ASC' if field not in ['count'] else 'DESC'

        
    indexesQ.append (f'CREATE INDEX IF NOT EXISTS "`{field}`" ON "{TABLENAME}" ("`{field}`" {direction});')
    
for q in indexesQ:
    cursor.execute(q)

cursor.execute(f"SELECT count(*) FROM {TABLENAME}")
all_collocations = cursor.fetchall()

date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
eprint(f'{date_time} Done.')