# imports
import sqlite3


def remove_deprel_from_transaction_row(cur, transaction_row: str, deprel: str):
    """
    Removes rows from transaction_row table that contain given deprel. Result is transaction_row table without given deprel values.
    
    Parameters:
                cur - SQLite Cursor-object
                transaction_row - transaction_row table name
                deprel - deprel value to be removed
    """
    cur.execute("""
    DELETE FROM {transaction_row} WHERE deprel='{deprel}'
    """.format(transaction_row=transaction_row, deprel=deprel))
    cur.connection.commit()

def remove_aux_verbs(cur, transaction_row: str):
    """
    Removes rows from transaction_row table that contain an auxiliary verb. Result is transaction_row table without auxiliary verbs.
    
    Parameters:
            cur - SQLite Cursor-object
            transaction_row - transaction_row_table name
    """
    cur.execute("""
    DELETE FROM {transaction_row} WHERE deprel='aux' AND lemma!='ei'
    """.format(transaction_row=transaction_row))
    cur.connection.commit()

def create_filtered_head_id_tbl(cur, all_ids_tbl: str, head_id_col1: str, ids_to_filter_tbl: str, head_id_col2: str, output_tbl: str):
    """
    Creates a new table that contains head ID-s of transactions that should be kept after filtering. Result is a table of selected head ID-s.
    
    Parameters:
            cur - SQLite Cursor-object
            all_ids_tbl - name of the table containing all head ID-s
            head_id_col1 - head ID column name in all_ids_tbl
            ids_to_filter_tbl - name of the table containing head ID-s that are to be filtered out
            head_id_col2  - head ID column name in ids_to_filter_tbl
            output_tbl - output table name
    
    Table all_ids_tbl should be longer than table ids_to_filter_tbl.
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_tbl}
    """.format(output_tbl=output_tbl))
    
    cur.execute("""
    CREATE TABLE {output_tbl}
    AS
    SELECT
        all_ids.{head_id_col1} AS head_id
    FROM
        {all_ids_tbl} AS all_ids
    LEFT JOIN
        {ids_to_filter_tbl} AS ids_to_filter
    ON
        all_ids.{head_id_col1}=ids_to_filter.{head_id_col2}
    WHERE
        ids_to_filter.{head_id_col2} isnull
    """.format(output_tbl=output_tbl, head_id_col1=head_id_col1, all_ids_tbl=all_ids_tbl, ids_to_filter_tbl=ids_to_filter_tbl, head_id_col2=head_id_col2))
    cur.connection.commit()

def create_filtered_transaction_row(cur, head_ids: str, head_id_col: str, transaction_row: str, output_tr_row: str):
    """
    Creates a copy of transaction_row table where only transactions with selected head ID-s are kept. Result is filtered transaction_row table.
    
    Parameters:
            cur - SQLite Cursor-object
            head_ids - name of head ID table containing head ID-s of transactions that are to be kept. 
            head_id_col - head ID column name in head_ids table.
            transaction_row - transaction_row table name
            output_tr_row - output transaction_row table name
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_tr_row}
    """.format(output_tr_row=output_tr_row))

    cur.execute("""
    CREATE TABLE {output_tr_row}
    AS
    SELECT DISTINCT
        tr.id,
        tr.head_id,
        tr.loc,
        tr.loc_rel,
        tr.deprel,
        tr.form,
        tr.lemma,
        tr.feats,
        tr.parent_loc,
        tr.pos
    FROM
        {head_ids} AS ids
    INNER JOIN
        {transaction_row} AS tr
    ON
       tr.head_id=ids.{head_id_col}
    """.format(output_tr_row=output_tr_row, head_ids=head_ids, transaction_row=transaction_row, head_id_col=head_id_col))
    cur.connection.commit()
    
def create_filtered_transaction_head(cur, head_ids: str, head_id_col: str, transaction_head: str, output_tr_head: str):
    """
    Creates a copy of transaction_head table where only transactions with selected head ID-s are kept. Result is filtered transaction_head table.
    
    Parameters:
            cur - SQLite Cursor-object
            head_ids - name of head ID table containing head ID-s of transactions that are to be kept. 
            head_id_col - head ID column name in head_ids table.
            transaction_head - transaction_head table name
            output_tr_head - output transaction_head table name
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_tr_head}
    """.format(output_tr_head=output_tr_head))

    cur.execute("""
    CREATE TABLE {output_tr_head}
    AS
    SELECT DISTINCT
        tr_head.id,
        tr_head.sentence_id,
        tr_head.loc,
        tr_head.verb,
        tr_head.verb_compound,
        tr_head.form,
        tr_head.deprel,
        tr_head.feats
    FROM
        {head_ids} AS ids
    INNER JOIN
        {transaction_head} AS tr_head
    ON
        ids.{head_id_col}=tr_head.id
    """.format(output_tr_head=output_tr_head, head_ids=head_ids, transaction_head=transaction_head, head_id_col=head_id_col))
    cur.connection.commit()