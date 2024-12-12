# imports
import sqlite3


def index_difference(cur, index_tbl_1: str, id_col_1: str, index_tbl_2: str, id_col_2: str, output_tbl: str):
    """
    Computes set difference between indexes, that are all rows in index_tbl_1 that are not present in index_tbl_2
    Creates a new table of resulting indexes. This table can be later used to filter transactions.
    
    Parameters:
            cur - SQLite Cursor-object
            index_tbl_1 - name of the table containing all indexes
            id_col_1 - ID column name in index_tbl_1
            index_tbl_2 - name of the table containing head indexes that are to be filtered out
            id_col_2  - ID column name in index_tbl_2
            output_tbl - output table name
    
    Table index_tbl_1 should be longer than table index_tbl_2.
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_tbl}
    """.format(output_tbl=output_tbl))
    
    cur.execute("""
    CREATE TABLE {output_tbl}
    AS
    SELECT
        tbl1.{id_col_1} AS head_id
    FROM
        {index_tbl_1} AS tbl1
    LEFT JOIN
        {index_tbl_2} AS tbl2
    ON
        tbl1.{id_col_1}=tbl2.{id_col_2}
    WHERE
        tbl2.{id_col_2} isnull
    """.format(output_tbl=output_tbl, id_col_1=id_col_1, index_tbl_1=index_tbl_1, index_tbl_2=index_tbl_2, id_col_2=id_col_2))
    cur.connection.commit()

def create_filtered_transaction_row(cur, index_tbl: str, id_col: str, transaction_row: str, output_tr_row: str):
    """
    Creates a copy of transaction_row table where only transactions with selected head ID-s are kept. Result is filtered transaction_row table.
    
    Parameters:
            cur - SQLite Cursor-object
            index_tbl - name of index table containing ID-s of transactions that are to be kept. 
            id_col - ID column name in index_tbl.
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
        {index_tbl} AS ids
    INNER JOIN
        {transaction_row} AS tr
    ON
       ids.{id_col}=tr.head_id
    """.format(output_tr_row=output_tr_row, index_tbl=index_tbl, transaction_row=transaction_row, id_col=id_col))
    cur.connection.commit()
    
def create_filtered_transaction_head(cur, index_tbl: str, id_col: str, transaction_head: str, output_tr_head: str):
    """
    Creates a copy of transaction_head table where only transactions with selected head ID-s are kept. Result is filtered transaction_head table.
    
    Parameters:
            cur - SQLite Cursor-object
            index_tbl - name of index table containing ID-s of transactions that are to be kept. 
            id_col - ID column name in index_tbl.
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
        {index_tbl} AS ids
    INNER JOIN
        {transaction_head} AS tr_head
    ON
        ids.{id_col}=tr_head.id
    """.format(output_tr_head=output_tr_head, index_tbl=index_tbl, transaction_head=transaction_head, id_col=id_col))
    cur.connection.commit()