#!/usr/bin/env python
# coding: utf-8

import sqlite3
import pandas as pd
from tqdm import tqdm
import numpy as np
from scipy.stats import binom_test
from scipy.stats import binom
import argparse
import json
import configparser

np.seterr(invalid='ignore')

# FUNCTIONS

def load_config(path):
    """Loads config.
    """
    config = configparser.ConfigParser()
    status = config.read(path) 
    assert status == [path]
    return config

def examples_table(database, obl_table):
    """Gets all verb+comp+case plus tags and example sentences from spatial_obl (for hoverplot)"""
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    query = f"""
    WITH base AS (
        SELECT
            verb,
            verb_compound,
            morph_case,
            form,
            sentence,
            --tags,
            CASE WHEN tags LIKE '%|ELT|%' THEN 1 ELSE 0 END AS is_elt,
            CASE WHEN tags LIKE '%|A|%'   THEN 1 ELSE 0 END AS is_a,
            CASE WHEN tags LIKE '%|S|%'   THEN 1 ELSE 0 END AS is_s
        FROM {obl_table}
    ),

    aggregated AS (
        SELECT
            verb,
            verb_compound,
            morph_case,
            COUNT(*) AS total,
            SUM(is_elt) AS elt_count,
            SUM(is_a)   AS a_count,
            SUM(is_s)   AS s_count
        FROM base
        GROUP BY verb, verb_compound, morph_case
    ),

    -- Convert wide to long (one row per tag)
    long_counts AS (
        SELECT verb, verb_compound, morph_case, total, 'ELT' AS tag, elt_count AS count FROM aggregated
        UNION ALL
        SELECT verb, verb_compound, morph_case, total, 'A',   a_count   FROM aggregated
        UNION ALL
        SELECT verb, verb_compound, morph_case, total, 'S',   s_count   FROM aggregated
    ),

    percentages AS (
        SELECT
            *,
            ROUND(100.0 * count / total, 2) AS pct
        FROM long_counts
    ),

    -- Flatten rows per tag for sampling examples
    tagged_rows AS (
        SELECT verb, verb_compound, morph_case, sentence, form, 'ELT' AS tag
        FROM base WHERE is_elt = 1
        UNION ALL
        SELECT verb, verb_compound, morph_case, sentence, form, 'A'
        FROM base WHERE is_a = 1
        UNION ALL
        SELECT verb, verb_compound, morph_case, sentence, form, 'S'
        FROM base WHERE is_s = 1
    ),

    ranked_examples AS (
        SELECT
            verb,
            verb_compound,
            morph_case,
            tag,
            sentence,
            form,
            ROW_NUMBER() OVER (
                PARTITION BY verb, verb_compound, morph_case, tag
                ORDER BY RANDOM()
            ) AS rn
        FROM tagged_rows
    ),

    top_examples AS (
        SELECT *
        FROM ranked_examples
        WHERE rn <= 3
    ),

    -- Aggregate examples into JSON array (Plotly-friendly)
    examples_json AS (
        SELECT
            verb,
            verb_compound,
            morph_case,
            tag,
            json_group_array(
                json_object(
                    'sentence', sentence,
                    'form', form,
                    'highlighted',
                        REPLACE(sentence, form,
                            '<span style="color:yellow;font-weight:bold;">' || form || '</span>'
                        )
                )
            ) AS examples
        FROM top_examples
        GROUP BY verb, verb_compound, morph_case, tag
    )

    SELECT
        p.verb,
        p.verb_compound,
        p.morph_case,
        p.tag,
        p.count,
        p.total,
        p.pct,
        e.examples

    FROM percentages p
    LEFT JOIN examples_json e
      ON p.verb = e.verb
     AND p.verb_compound = e.verb_compound
     AND p.morph_case = e.morph_case
     AND p.tag = e.tag

    -- Order tags within each verbcase by percentage
    ORDER BY
        p.verb,
        p.verb_compound,
        p.morph_case,
        p.pct DESC;
    """

    df2 = pd.read_sql(query, conn)
    
    conn.close()
    return df2



def run(conf_file):
    
    DATABASE = conf_file["configuration"]["database"]
    OBL_TABLE = conf_file["configuration"]["obl_table"]

    examples_df = examples_table(DATABASE, OBL_TABLE)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    examples_df.to_sql("spatial_obl_plotting_examples", conn, if_exists="replace", index=False)

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






