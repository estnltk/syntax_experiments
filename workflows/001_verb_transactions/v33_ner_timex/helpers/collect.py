import logging
from typing import List, Dict
from .syntax_graph import SyntaxGraph
from sqlalchemy import text
from .models import Timex, Ner

# helpers
logger = logging.getLogger("ner_timex")

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def collect_data(col_id: int, text: Dict, nodes: List[int] = None):
    """
    Kogub kokku lausest NEX ja TIMEX andmed etteantud sõnade kohta

    text vajalikud kihid:
        * v172_stanza_syntax
        * v172_pre_timexes
        * v171_named_entities

    Tagastab kaks massiivi - NER ja TIMEX andmetega.
    Eraldi rida iga sõna ja iga fraasi kohta.
    """
    # 1. SENTENCE TO GRAPH
    graph = SyntaxGraph(text["v172_stanza_syntax"])

    # 2. NODES TO FILTER RSULT BY

    # return data for all nodes
    if nodes is None:
        nodes = [n for n in graph.nodes]

    # return empty data
    if not len(nodes):
        return [], []

    # 2. TIMEX info
    timex_data = collect_timex(graph=graph, timex_layer=text["v172_pre_timexes"])
    # if timex_data:
    #    display(text["v172_pre_timexes"])

    # 3. NER info
    ner_data = collect_ner(graph=graph, ner_layer=text["v171_named_entities"])
    # if timex_data:
    #    display(text["v171_named_entities"])

    # teeme iga node kohta eraldi rea, see on kuju, kuidas sisestame baasi
    sentence_timex = [
        {
            "sentence_id": col_id,
            "loc": n,
            "timex_type": t["type"],
            "timex_id": t["id"],
            "part_of_interval": t["part_of_interval"],
            "timex_members": len(t["nodes"]),
        }
        for t in timex_data
        for n in t["nodes"]
        if n in nodes
    ]

    sentence_ner = [
        {
            "sentence_id": col_id,
            "loc": n,
            "ner_tag": ner["tag"],
            "ner_id": ner["id"],
            "ner_members": len(ner["nodes"]),
        }
        for ner in ner_data
        for n in ner["nodes"]
        if n in nodes
    ]

    return sentence_timex, sentence_ner


def collect_timex(graph, timex_layer) -> List[Dict]:
    """
    collects timex data, return as array
    """
    timex_data = []
    for timex in timex_layer:

        # timex span can begin and end in the middle of words
        # span.end and span.begin in some cases do not match end and start of word spans
        # first we try to find exact match and if it doesn't work we find nearest matched end and start of word spans
        #
        try:
            first_node = graph.get_nodes_by_attributes(
                attrname="start", attrvalue=timex.start
            )[0]
        except Exception:
            # last node that starts before timex span starts
            first_node = [
                n for n in graph.nodes if n and graph.nodes[n]["start"] < timex.start
            ][-1]
            # display (text.words)
            # print ('timex', timex, f'timex.start: {timex.start}', f'timex.end: {timex.end}')
            # print ('first node', first_node)

        try:
            last_node = graph.get_nodes_by_attributes(
                attrname="end", attrvalue=timex.end
            )[0]
        except Exception:
            # fist node that ends after timex span ends
            last_node = [
                n for n in graph.nodes if n and graph.nodes[n]["end"] > timex.start
            ][0]
            # display (text.words)
            # print ('timex', timex, f'timex.start: {timex.start}', f'timex.end: {timex.end}')
            # print ('last node', last_node)

        timex_data.append(
            {
                "id": timex.tid,
                "type": timex.type,
                "part_of_interval": timex.part_of_interval,
                "nodes": list(range(first_node, last_node + 1)),
            }
        )
    return timex_data


def collect_ner(graph, ner_layer) -> List[Dict]:
    ner_data = []
    for nid, ner in enumerate(ner_layer):
        start_nodes = [
            graph.get_nodes_by_attributes(attrname="start", attrvalue=s.start)[0]
            for s in ner.spans
        ]
        end_nodes = [
            graph.get_nodes_by_attributes(attrname="end", attrvalue=s.end)[0]
            for s in ner.spans
        ]
        if not start_nodes == end_nodes:
            print(ner, f"ner.start: {ner.start}", f"ner.end: {ner.end}")
            raise "NER not start_nodes == end_nodes"

        ner_data.append({"id": nid + 1, "tag": ner.nertag, "nodes": start_nodes})
    return ner_data


def extract_sentence_and_nodes_verbs(sess, batch_size: int, offset: int) -> Dict:
    """
    Executes sql query to fetch all sentence ids and words presented in database.
    Uses left join, as not all heads have related rows in rows table.
    """
    logger.info("Starting fetching sentence and node ids for batch.")

    sql = """
        SELECT
            th.id as head_id,
            tr.id as trnx_row_id,
            th.sentence_id,
            th.loc as verb_position,
            tr.loc AS child_position
        FROM transactions.transaction_head AS th
        LEFT JOIN transactions.transaction_row AS tr ON tr.head_id = th.id
        ORDER BY th.id, tr.id
        LIMIT %i OFFSET %i""" % (
        batch_size,
        offset,
    )

    # iterate over transaction_ids
    res = sess.execute(text(sql)).mappings().all()

    count = 0
    sentence_ids = {}
    first_row = {}
    last_row = {}
    for row in res:
        sentence_id = row["sentence_id"]
        verb_position = row["verb_position"]
        child_position = row["child_position"]
        if count == 0:
            first_row = row
        count += 1
        if sentence_id not in sentence_ids:
            sentence_ids[sentence_id] = []
        sentence_ids[sentence_id].append(verb_position)
        sentence_ids[sentence_id].append(child_position)
        sentence_ids[sentence_id] = list(set(sentence_ids[sentence_id]))
        last_row = row
    logger.info(
        f"Fetched {count} rows, unique sentence ids: {len(sentence_ids.keys())}"
        f"\n\tFirst row: {first_row}"
        f"\n\tLast row: {last_row}"
    )

    return sentence_ids


def get_total_rows_to_fetch(sess):

    sql = """
        SELECT COUNT(th.id) as total
        FROM transactions.transaction_head AS th
        LEFT JOIN transactions.transaction_row AS tr ON tr.head_id = th.id
        """

    return sess.execute(text(sql)).scalar_one()


def save_timex_to_db(sess, timex_data):
    logger.info("Timex, saving to db")
    sess.bulk_insert_mappings(Timex, timex_data)
    sess.commit()
    logger.info(f"Timex, saved to db {len(timex_data)} rows")


def save_ner_to_db(sess, ner_data):
    logger.info("NER, saving to db")
    sess.bulk_insert_mappings(Ner, ner_data)
    sess.commit()
    logger.info(f"NER, saved to db {len(ner_data)} rows")
