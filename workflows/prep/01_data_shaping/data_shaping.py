#!/usr/bin/env python
# coding: utf-8

# ## Adds sentence_id to transaction table
# Useful later on when ner and timex tags need to be added.

import sqlite3
import pandas as pd
import time
from tqdm import tqdm
import argparse
import json
import configparser


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


def data_shaping(conf_file):

    # Variables from conf file
    # database file path
    DB_FILE = conf_file["configuration"]["database"]
    # transaction table to update with status
    TRANSACTION_TABLE = conf_file["configuration"]["transaction_row_table"]
    HEAD_TABLE = conf_file["configuration"]["transaction_head_table"]

    # ### Connect to database
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # ### Add sentence_id to transaction table
    print(f"Adding sentence_id to {TRANSACTION_TABLE}...")
    start = time.time()

    # add sentence_id column if it doesn't exist
    if not column_exists(cur, TRANSACTION_TABLE, "sentence_id"):
        cur.execute("ALTER TABLE " + TRANSACTION_TABLE +  " ADD COLUMN sentence_id INTEGER")

    # add data
    cur.execute(f"""
    UPDATE {TRANSACTION_TABLE}
    SET sentence_id = (
        SELECT th.sentence_id
        FROM {HEAD_TABLE} th
        WHERE th.id = {TRANSACTION_TABLE}.head_id
    )
    WHERE EXISTS (
        SELECT 1
        FROM {HEAD_TABLE} th
        WHERE th.id = {TRANSACTION_TABLE}.head_id
    );
    """
    )

    conn.commit()
    conn.close()

    end = time.time()
    elapsed_time = end - start
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    print(f"Data shaping done in {minutes} minute(s) and {seconds} second(s).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    data_shaping(config)


if __name__ == "__main__":
    main()






