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
    """Gets all verb+comp+case plus tags and example sentences from spatial_obl (for hoverplot).
    Calculates
    - how many rows belong to each tag (ELT, A, S, or empty),
    - percentages per tag,
    - and up to 3 random example sentences for each tag+verbcase combination.
    Tables (not permanent):
    base: spatial obl join transaction_head. 0 or 1 for each tag if it is in tags column.
    aggregated: statistics. Groups by verbcase, what is the total count, count for each tag and count for no tag.
    long_counts: transforms wide counts into long format. Each row is verbcase,total,tag, count (each row has count for one tag).
    percentages: percentages for each tag in verbcase (based on long_counts).
    tagged_rows:  creates a normalized tag-level example table (from base).
    ranked_examples: randomly ranks/numbers example rows within each verbcase+tag.
    top_examples: takes 3 random examples per subgroup (verbcase+tag).
    examples_json: packages example rows into JSON arrays.
    final result: joins percentages and examples_json. 
    output format:
    verb	compound	case	tag	count	total	    pct	examples
    v1	    comp1	    ALL     A	    50	    100	    50.0	[...]
    v1	    comp1	    ALL     ELT	20	    100	    20.0	[...]
    
    """

    import sqlite3
    import pandas as pd
    import json

    conn = sqlite3.connect(database)

    query = f"""
    WITH base AS (
        SELECT
            so.verb,
            so.verb_compound,
            so.morph_case,
            so.form,
            so.row_loc,
            so.sentence,
            so.sentence_id,
            th.phrase,
            th.form as verb_form,
            so.tags,

            CASE WHEN so.tags LIKE '%|ELT|%' THEN 1 ELSE 0 END AS is_elt,
            CASE WHEN so.tags LIKE '%|A|%'   THEN 1 ELSE 0 END AS is_a,
            CASE WHEN so.tags LIKE '%|S|%'   THEN 1 ELSE 0 END AS is_s,
            CASE WHEN so.tags = '' OR so.tags IS NULL THEN 1  ELSE 0 END AS is_empty

        FROM {obl_table} so

        LEFT JOIN transaction_head th
          ON so.sentence_id = th.sentence_id
         AND so.verb = th.verb
         AND so.verb_compound = th.verb_compound
        AND so.head_id = th.id
    ),

    aggregated AS (
        SELECT
            verb,
            verb_compound,
            morph_case,

            COUNT(*) AS total,

            SUM(is_elt)   AS elt_count,
            SUM(is_a)     AS a_count,
            SUM(is_s)     AS s_count,
            SUM(is_empty) AS empty_count

        FROM base

        GROUP BY
            verb,
            verb_compound,
            morph_case
    ),

    long_counts AS (

        SELECT
            verb,
            verb_compound,
            morph_case,
            total,
            'ELT' AS tag,
            elt_count AS count
        FROM aggregated

        UNION ALL

        SELECT
            verb,
            verb_compound,
            morph_case,
            total,
            'A',
            a_count
        FROM aggregated

        UNION ALL

        SELECT
            verb,
            verb_compound,
            morph_case,
            total,
            'S',
            s_count
        FROM aggregated

        UNION ALL

        SELECT
            verb,
            verb_compound,
            morph_case,
            total,
            '' AS tag,
            empty_count
        FROM aggregated
    ),

    percentages AS (
        SELECT
            *,
            ROUND(100.0 * count / total, 2) AS pct
        FROM long_counts
    ),

    tagged_rows AS (

        SELECT
            verb,
            verb_compound,
            morph_case,
            sentence,
            sentence_id,
            form,
            phrase,
            verb_form,
            row_loc,
            'ELT' AS tag

        FROM base
        WHERE is_elt = 1

        UNION ALL

        SELECT
            verb,
            verb_compound,
            morph_case,
            sentence,
            sentence_id,
            form,
            phrase,
            verb_form,
            row_loc,
            'A'

        FROM base
        WHERE is_a = 1

        UNION ALL

        SELECT
            verb,
            verb_compound,
            morph_case,
            sentence,
            sentence_id,
            form,
            phrase,
            verb_form,
            row_loc,
            'S'

        FROM base
        WHERE is_s = 1

        UNION ALL

        SELECT
            verb,
            verb_compound,
            morph_case,
            sentence,
            sentence_id,
            form,
            phrase,
            verb_form,
            row_loc,
            '' AS tag

        FROM base
        WHERE is_empty = 1
    ),

    ranked_examples AS (
        SELECT
            verb,
            verb_compound,
            morph_case,
            tag,
            sentence,
            sentence_id,
            form,
            phrase,
            verb_form,
            row_loc,

            ROW_NUMBER() OVER (
                PARTITION BY
                    verb,
                    verb_compound,
                    morph_case,
                    tag
                ORDER BY RANDOM()
            ) AS rn

        FROM tagged_rows
    ),

    top_examples AS (
        SELECT *
        FROM ranked_examples
        WHERE rn <= 3
    ),

    examples_json AS (
        SELECT
            verb,
            verb_compound,
            morph_case,
            tag,
            -- information that is needed for highlighting/marking for plotting
            json_group_array(
                json_object(
                    'sentence', sentence,
                    'sentence_id', sentence_id,
                    'form', form,
                    'phrase', phrase,
                    'verb_form', verb_form,
                    'verb_compound', verb_compound,
                    'row_loc', row_loc
                )
            ) AS examples

        FROM top_examples

        GROUP BY
            verb,
            verb_compound,
            morph_case,
            tag
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






