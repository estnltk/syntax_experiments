#!/usr/bin/env python
# coding: utf-8

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


def run(conf_file):

    # database file path
    DB_FILE = conf_file["configuration"]["database"]
    # transaction table to update with status
    TRANSACTION_TABLE = conf_file["configuration"]["transaction_row_table"]
    # column to show morph-syntax errors
    STATUS_COL = conf_file["configuration"]["conflict_column"]

    # ### Connect to database
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # ### Add new status column with empty strings
    if not column_exists(cur, TRANSACTION_TABLE, STATUS_COL):
        cur.execute("ALTER TABLE " + TRANSACTION_TABLE +  f" ADD COLUMN {STATUS_COL} TEXT")

    # ### Update status column based on rules
    # #### This is a temporary fix. There are SQL, text and layer operations to consider.
    print(f"Adding syntax-morph conflicts to '{STATUS_COL}' column in {TRANSACTION_TABLE}...")
    start = time.time()

    # reset values to ensure reruns reflect updates
    cur.execute(f"UPDATE {TRANSACTION_TABLE} SET {STATUS_COL} = '' ")

    # RULES
    # when nsubj is not in nominative/partitive case
    cur.execute(f"""
    UPDATE {TRANSACTION_TABLE}
    SET {STATUS_COL} = 'syntax-morph conflict'
    WHERE deprel = 'nsubj' 
            and ',' || feats || ',' NOT LIKE '%,nom,%' 
            and ',' || feats || ',' NOT LIKE '%,part,%'
    """)

    # when nsubj:cop is not in nominative/partitive case
    cur.execute(f"""
    UPDATE {TRANSACTION_TABLE}
    SET {STATUS_COL} = 'syntax-morph conflict'
    WHERE deprel = 'nsubj:cop' 
            and ',' || feats || ',' NOT LIKE '%,nom,%' 
            and ',' || feats || ',' NOT LIKE '%,part,%'
    """)

    # when obj is not in nominative/genitive/partitive case
    cur.execute(f"""
    UPDATE {TRANSACTION_TABLE}
    SET {STATUS_COL} = 'syntax-morph conflict'
    WHERE deprel = 'obj' 
            and ',' || feats || ',' NOT LIKE '%,nom,%'
            and ',' || feats || ',' NOT LIKE '%,gen,%' 
            and ',' || feats || ',' NOT LIKE '%,part,%'
    """)

    # when advcl has case marking
    cur.execute(f"""
    UPDATE {TRANSACTION_TABLE}
    SET {STATUS_COL} = 'syntax-morph conflict'
    WHERE deprel = 'advcl' 
            and feats!=''
    """)

    # when advmod has case marking
    cur.execute(f"""
    UPDATE {TRANSACTION_TABLE}
    SET {STATUS_COL} = 'syntax-morph conflict'
    WHERE deprel = 'advmod' 
            and feats!=''
    """)

    # when xcomp has case marking
    cur.execute(f"""
    UPDATE {TRANSACTION_TABLE}
    SET {STATUS_COL} = 'syntax-morph conflict'
    WHERE deprel = 'xcomp' 
            and feats!=''
    """)

    # when obl is in nominative case
    cur.execute(f"""
    UPDATE {TRANSACTION_TABLE}
    SET {STATUS_COL} = 'syntax-morph conflict'
    WHERE deprel = 'obl' 
            and ',' || feats || ',' LIKE '%,nom,%'
    """)

    conn.commit()
    conn.close()

    end = time.time()
    elapsed_time = end - start
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(f"Added syntax-morph conflicts in {minutes} minute(s) and {seconds} second(s).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    run(config)


if __name__ == "__main__":
    main()


