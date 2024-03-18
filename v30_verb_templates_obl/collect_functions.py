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
            " `sentence_id` text,"
            " `verb_id` text,"
            " `verb` text,"
            " `verb_compound` text,"
            " `obl_root_id` int);"
        )

        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS `transaction`"
            " (`id` INTEGER PRIMARY KEY AUTOINCREMENT,"
            " `head_id` int,"
            " `loc` int,"
            " `deprel` text,"
            " `form` text,"
            " `lemma` text,"
            " `feats` text,"
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
                    head["verb_id"],
                    head["verb"],
                    head["verb_compound"],
                    head["obl_root_id"],
                )
            )
            for tr in head["members"]:
                transactions.append(
                    (
                        head["sentence_id"],
                        head["verb_id"],
                        head["obl_root_id"],
                        tr["loc"],
                        tr["deprel"],
                        tr["form"],
                        tr["lemma"],
                        tr["pos"],
                        tr["feats"],
                    )
                )

        self._cursor.executemany(
            "INSERT INTO `transaction_head` ("
            " sentence_id,"
            " verb_id,"
            " verb,"
            " verb_compound,"
            " obl_root_id"
            ")"
            " VALUES (?, ?, ?, ?, ?);",
            transaction_heads,
        )

        self._cursor.executemany(
            "INSERT INTO `transaction` ("
            " head_id,"
            " loc,"
            " deprel,"
            " form,"
            " lemma,"
            " pos,"
            " feats"
            ")"
            "VALUES ("
            "(SELECT `id` FROM `transaction_head`  WHERE"
            " `sentence_id` = ? AND `verb_id` = ? AND `obl_root_id` = ?),"
            "?, ?, ?, ?, ?, ?);",
            transactions,
        )

        self._connection.commit()
        eprint(
            "andmebaasi salvestatud kollokatsioonid kollektsioonidest:"
            f" 0 - {lastcollection}"
        )

    def index_fields(self):
        indexesQ = []
        for field in ("sentence_id", "verb_id", "verb", "verb_compound"):
            direction = "ASC" if field not in ["count"] else "DESC"
            indexesQ.append(
                f'CREATE INDEX IF NOT EXISTS "`{field}`"'
                f' ON transaction_head("`{field}`" {direction});'
            )
        for q in indexesQ:
            self._cursor.execute(q)
        self._connection.commit()


def eprint(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)


def extract_something(text, collection_id, data):
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
    graph = SyntaxGraph(text["v172_stanza_syntax"])

    # graph.draw_graph2()

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

    # ---
    # 3. collect OBL info
    # obl['root_lemma_compound'],
    # obl['root_case'],

    obl_data = []
    for obl in text["v172_obl_phrases"]:
        obl_kids = [k for k in dpath[obl.root_id] if dpath[obl.root_id][k] == 1]
        obl_data.append(
            {
                "nodes": [
                    graph.get_nodes_by_attributes(attrname="start", attrvalue=s.start)[
                        0
                    ]
                    for s in obl.spans
                ],
                "root_id": obl.root_id,
                "root_lemma": graph.nodes[obl.root_id]["lemma"],
                "root_lemma_compound": text["morph_analysis"][obl.root_id - 1]["root"][
                    0
                ],
                "root_case": graph.get_node_case(obl.root_id),
                "root_pos": graph.nodes[obl.root_id]["pos"],
                "obl_kids": obl_kids,
                "k": ",".join(
                    sorted(
                        [
                            graph.nodes[k]["lemma"]
                            for k in obl_kids
                            if graph.nodes[k]["pos"] == "K"
                            and graph.nodes[k]["deprel"] == "case"
                        ]
                    )
                ),
            }
        )
    # print("obl_data", obl_data)

    # iteratsioon üle verbide
    # kogume kokku compound järjestatud
    # itereerime üle obl fraaside, kui mõne fraasi juur on
    # selle verbi alluv (siin tuleb optimeerida ?)

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

        # TODO! küsi üle
        # if obl_data is empty, there is no need to further check
        if not len(obl_data):
            continue

        for obl in obl_data:
            if not obl["root_id"] in kids:
                continue
            transaction_head = {
                "sentence_id": collection_id,
                "verb_id": verb,
                "verb": verb_lemma,
                "obl_root_id": obl["root_id"],
                "verb_compound": verb_compound,
                "members": [],
            }

            for m in sorted(obl["obl_kids"] + [obl["root_id"]]):
                member = {
                    "loc": m,
                    "deprel": graph.nodes[m]["deprel"],
                    "morf": "morf",
                    "form": graph.nodes[m]["form"],
                    "lemma": graph.nodes[m]["lemma"],
                    "pos": graph.nodes[m]["pos"],
                    "feats": ",".join(sorted(graph.nodes[m]["feats"])),
                }
                transaction_head["members"].append(member)
            data.append(transaction_head)

    return (data,)
