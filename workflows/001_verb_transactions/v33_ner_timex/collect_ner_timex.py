import os
import sys
import helpers.collect as collect
import pandas as pd
import math
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from estnltk.storage.postgres import PostgresStorage, IndexQuery
from datetime import datetime
from pathlib import Path

# from helpers.syntax_graph import SyntaxGraph
from helpers.models import Base  # , Ner, Timex

ROOT = Path(os.getcwd()).parent.parent.parent

sys.path.append(ROOT / "common_code")


# verb transactions database
TRANSACTION_DB = (
    ROOT / "databases/v33_koondkorpus_sentences_verb_pattern_obl_20241002-130310.db"
)
# TRANSACTION_DB = Path("./example_data/transactions.db")

# result database with ner and timex data
# RESULT_DB = "./example_data/ner_timex.db"
date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
RESULT_DB = f"ner_timex_{date_time}.db"

# layers used for data extracted
LAYERS = ["v171_named_entities", "v172_stanza_syntax", "v172_pre_timexes"]

# collection of koondkorpus sentences
COLLECTION_NAME = "koondkorpus_sentences"

# batch size to write in local db-file
BATCH_SIZE = 100000

# batch size of reading vert trx ids from verb transactions database
BATCH_SIZE_TRX_ROW = 100000


# create db
engine = create_engine(f"sqlite+pysqlite:///{RESULT_DB}", future=True, echo=False)
conn = engine.connect()


# connect koondkorpus sentences db
storage = PostgresStorage(
    pgpass_file="~/.pgpass",
    schema="estonian_text_corpora",
    role="estonian_text_corpora_read",
    temporary=False,
)

# tables are defined in models.py
with Session(bind=conn) as session:
    Base.metadata.create_all(engine)
    session.commit()
    print("Database and tables created.")


collection = storage[COLLECTION_NAME]
logger = collect.logger

with Session(engine) as session:
    # attaching trnx database
    db_path = os.fspath(TRANSACTION_DB)  # or str(TRANSACTION_DB)
    session.execute(text("ATTACH DATABASE :trxdb AS transactions"), {"trxdb": db_path})

    total_trnx_rows = collect.get_total_rows_to_fetch(session)

    batches_total = math.ceil(total_trnx_rows / BATCH_SIZE_TRX_ROW)

    sentences_checked = 0

    logger.info(f"Transaction rows total: {total_trnx_rows}")
    logger.info(f"Batches to fetch: {batches_total}")

    collected_ner = []
    collected_timex = []

    # last trx_row_id
    for batch_nr in range(1, batches_total + 1):
        offset = (batch_nr - 1) * BATCH_SIZE_TRX_ROW
        logger.info(f"BATCH: {batch_nr}. Limit {BATCH_SIZE_TRX_ROW}, offset {offset}")

        sentence_ids = collect.extract_sentence_and_nodes_verbs(
            session, batch_size=BATCH_SIZE_TRX_ROW, offset=offset
        )
        my_sentence_ids = list(sentence_ids.keys())
        logger.info(f"Sentences to fetch: {len(my_sentence_ids)}")

        # request data of relevant sentences
        my_select = collection.select(
            IndexQuery(my_sentence_ids),
            progressbar=None,
            layers=LAYERS,
            return_index=True,
        )

        setneces = 0
        for col_id, text_data in my_select:
            sentences_checked += 1

            # whitelisted nodes
            wl_nodes = sentence_ids[col_id]

            timex, ner = collect.collect_data(
                col_id=col_id, text=text_data, nodes=wl_nodes
            )

            collected_timex = collected_timex + timex
            collected_ner = collected_ner + ner

        if len(collected_ner) > BATCH_SIZE:
            collect.save_ner_to_db(session, collected_ner)
            collected_ner = []

        if len(collected_timex) > BATCH_SIZE:
            collect.save_timex_to_db(session, collected_timex)
            logger.info("write timex to db")
            collected_timex = []

    df_ner = pd.DataFrame(collected_ner)
    df_timex = pd.DataFrame(collected_timex)

    if len(collected_ner):
        collect.save_ner_to_db(session, collected_ner)

    if len(collected_timex):
        collect.save_timex_to_db(session, collected_timex)

    logger.info(f"Sentences checked: {sentences_checked}")
    logger.info("Done.")
