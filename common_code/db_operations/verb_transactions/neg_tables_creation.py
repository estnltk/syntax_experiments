# imports
import sqlite3
from ..db_udf import udf_lower, register_user_defined_functions

def create_verb_neg_table(cur, transaction_head: str, output_table: str):
    """
    Finds negated verbs from transaction_head table and creates a new table containing necessary attributes from detected transaction_head rows.
    
    Parameters:
            cur - SQLite Cursor-object
            transaction_head - transaction head table name
            output_table - output table name
            
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_table}
    """.format(output_table=output_table))

    cur.execute("""
    CREATE TABLE {output_table} AS
    SELECT DISTINCT
        id,
        verb,
        verb_compound,
        form,
        deprel,
        feats    
    FROM
        {transaction_head} AS tr_head
    WHERE
        instr(tr_head.feats, 'neg') > 0
    """.format(output_table=output_table, transaction_head=transaction_head))


def create_verb_neg_phrase_table(cur, verb_neg: str, transaction_row: str, output_table: str):
    """
    Finds transactions from transaction_row table that match an ID in verb_neg table and creates a new table containing necessary attributes from detected transaction_row rows.
    
    Parameters:
            cur - SQLite Cursor-object
            verb_neg - name of table containing negated verbs found from transactions
            transaction_row - transaction row table name
            output_table - output table name
            
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_table}
    """.format(output_table=output_table))

    cur.execute("""
    CREATE TABLE {output_table} AS
    SELECT
        head_id,
        tr.deprel,
        tr.form,
        lemma,
        tr.feats
    FROM
        {verb_neg} as verb_neg
    INNER JOIN
        {transaction_row} as tr
    ON
        verb_neg.id = tr.head_id
    """.format(output_table=output_table, verb_neg=verb_neg, transaction_row=transaction_row))
    

def create_neg_tables(cur, transaction_head: str, transaction_row: str):
    """
    Creates two negation tables that can be further used in creating negation patterns.
    
    Parameters:
            cur - SQLite Cursor-object
            transaction_head - transaction head table name
            transaction_row - transaction row table name
            
    Result:
            verb_neg - transaction heads from transaction_head that contain a negated verb form
            verb_neg_phrases - transactions from transaction_row that also match a transaction head from verb_neg table
            
    """
    
    create_verb_neg_table(cur, transaction_head, 'verb_neg')
    create_verb_neg_phrase_table(cur, 'verb_neg', transaction_row, 'verb_neg_phrases')
