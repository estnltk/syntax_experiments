#!/usr/bin/env python
# coding: utf-8

import sqlite3
import pandas as pd
import os
import re
import time
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


def ner_timex_to_table(input_table, cursor1, cursor2, conn1, conn2):
    # Step 1: Retrieve data from database1
    cursor1.execute("SELECT sentence_id, ner_tag, loc FROM ner")
    ners = cursor1.fetchall()  # List of (sentence_id, ner_tag, loc)

    # Step 2: add new column to database2 table
    if not column_exists(cursor2, input_table, "ner_tag"):
        cursor2.execute("ALTER TABLE " + input_table +  " ADD COLUMN ner_tag TEXT")

    # Step 3: Create a temporary table
    cursor2.execute("CREATE TEMP TABLE temp_ner (sentence_id INT, ner_tag TEXT, loc INT)")

    # Step 4: Insert all values into the temp table
    cursor2.executemany("INSERT INTO temp_ner (sentence_id, ner_tag, loc) VALUES (?, ?, ?)", ners)

    cursor2.execute(f"""
        UPDATE {input_table}
        SET ner_tag = temp_ner.ner_tag
        FROM temp_ner
        WHERE {input_table}.sentence_id = temp_ner.sentence_id and {input_table}.loc=temp_ner.loc;
    """)
    
    conn2.commit()
    
    
    # Step 1: Retrieve data from database1
    cursor1.execute("SELECT sentence_id, timex_type, loc FROM timex")
    timexes = cursor1.fetchall()  # List of (sentence_id, timex_type, loc)

    # Step 2: add new column to database2 table
    if not column_exists(cursor2, input_table, "timex_tag"):
        cursor2.execute("ALTER TABLE " + input_table +  " ADD COLUMN timex_tag TEXT")

    # Step 3: Create a temporary table
    cursor2.execute("CREATE TEMP TABLE temp_timex (sentence_id INT, timex_type TEXT, loc INT)")

    # Step 4: Insert all values into the temp table
    cursor2.executemany("INSERT INTO temp_timex (sentence_id, timex_type, loc) VALUES (?, ?, ?)", timexes)

    # Step 3: Perform a fast join-based update
    cursor2.execute(f"""
        UPDATE {input_table}
        SET timex_tag = temp_timex.timex_type
        FROM temp_timex
        WHERE {input_table}.sentence_id = temp_timex.sentence_id and {input_table}.loc=temp_timex.loc;
    """)
    
    conn2.commit()

    conn1.close()
    conn2.close()


def run(conf_file):
    # ### Variables from conf file
    # database file path
    DB_FILE = conf_file["configuration"]["database"]
    NER_TIMEX_DB = conf_file["configuration"]["ner_timex_db"]
    # transaction table to update with status
    TRANSACTION_TABLE =  conf_file["configuration"]["transaction_row_table"]

    # ### Connect to databases
    conn_source = sqlite3.connect(NER_TIMEX_DB)  # Source database
    conn_target = sqlite3.connect(DB_FILE)  # Target database
    cursor_source = conn_source.cursor()
    cursor_target = conn_target.cursor()


    # ### Add ner and timex tags
    print("Adding ner and timex tags to table...")
    start = time.time()

    ner_timex_to_table(TRANSACTION_TABLE, cursor_source, cursor_target, conn_source, conn_target)

    conn_source.close()
    conn_target.close()

    end = time.time()
    elapsed_time = end - start
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"Added ner and timex tags in {minutes} minute(s) and {seconds} second(s)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    run(config)


if __name__ == "__main__":
    main()

