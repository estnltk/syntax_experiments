# imports
import sqlite3
from ..db_udf import udf_lower, register_user_defined_functions

def create_neg_patterns_table(cur, verb_neg: str, verb_neg_phrases: str, output_table: str):
    """
    Finds negation patterns from tables containing negated verb forms ('olema') and transactions containing a negation word ('ei', 'ära'). Creates a new table of negation patterns
    
    Parameters:
            cur - SQLite Cursor-object
            verb_neg - name of table containing negated verbs found from transactions
            verb_neg_phrases - name of table containing transactions that contain a negated verb form
            output_table - output table name
            
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_table}
    """.format(output_table=output_table))

    cur.execute("""
    CREATE TABLE {output_table} (
        pat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        form TEXT,
        deprel TEXT
    )
    """.format(output_table=output_table))

    cur.execute("""
    INSERT INTO {output_table} (
        form,
        deprel
    )
    SELECT DISTINCT
        udf_lower(form),
        deprel
    FROM
        {verb_neg}
    WHERE
        verb='olema'
    AND
        instr(udf_lower(form), 'pol') > 0
    AND
        instr(udf_lower(feats), 'neg') > 0
    """.format(output_table=output_table, verb_neg=verb_neg))

    cur.execute("""
    INSERT INTO {output_table} (
        form,
        deprel
    )
    SELECT DISTINCT
        udf_lower(form),
        deprel
    FROM
        {verb_neg_phrases}
    WHERE
        lemma='ei'
    AND
        instr(feats, 'neg') > 0
    AND
        deprel='aux'
    """.format(output_table=output_table, verb_neg_phrases=verb_neg_phrases))

    cur.execute("""
    INSERT INTO {output_table} (
        form,
        deprel
    )
    SELECT DISTINCT
        udf_lower(form),
        deprel
    FROM
        {verb_neg_phrases}
    WHERE
        lemma='ära'
    AND
        instr(feats, 'neg') > 0
    AND
        deprel='aux'
    """.format(output_table=output_table, verb_neg_phrases=verb_neg_phrases))
    cur.connection.commit()


def create_neg_feats_table(cur, neg_patterns: str, verb_neg: str, verb_neg_phrases: str, output_table: str):
    """
    Finds and creates a new table for 'feats' column values of negation (pattern) occurrences among transactions.
    
    Parameters:
            cur - SQLite Cursor-object
            neg_patterns - name of negation patterns table
            verb_neg - name of table containing negated verbs found from transactions
            verb_neg_phrases - name of table containing transactions that contain a negated verb form
            output_table - output table name
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_table}
    """.format(output_table=output_table))

    cur.execute("""
    CREATE TABLE {output_table} (
        pat_id INTEGER,
        feats TEXT
    )
    """.format(output_table=output_table))

    cur.execute("""
    INSERT INTO {output_table} (
        pat_id,
        feats
        )
    SELECT DISTINCT
        pat_id,
        feats
    FROM
    (
        SELECT
            pat_id,
            form,
            deprel
        FROM
            {neg_patterns} AS pat
    ) AS tbl
    INNER JOIN
        {verb_neg} AS verb_neg
    ON
        (tbl.form=udf_lower(verb_neg.form) AND tbl.deprel=verb_neg.deprel)   
    WHERE
        verb_neg.verb='olema'
    AND
        instr(udf_lower(verb_neg.form), 'pol') > 0
    AND
        instr(udf_lower(feats), 'neg') > 0
    """.format(output_table=output_table, neg_patterns=neg_patterns, verb_neg=verb_neg))

    cur.execute("""
    INSERT INTO {output_table} (
        pat_id,
        feats
    )
    SELECT DISTINCT
        pat_id,
        feats
    FROM
    (
        SELECT
            pat_id,
            form,
            deprel
        FROM
            {neg_patterns} AS pat
    ) as tbl
    INNER JOIN
        {verb_neg_phrases} AS phrases
    ON
        (tbl.form=udf_lower(phrases.form) AND tbl.deprel=phrases.deprel)
    WHERE
        lemma='ei'
    AND
        instr(feats, 'neg') > 0
    AND
        phrases.deprel='aux'
    """.format(output_table=output_table, neg_patterns=neg_patterns, verb_neg_phrases=verb_neg_phrases))

    cur.execute("""
    INSERT INTO {output_table} (
        pat_id,
        feats
    )
    SELECT DISTINCT
        pat_id,
        feats
    FROM
    (
        SELECT
            pat_id,
            form,
            deprel
        FROM
            {neg_patterns} AS pat
    ) AS tbl
    INNER JOIN
        {verb_neg_phrases} AS phrases
    ON
        (tbl.form=udf_lower(phrases.form) AND tbl.deprel=phrases.deprel)
    WHERE
        lemma='ära'
    AND
        instr(feats, 'neg') > 0
    AND
        phrases.deprel='aux'
    """.format(output_table=output_table, neg_patterns=neg_patterns, verb_neg_phrases=verb_neg_phrases))
    cur.connection.commit()
    
def create_neg_patterns(conn, cur, verb_neg: str, verb_neg_phrases: str):
    """
    Creates negation patterns table and corresponding 'feats' values table.
    
    Parameters:
            conn - SQLite connection
            cur - SQLite Cursor-object
            verb_neg - name of table containing negated verbs found from transactions
            verb_neg_phrases - name of table containing transactions that contain a negated verb form
            
    Result:
            neg_patterns - negation patterns
            neg_feats - 'feats' column values that occur together with a negation pattern
            
    """
    register_user_defined_functions(conn=conn)
    
    create_neg_patterns_table(cur, verb_neg, verb_neg_phrases, 'neg_patterns')
    create_neg_feats_table(cur, 'neg_patterns', verb_neg, verb_neg_phrases, 'neg_feats')
    