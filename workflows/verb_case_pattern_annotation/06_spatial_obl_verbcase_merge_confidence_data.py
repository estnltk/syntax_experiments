#!/usr/bin/env python
# coding: utf-8

# ## Merge confidence values with spatial_obl values to sort them into categories
# Datapoints get :
# - level: n80, n90, n70, n10, n20, n30, -
# - olulisus: p-value
# - annotated word count (form, ekilex_tag=given tag)
# - not annotated word count (form, ekilex_tag is null)
# - unique lemma count (ekilex_tag=given tag)
# Final LINE_DATA_TABLE2 can be used to later extract info for gpt

import sqlite3
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import binom
import copy
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


def get_level(row):
    if row['log2_tag'] >= row[f"log2_y_pos90"]: #kõrgemal 90 joonest
        return "n90"
    elif row['log2_tag'] >= row[f"log2_y_pos80"] and row['log2_tag'] < row[f"log2_y_pos90"]: #kõrgemal 80 joonest
        return "n80"
    elif row['log2_tag'] >= 0 and row['log2_tag'] <= row[f"log2_y_pos70"]: #madalamal 70 ja kõrgemal 0 joonest
        return "n70"
    elif row['log2_tag'] >= row[f"log2_y_pos30"] and row['log2_tag'] <= 0: #madalamal 0 ja kõrgemal 30 joonest
        return "n30"
    elif row['log2_tag'] <= row[f"log2_y_pos20"] and row['log2_tag'] > row[f"log2_y_pos10"]: #madalamal 20 joonest
        return "n20"
    elif row['log2_tag'] <= row[f"log2_y_pos10"]: #madalamal 10 joonest
        return "n10"
    else:
        return "-"


def kv_for_datapoint(row): #(log2_unique_lemmas->unique_lemmas, log2_tag, p)
    #n=2**log2_x : log2_x = log2_unique_lemmas
    # n : unique_lemmas
    # log2_ratio : log2_tag
    # p = 0.8 kui n80
    mapping_level = {"n80": 0.8, "n90": 0.9, "n70":0.7, "n20": 0.2, "n10":0.1, "n30": 0.3}
    if row["level"] != "-":
        n = row["unique_lemmas"]
        log2_ratio = row["log2_tag"]
        p = mapping_level[row["level"]]

        # Compute observed successes from log2(y_pos/y_neg)
        ratio = 2 ** log2_ratio
        k_obs = n * ratio / (1 + ratio)
        # Compute probability P(X >= k_obs), üleval pool joont
        if p>0.5:
            kv_obs = binom.sf(int(round(k_obs)) - 1, int(round(n)), p)
        else: # all pool joont
            kv_obs = binom.cdf(int(round(k_obs)), int(round(n)), p)
        #return n, k_obs, kv_obs
        return round(kv_obs, 5)
    else:
        return "-"



def run(conf_file):

    DATABASE = conf_file["configuration"]["database"]
    TAG = conf_file["configuration"]["target_tag"]
    OBL_TABLE = conf_file["configuration"]["obl_table"]
    TAG_COLUMN = conf_file["configuration"]["tags_column"]
    CONFIDENCE_TABLE = conf_file["configuration"]["confidence_values_table"]

    VERB_COUNTS_TABLE = f"verb_case_counts_{TAG}"
    VERB_CASE_TABLE = f"verb_case_log_{TAG}"
    # tables to save verb+case info with n class
    LINE_DATA_TABLE = f"spatial_obl_{TAG}_n_class_wide"
    LINE_DATA_TABLE2 = f"spatial_obl_{TAG}_n_class"


    # ## Data tables
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # confidence values
    query = f"SELECT * FROM {CONFIDENCE_TABLE}"
    lines_df = pd.read_sql(query, conn)
    # table with verb+case data and unique lemma number
    query = f"SELECT * FROM {VERB_CASE_TABLE}"
    verb_case_log = pd.read_sql(query, conn)

    # ## merge
    new_df = pd.merge(verb_case_log, lines_df, left_on='unique_lemmas', right_on='x')

    # ## Assign n class for each obl verb+case
    new_df["level"] = new_df.apply(get_level, axis=1)


    # ## not_ann_words ja ann_words 
    # (Not lemmas but "form" from spatial_obl table where ekilex_tag is null or not)
    query = f"""
            SELECT verb, verb_compound, morph_case, count(form) as not_ann_words
            FROM {OBL_TABLE}
            WHERE {TAG_COLUMN} = ''
            GROUP BY verb, verb_compound, morph_case;
            """
    df_notag = pd.read_sql(query, conn)

    # Merge with df_log based on verb, verb_compound, morph_case
    new_df = new_df.merge(df_notag, on=['verb', 'verb_compound', 'morph_case'], how='left')

    query = f"""
            SELECT verb, verb_compound, morph_case, count(form) as ann_words
            FROM {OBL_TABLE}
            WHERE {TAG_COLUMN} like '%|{TAG}|%'
            GROUP BY verb, verb_compound, morph_case;
            """
    df_tag = pd.read_sql(query, conn)

    # Merge with df_log based on verb, verb_compound, morph_case
    new_df = new_df.merge(df_tag, on=['verb', 'verb_compound', 'morph_case'], how='left')


    # ## How many unique lemmas are annotated
    query = f"""
        SELECT 
            verb, 
            verb_compound,
            morph_case, 
            COUNT(DISTINCT lemma) AS ann_unique_lemmas
        FROM {OBL_TABLE}
        WHERE {TAG_COLUMN} like '%|{TAG}|%'
        GROUP BY verb, verb_compound, morph_case
    """
    df_ul_tag = pd.read_sql(query, conn)

    # Merge with df_log based on verb, verb_compound, morph_case
    new_df = new_df.merge(df_ul_tag, on=['verb', 'verb_compound', 'morph_case'], how='left')

    # ## How many unique lemmas are not annotated
    query = f"""
        SELECT 
            verb, 
            verb_compound,
            morph_case, 
            COUNT(DISTINCT lemma) AS not_ann_unique_lemmas
        FROM {OBL_TABLE}
        WHERE {TAG_COLUMN} = ''
        GROUP BY verb, verb_compound, morph_case
    """
    df_ul_ntag = pd.read_sql(query, conn)

    new_df = new_df.merge(df_ul_ntag, on=['verb', 'verb_compound', 'morph_case'], how='left')


    # ## olulisus (p-value)
    new_df["olulisus"] = new_df.apply(kv_for_datapoint, axis=1)
    new_df = new_df.rename(columns={'log2_tag': 'log2_ratio'})

    new_df.to_sql(LINE_DATA_TABLE, conn, if_exists="replace", index=False)


    # ## What was the given tag number and other tag number 
    # interesting columns are up to "not_annotated", the rest is for extra information
    query = f"""SELECT tbl1.verb, tbl1.verb_compound, tbl1.morph_case, 
            log2_ratio, unique_lemmas, level, ann_unique_lemmas,
            not_ann_unique_lemmas, olulisus, my_tag, other_tags, annotated, not_annotated,
            log2_annotation, tbl1.verb_case_count, 
            log2_unique_lemmas,synset_count, x, y_pos80, log2_x, y_neg80, log2_y_pos80,
           y_pos90, y_neg90, log2_y_pos90, y_pos70, y_neg70,log2_y_pos70, y_pos30, y_neg30, log2_y_pos30, y_pos20,
           y_neg20, log2_y_pos20, y_pos10, y_neg10, log2_y_pos10, not_ann_words, ann_words
           --,{VERB_COUNTS_TABLE}.verb_case_count as loc_verb_case_count

                FROM {LINE_DATA_TABLE} as tbl1
                left join 
                {VERB_COUNTS_TABLE} 
                on 
                tbl1.verb = {VERB_COUNTS_TABLE}.verb and
                tbl1.verb_compound = {VERB_COUNTS_TABLE}.verb_compound and
                tbl1.morph_case = {VERB_COUNTS_TABLE}.morph_case
                """

    df = pd.read_sql(query, conn)

    # verb_case_count peaks olema sama, mis loc_verb_case_count, ehk võib võtta ühe
    # ann_words peaks olema sama, mis my_tag (NaN vs 0 ka)
    # not_ann_words peaks olema sama, mis not_annotated (Nan vs 0 ka)

    # ## save to database
    df.to_sql(LINE_DATA_TABLE2, conn, if_exists="replace", index=False)

    # example query to later read in 
    #query = f"""SELECT verb, verb_compound, morph_case, log2_ratio, unique_lemmas, level, 
    #            ann_unique_lemmas, not_ann_unique_lemmas, olulisus,
    #            my_tag, other_tags, annotated, not_annotated
    #            FROM {LINE_DATA_TABLE2}
    #            """
    #df = pd.read_sql(query, conn)

    conn.close()
    print("Done!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    run(config)


if __name__ == "__main__":
    main()





