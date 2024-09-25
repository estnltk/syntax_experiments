import sys
import sqlite3
from data_helpers.utils import ListUtils
from data_helpers.syntax_graph import SyntaxGraph
from html import escape


class DbMethods:
    """
    Class for creating and storing data in sqlite database
    """

    _cursor = None
    _connection = None

    _DB_NAME = None
    _TABLE1_NAME = None
    _TABLE2_NAME = None

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
        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS collections_processed"
            " (tablename text, lastcollection integer);"
        )

        self._cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS collections_processed_uniq"
            " ON collections_processed(tablename);"
        )

        # tsv failist lugemise korral loome tabeli alati nullist
        self._cursor.execute(
            "INSERT INTO collections_processed VALUES (?,?)"
            " ON CONFLICT(tablename) DO UPDATE SET lastcollection=?;",
            (
                self._TABLE1_NAME,
                0,
                0,
            ),
        )

        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS transaction_head"
            " (`id` INTEGER PRIMARY KEY AUTOINCREMENT,"
            " `sentence_id` int,"
            " `loc` int,"
            " `verb` text,"
            " `verb_compound` text,"
            " `deprel` text,"
            " `feats` text);"
        )
        self._cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS transaction_head_uniq"
            " ON transaction_head(sentence_id, loc);"
        )

        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS `transaction`"
            " (`id` INTEGER PRIMARY KEY AUTOINCREMENT,"
            " `head_id` int,"
            " `loc` int,"
            " `loc_rel` int,"
            " `deprel` text,"
            " `form` text,"
            " `lemma` text,"
            " `feats` text,"
            " `parent_loc` int,"
            " `pos` text);"
        )

        if do_truncate:
            self._cursor.execute("DELETE FROM `transaction_head` WHERE 1;")
            self._cursor.execute("DELETE FROM `transaction` WHERE 1;")

        self._connection.commit()

    def save_coll_to_db(self, data, lastcollection):

        transaction_heads = []
        transactions = []
        for head in data:
            transaction_heads.append(
                (
                    head["sentence_id"],
                    head["loc"],
                    head["verb"],
                    head["verb_compound"],
                    head["deprel"],
                    head["feats"],
                )
            )
            for tr in head["members"]:
                transactions.append(
                    (
                        head["sentence_id"],
                        head["loc"],
                        tr["loc"],
                        tr["loc_rel"],
                        tr["deprel"],
                        tr["form"],
                        tr["lemma"],
                        tr["pos"],
                        tr["feats"],
                        tr["parent_loc"],
                    )
                )

        self._cursor.executemany(
            "INSERT INTO `transaction_head` ("
            " sentence_id,"
            " loc,"
            " verb,"
            " verb_compound,"
            " deprel,"
            " feats"
            ")"
            " VALUES (?, ?, ?, ?, ?, ?);",
            transaction_heads,
        )

        self._cursor.executemany(
            "INSERT INTO `transaction` ("
            " head_id,"
            " loc,"
            " loc_rel,"
            " deprel,"
            " form,"
            " lemma,"
            " pos,"
            " feats,"
            " parent_loc"
            
            ")"
            "VALUES ("
            "(SELECT `id` FROM `transaction_head`  WHERE"
            " `sentence_id` = ? AND `loc` = ?),"
            "?, ?, ?, ?, ?, ?, ?, ?);",
            transactions,
        )

        self._connection.commit()
        eprint(
            "andmebaasi salvestatud kollokatsioonid kollektsioonidest:"
            f" 0 - {lastcollection}"
        )

    def index_fields(self):
        indexesQ = []
        for field in ("verb", "verb_compound", "feats", "deprel"):
            direction = "ASC" if field not in ["count"] else "DESC"
            indexesQ.append(
                f'CREATE INDEX IF NOT EXISTS "`transaction_head_{field}`"'
                f' ON transaction_head("`{field}`" {direction});'
            )
        for q in indexesQ:
            self._cursor.execute(q)
        
        for field in ("head_id", "deprel"):
            direction = "ASC" if field not in ["count"] else "DESC"
            indexesQ.append(
                f'CREATE INDEX IF NOT EXISTS "`transaction_{field}`"'
                f' ON `transaction`("`{field}`" {direction});'
            )
        for q in indexesQ:
            self._cursor.execute(q)
            
        self._connection.commit()


def eprint(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)


def extract_something(text, collection_id, data, draw_tree=False, display_trees=False):
    """
    Collects custom data from text layers
    One sentence per text.
    # text should contain following layers:
    * v172_stanza_syntax  - Stanza märgendus
    * morph_analysis
    """

    deprels_to_ignore = [
        "punct",
        "conj",
        "mark",
        "cc",
        "parataxis",
        "discourse",
        "vocative",
        "cop",
        "cc:preconj",
        "goeswith",
        "list",
        "dep",
    ]

    # 1. make stanza syntax graph
    graph = SyntaxGraph(text["v172_stanza_syntax"])

    # matrix for node distances
    dpath = graph.get_distances_matrix()

    # ---
    # 2. collect verbs, compounds node ids

    # verb nodes
    verb_nodes = graph.get_nodes_by_attributes(attrname="pos", attrvalue="V")
    # print ('verb_nodes', verb_nodes)

    # compound:prt
    compound_nodes = graph.get_nodes_by_attributes(
        attrname="deprel", attrvalue="compound:prt"
    )

    # iteratsioon üle verbide
    # kogume kokku compound järjestatud
    # itereerime üle verbide
    highlight = []
    for verb in verb_nodes:
        # do skip collocation if verb is "unusual"
        if not graph.is_verb_normal(verb):
            continue

        # childnodes
        kids = [k for k in dpath[verb] if dpath[verb][k] == 1]
        verb_lemma = graph.nodes[verb]["lemma"]

        # compound children
        n_compounds = ListUtils.list_intersection(kids, compound_nodes)
        if not len(n_compounds):
            verb_compound = ""
            n_compounds.append(None)
        else:
            verb_compound = ", ".join(
                [graph.nodes[n]["lemma"] for n in sorted(n_compounds) if n]
            )

        transaction_head = {
            "sentence_id": collection_id,
            "loc": verb,
            "verb": verb_lemma,
            "verb_compound": verb_compound,
            "feats": ",".join(sorted(graph.nodes[verb]["feats"])),
            "deprel": graph.nodes[verb]["deprel"],
            "members": [],
        }

        # remove irrelevant nodes
        kids = [m for m in kids if graph.nodes[m]["deprel"] not in deprels_to_ignore]
        # verb -> obl -> case
        # add obl kids case
        grandkids = {}
        for obl in [m for m in kids if graph.nodes[m]["deprel"] == "obl"]:
            for case in [
                k
                for k in dpath[obl]
                if dpath[obl][k] == 1 and graph.nodes[k]["deprel"] == "case"
            ]:
                kids.append(case)
                grandkids[case] = obl

        child_pos = {node: num for num, node in enumerate(sorted(kids + [verb]))}

        for m in sorted(kids):
            member = {
                "loc": m,
                "loc_rel": child_pos[m] - child_pos[verb],
                "deprel": graph.nodes[m]["deprel"],
                "morf": "morf",
                "form": graph.nodes[m]["form"],
                "lemma": graph.nodes[m]["lemma"],
                "pos": graph.nodes[m]["pos"],
                "feats": ",".join(sorted(graph.nodes[m]["feats"])),
                "parent_loc": grandkids[m] if m in grandkids else None,  
            }
            transaction_head["members"].append(member)

        data.append(transaction_head)
        highlight.append(verb)

    if draw_tree:
        graph.draw_graph2(
            filename=f"sentences/{collection_id}.png",
            highlight=highlight,
            display=display_trees,
        )
        open(f"sentences/{collection_id}.txt", "w").write(text.text)
        open(f"sentences/{collection_id}.html", "w").write(
            """<html>
            <head>
            <link rel="stylesheet" href="styles.css">
            </head>
            <body><h1>%s</h1>
            <img src="%s">%s</body></html>"""
            % (
                escape(text.text),
                f"{collection_id}.png",
                text["v172_stanza_syntax"]._repr_html_(),
            )
        )

    return (data,)
