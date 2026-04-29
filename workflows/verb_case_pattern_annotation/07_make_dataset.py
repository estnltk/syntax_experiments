#!/usr/bin/env python
# coding: utf-8


import sqlite3
import pandas as pd
import os
import csv
import argparse
import json
import configparser


# ## Functions

def load_config(path):
    """Loads config.
    """
    config = configparser.ConfigParser()
    status = config.read(path) 
    assert status == [path]
    return config


def run(conf_file):

    DATABASE = conf_file["configuration"]["database"]
    OBL_TABLE = conf_file["configuration"]["obl_table"]
    TAG = conf_file["configuration"]["target_tag"]
    CLASS = conf_file["configuration"]["class"]
    # how many unique lemmas per verb+comp+case
    LEMMA_LIMIT = conf_file["configuration"]["lemma_limit"].strip()
    DIR_DATA = conf_file["configuration"]["dir_data"] 

    LINE_DATA_TABLE = f"spatial_obl_{TAG}_n_class"
    FILTERED_CLASS_TABLE = f"spatial_obl_{TAG}_{CLASS}"
    FNAME = f"{TAG}_{CLASS}_{LEMMA_LIMIT}"
    LARGE_DATA_FILE = f"{DIR_DATA}/{FNAME}.csv"
    LARGE_DATA_FILE_SORTED = f"{DIR_DATA}/{FNAME}_sorted.csv"

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # ### graafiku punktide info
    level_str = f"where level = '{CLASS}'"
    if CLASS == "n50":
        level_str = f"where level = 'n30' or level = 'n70'"

    query = f"""SELECT verb, verb_compound, morph_case, log2_ratio, level,unique_lemmas, ann_unique_lemmas, 
                not_ann_unique_lemmas, olulisus, my_tag, other_tags, annotated, not_annotated, verb_case_count
                FROM {LINE_DATA_TABLE}
                {level_str}
                """
    filtered_class = pd.read_sql(query, conn)
    filtered_class.to_sql(FILTERED_CLASS_TABLE, conn, if_exists="replace", index=False)

    # ### võtta spatial_obl tabelist näitelaused koos vajaliku infoga
    # spatial obl tabelist lõksud, mis on spatial_obl_{tag}_n_class tabelis
    # iga lõksu kohta max 500 lemmat ja iga unikaalse lemma kohta 1 näide

    limit_str = ""
    if LEMMA_LIMIT != 'max':
        LEMMA_LIMIT = int(LEMMA_LIMIT)
        limit_str = f" WHERE rn_group_limit <= {LEMMA_LIMIT} "

    query = f"""
    WITH cleaned AS (
        -- Step 1 & 2: match subset table + remove rows with timex_tag NOT NULL
        SELECT
            d.head_id,
            d.row_loc as head_loc,
            d.form,
            d.lemma,
            d.verb,
            d.verb_compound,
            d.morph_case,
            d.sentence,
            d.sentence_id,
            d.timex_tag,
            d.ekilex_tag,
            d.ner_tag,
            tags
        FROM {OBL_TABLE} AS d
        JOIN {FILTERED_CLASS_TABLE} AS s
          ON d.verb = s.verb
         AND d.verb_compound = s.verb_compound
         AND d.morph_case = s.morph_case
    ),

    distinct_lemmas AS (
        -- Step 3 & 4: for each lemma, pick ONE sentence deterministically
        -- Collects all sentences for (verb, verb_compound, morph_case, lemma), orders by sentence_id, assigns rn_per_lemma
        -- for one (verb, verb_compound, morph_case, lemma) example:
        -- sentence_id 10 → rn_per_lemma = 1
        -- sentence_id 25 → rn_per_lemma = 2
        -- sentence_id 42 → rn_per_lemma = 3 ...
        -- in next part rm_per_lemma = 1 then selects the first row per lemma

        SELECT 
            *,
            ROW_NUMBER() OVER (
                PARTITION BY verb, verb_compound, morph_case, lemma
                ORDER BY sentence_id   -- choose best or earliest sentence
            ) AS rn_per_lemma
        FROM cleaned
    ),

    limited AS (
        -- Step 5: limit to 500 unique lemmas per (verb, verb_compound, morph_case)
        -- assigns numbers like:
        -- lemma A → 1
        -- lemma B → 2  ...
        -- lemma ZZZ → 501

        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY verb, verb_compound, morph_case
                ORDER BY lemma        -- choose 500 lexicographically smallest lemmas
            ) AS rn_group_limit
        FROM distinct_lemmas
        WHERE rn_per_lemma = 1      -- keep only one sentence per lemma
    )

    -- Step 6: final output
    -- rn_group_limit <= 500 cuts off at the 500th lemma. Lemmas that have rn_group_limit 501, 502, ... are not included
    SELECT
        sentence_id,
        head_id,
        head_loc, 
        verb,
        verb_compound,
        morph_case,
        lemma,
        form,
        sentence,
        tags,
        timex_tag,
        ekilex_tag,
        ner_tag
    FROM limited
    {limit_str}
    ORDER BY verb, verb_compound, morph_case, lemma;

    """

    spatial_obl_ex = pd.read_sql(query, conn)

    # saving to csv
    spatial_obl_ex.to_csv(LARGE_DATA_FILE_SORTED, encoding="utf-8", index = False,sep=",", quoting=csv.QUOTE_MINIMAL)

    # saving to database
    spatial_obl_ex.to_sql(FNAME, conn, if_exists="replace", index=False)

    # shuffle
    df = spatial_obl_ex.sample(frac=1)
    df.to_csv(LARGE_DATA_FILE, encoding="utf-8", index = False,sep=",", quoting=csv.QUOTE_MINIMAL)

    conn.close()
    print(f"{FNAME} done!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    run(config)


if __name__ == "__main__":
    main()