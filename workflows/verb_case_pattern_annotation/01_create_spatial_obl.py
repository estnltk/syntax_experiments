#!/usr/bin/env python
# coding: utf-8

# ## Finding all adverbials from a database
# The aim of this is to find all adverbials from the Estonian Reference corpus. This is needed to annotate them with semantic class using both rule based methods and LLMs. The code extracts data from Katrin Tsepelina's database [v33_koondkorpus_sentences_verb_pattern_obl_20241002-130310.db](https://github.com/estnltk/syntax_experiments/tree/verb_templates/workflows/001_verb_transactions/v33) with data extracted from the Estonian Reference corpus.
# This code creates new tables in the database
# 1. **spatial_obl** with nominal adverbials aka obliques in spatial cases (form + lemma + feats), their head verb (verb+compund) and sentences the obliques came from.
# Optionally as well (code needs to be modified):
# 2. **advmod** with adverbs (form + lemma), their head verbs (verb+compound) and sentences the adverbs came from
# The sentences are taken from another database and added to this one based on their sentence id.
# Ner and timex tags are taken from another database and added to this one based on their sentence id and location in sentence.

#imports
import sqlite3
import pandas as pd
from tqdm import tqdm
import argparse
import json
import configparser

# FUNCTIONS

def load_config(path):
    """Loads config.
    """
    config = configparser.ConfigParser()
    status = config.read(path) 
    assert status == [path]
    return config


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def get_combos(letters, limit, combinations):
    letters_set = set(letters)
    result = []
    for letter in letters:
        for combo in combinations[letter]:
            # combo has the right amount of tags and not other tags
            if len(combo) > limit and letters_set.issubset(combo):
                result.append(combo)

    return result


def get_tags(ekilex_tag, ner_tag, timex_tag, morph_case, combinations, mapping):

    if ner_tag == "ORG":
        # NER ORG sisekohakäänetes on LOC (adit, in, ill, el)
        if morph_case in ["adit", "in", "ill", "el"]:
            ner_tag = "LOC"
        # NER ORG väliskohakäänetes on ALIVE (ad, all, abl)
        elif morph_case in ["ad", "all", "abl"]:
            ner_tag = "PER"
            
    if ekilex_tag == "ORG":
        # TODO: ekilex org sisekohakäänetes on LOC (adit, in, ill, el)
        if morph_case in ["adit", "in", "ill", "el"]:
            ekilex_tag = "LOC"
        # TODO: EKILEX organisation väliskohakäänetes on ALIVE (ad, all, abl)
        elif morph_case in ["ad", "all", "abl"]:
            ekilex_tag = "alive"

    sources = []
    # Info about what tags are present
    if ekilex_tag is not None:
        sources.append(mapping[ekilex_tag])
    if ner_tag is not None:
        sources.append(mapping[ner_tag])
    if timex_tag is not None:
        sources.append("T")

    if not sources:
        return []

    letters = set(sources)
    if len(letters) == 1: # only one tag is present, get 1,2,3 letter combinations
        tags = combinations[next(iter(letters))]
    else: # more than one tag, get 2+3 or just 3 letter combinations
        limit = 1 if len(letters) == 2 else 2
        tags = list(set(get_combos(letters, limit, combinations)))

    # alphabetically and order by 1-letter tags, 2-letter tags, 3-letter tags
    tags.sort(key=lambda w: (len(w), w))
    return tags


def sentences_to_table(input_table, sentence_db, target_db):
    
    # Connect to both databases
    conn1 = sqlite3.connect(sentence_db)  # Source database
    conn2 = sqlite3.connect(target_db)  # Target database
    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()
    
    # Step 1: Retrieve sentences from database1
    cursor1.execute("SELECT id, text FROM sentences")
    sentences = cursor1.fetchall()  # List of (sentence_id, sentence)

    # Step 2: add new column to database2 table
    if not column_exists(cursor2, input_table, "sentence"):
        cursor2.execute("ALTER TABLE " + input_table +  " ADD COLUMN sentence TEXT")

    # Step 3: Create a temporary table
    cursor2.execute("CREATE TEMP TABLE temp_sentence (id INT PRIMARY KEY, sentence TEXT)")

    # Step 4: Insert all values into the temp table
    cursor2.executemany("INSERT INTO temp_sentence (id, sentence) VALUES (?, ?)", sentences)

    # Step 3: Perform a fast join-based update
    query = f"""
        UPDATE {input_table}
        SET sentence = (
            SELECT sentence
            FROM temp_sentence
            WHERE temp_sentence.id = {input_table}.sentence_id
            LIMIT 1
         )
        WHERE EXISTS (
            SELECT 1
            FROM temp_sentence
            WHERE temp_sentence.id = {input_table}.sentence_id
        )
    """

    cursor2.execute(query)

    conn2.commit()
    conn1.close()
    conn2.close()


def create_obl_table(db_file:str, obl_table:str):
    """ Creates table for obl in spatial cases """
    # connecting with database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # ### Create new table spatial_obl
    cursor.execute(f"DROP TABLE if exists {obl_table}")

    #searches for obliques in spatial cases + head verb + sentence id
    query = (f"CREATE TABLE {obl_table} AS " 
             f"SELECT transaction_row.id, transaction_row.sentence_id, transaction_row.head_id, transaction_row.loc as row_loc, verb, verb_compound, transaction_row.feats, pos, lemma, transaction_row.form, status, ekilex_tag, ner_tag, timex_tag " 
             f"FROM `transaction_row` JOIN `transaction_head` ON transaction_head.id = transaction_row.head_id WHERE transaction_row.deprel = 'obl' "
            f"AND (transaction_row.feats LIKE ? OR transaction_row.feats LIKE ? OR transaction_row.feats LIKE ? OR transaction_row.feats LIKE ? OR transaction_row.feats LIKE ? OR transaction_row.feats LIKE ? OR transaction_row.feats LIKE ?)")
    cursor.execute(query, ('%adit,%', '%ill,%', '%in,%', '%el,%', '%all,%', '%ad,%', '%abl,%'))

    conn.commit()
    conn.close()


def separate_cases(db_file:str, obl_table:str):
    """ Separates spatial cases and adds them to new column """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # ### Separate cases
    # Separating the case tag from the larger feats value and adding it to the database table
    cursor.execute(f"ALTER TABLE {obl_table} ADD COLUMN morph_case TEXT")

    # separate cases
    cases = ['adit', 'ill', 'in', 'el', 'all', 'ad', 'abl']

    # Fetch feats column
    cursor.execute(f"SELECT id, feats FROM {obl_table}")
    rows = cursor.fetchall()

    # find case and separate into separate column
    updates = []
    for rowid, feats in rows:
        if feats:
            for case in cases:
                if case in feats.split(","):
                    case_value = case
            updates.append((case_value, rowid))

    # add case info to main table

    # Step 1: Create a temporary table
    cursor.execute("CREATE TEMP TABLE temp_case (id INT PRIMARY KEY, morph_case TEXT)")

    # Step 2: Insert all values into the temp table
    cursor.executemany("INSERT INTO temp_case (morph_case, id) VALUES (?, ?)", updates)

    # Step 3: Perform a fast join-based update
    cursor.execute(f"""
        UPDATE {obl_table}
        SET morph_case = (SELECT morph_case FROM temp_case WHERE temp_case.id = spatial_obl.id)
    """)

    # Commit changes and close connection
    conn.commit()
    conn.close()


def create_new_tags(db_file:str, obl_table:str, tag_col:str):
    """ Creates new tag column based on ekilex, ner and timex tags """
    # ### Create tags column based on ekilex, ner and timex tags
    # All on välja toodud üldised semantilised klassid ja mis eri süsteemi märgenditest need kombineeruvad. 
    # Peamine erinevus on see, et klass ORG ei ole eraldi, vaid arvestatakse vastavalt oma käändele kas kohaks või elusaks. 
    # Sisekohakäändes (sees-, sisse-, seestütlev) on ORG koht ("Ülikoolis on palju õpilasi"), 
    # väliskohakäändes (alal-, alale-, alaltütlev) on ORG valdajamäärus/elus ("Ülikoolil on palju õpilasi".)
    # Future purposes:
    # 1. Test1: event separately
    # 2. Test2: event together with location
    # 3. Test3: time, location and event together

    # - SÜNDMUS/EVENT = EKILEX event
    # - AEG/TIME = EKILEX time + TIMEX
    # - KOHT/LOC = EKILEX location + NER LOC + EKILEX organisation sisekohakäänetes + NER ORG sisekohakäänetes
    # - KOHTSÜNDMUS/LOCEVENT = EKILEX location NER LOC + EKILEX organisation sisekohakäänetes + NER ORG sisekohakäänetes + EKILEX event
    # - KOHTSÜNDMUSAEG/LOCEVENTTIME = KOHT + SÜNDMUS + AEG
    # - VALDAJA/ALIVE = EKILEX alive + NER PER + EKILEX organisation väliskohakäänetes + NER ORG väliskohakäänetes 
    # - SEISUND/STATE = EKILEX state

    # For tag combinations:
    # - EVENT - E
    # - TIME - T
    # - LOC - L
    # - LOCEVENT - EL
    # - LOCEVENTTIME - ELT
    # - ALIVE - A
    # - STATE - S

    mapping = {"alive":"A", "PER": "A", "location":"L", "LOC":"L", "time":"T", "event":"E", "state":"S"}
    # ORG is not separately
    combinations = { 
        "T": ["T","LT","ET","ELT","AT","ALT","AET","LST","AST","ST"], 
        "L": ["L","LT","EL","ELT","LS","AL","ALT","LST"], 
        "E": ["E","EL","ET","ELT","AE","AET",], 
        "A": ["A","AT","AL","AE","AS","ALT","AET","AST"], 
        "S": ["S","LS","AS","LST","AST","ST",], 
    }

    # connecting with database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # get necessary columns from obl table
    query = f"SELECT id, ekilex_tag, ner_tag, timex_tag, morph_case FROM spatial_obl"
    obl_tags = pd.read_sql(query, conn)
    #obl_tags # 7842662 rows

    # Get tags for all rows
    tags_col = []
    for i in tqdm(range(len(obl_tags))):
        idx = obl_tags.iloc[i]["id"]
        eki = obl_tags.iloc[i]["ekilex_tag"]
        ner = obl_tags.iloc[i]["ner_tag"]
        timex = obl_tags.iloc[i]["timex_tag"]
        case = obl_tags.iloc[i]["morph_case"]

        tag_list = get_tags(eki, ner, timex, case, combinations, mapping)
        if len(tag_list) != 0:
            tag_str = "|" + "|".join(tag_list) + "|"
        else:
            tag_str = ""
            
        tags_col.append((idx, tag_str))

    tags_col_clean = [(int(i), t) for i, t in tags_col]
    assert len(tags_col_clean) == len(obl_tags)

    # New column if it doesn't exist
    if not column_exists(cursor, obl_table, tag_col):
        cursor.execute("ALTER TABLE " + obl_table +  f" ADD COLUMN {tag_col} TEXT")

    # Create a temporary table
    cursor.execute("CREATE TEMP TABLE temp_tags (id INT PRIMARY KEY, tags TEXT)")

    # Insert all values into the temp table
    cursor.executemany("INSERT INTO temp_tags (id, tags) VALUES (?, ?)", tags_col_clean)

    # Perform a fast join-based update
    query = f"""
        UPDATE {obl_table}
        SET {tag_col} = (
            SELECT tags
            FROM temp_tags
            WHERE temp_tags.id = {obl_table}.id
            LIMIT 1
         )
        WHERE EXISTS (
            SELECT 1
            FROM temp_tags
            WHERE temp_tags.id = {obl_table}.id
        )
    """

    cursor.execute(query)

    conn.commit()
    conn.close()


def run(conf_file):

    # variables from conf
    DB_FILE = conf_file["configuration"]["database"]
    SENTENCES_DB = conf_file["configuration"]["sentences_db"]
    OBL_TABLE = conf_file["configuration"]["obl_table"]
    #ADVMOD_TABLE = conf_file["configuration"]["advmod"]
    TAG_COL = conf_file["configuration"]["tags_column"]

    # Create obl table 
    print(f"Creating table {OBL_TABLE}")
    create_obl_table(DB_FILE, OBL_TABLE)

    # separate cases 
    print(f"Separating spatial cases for {OBL_TABLE}")
    separate_cases(DB_FILE, OBL_TABLE)

    # Create new tags 
    print(f"Creating new column '{TAG_COL}' for {OBL_TABLE}")
    create_new_tags(DB_FILE, OBL_TABLE, TAG_COL)

    # Add sentences to table
    print(f"Adding 'sentences' to {OBL_TABLE}")
    sentences_to_table(OBL_TABLE, SENTENCES_DB, DB_FILE)

    print("Done!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    run(config)


if __name__ == "__main__":
    main()



