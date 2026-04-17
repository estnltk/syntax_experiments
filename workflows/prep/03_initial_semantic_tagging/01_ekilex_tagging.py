#!/usr/bin/env python
# coding: utf-8

import sqlite3
import pandas as pd
import os
import re
import time
from tqdm import tqdm
from collections import defaultdict
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


def word_semtype_fun(directory_str):
    word_semtype = [] # tuples of semtype and word, i.e. (amount, aegsamini)
    
    directory = os.fsencode(directory_str)
    
    for file in os.listdir(directory):
        file_name = os.fsdecode(file)
        filepath = directory_str + '/' + file_name
        semtype = re.findall(r"^(?:adv_)?(.+?)\.[^.]+$", file_name)
        with open(filepath, "r", encoding="utf-8") as f:
            words = f.read().splitlines()
            for word in words:
                word_semtype.append((semtype[0], word))  
    return word_semtype


def find_duplicates(data):
    word_to_categories = defaultdict(set)
    for category, word in data:
        word_to_categories[word].add(category)
    return {w: c for w, c in word_to_categories.items() if len(c) > 1}


def semtype_to_db(deprel, table_name, semtypes, db_file, tag_col):
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Step 1: add new column to database table
    if not column_exists(cursor, table_name, tag_col):
        cursor.execute("ALTER TABLE " + table_name + f" ADD COLUMN {tag_col} TEXT")

    # Step 2: add word + semantic tag to temporary table
    cursor.execute(f"CREATE TEMP TABLE IF NOT EXISTS temp_updates (lemma TEXT PRIMARY KEY, {tag_col} TEXT)")
    cursor.executemany(f"INSERT INTO temp_updates ({tag_col}, lemma) VALUES (?, ?)", semtypes)

    # Step 3: Add temporary table info to database table
    #ps, pronouns are excluded for spatial obliques
    cursor.execute(f"""
        UPDATE {table_name}
        SET {tag_col} = (SELECT {tag_col} FROM temp_updates WHERE temp_updates.lemma = {table_name}.lemma)
        WHERE pos != 'P' 
                AND EXISTS (SELECT 1 FROM temp_updates WHERE temp_updates.lemma = {table_name}.lemma)
                AND deprel='{deprel}'
    """)

    conn.commit()
    conn.close()


def run(conf_file):

    # database file path
    DB_FILE = conf_file["configuration"]["database"]
    # transaction table to update with status
    TRANSACTION_TABLE = conf_file["configuration"]["transaction_row_table"]
    EKILEX_COL = "ekilex_tag"
    # DIRs for ekilex tag files
    DIRECTORY_OBL =  conf_file["configuration"]["dir_obl_files"]
    DIRECTORY_ADVMOD =  conf_file["configuration"]["dir_advmod_files"]

    # ### Save word and semantic type to dict
    word_semtype_obl = word_semtype_fun(DIRECTORY_OBL)
    word_semtype_adv = word_semtype_fun(DIRECTORY_ADVMOD)

    # ### Check if any lemma is in multiple categories
    duplicates = find_duplicates(word_semtype_obl)
    assert duplicates == {}, f"obl words found in multiple categories: {duplicates}"
    duplicates = find_duplicates(word_semtype_adv)
    assert duplicates == {}, f"advmod words found in multiple categories: {duplicates}"

    print("Adding ekilex tags to table...")
    # ### Add semantic types to lemmas in the database
    semtype_to_db("obl", TRANSACTION_TABLE, word_semtype_obl, DB_FILE, EKILEX_COL)
    semtype_to_db('advmod', TRANSACTION_TABLE, word_semtype_adv, DB_FILE, EKILEX_COL)
    print("Done!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    run(config)


if __name__ == "__main__":
    main()

