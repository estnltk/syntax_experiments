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
    
    NB! Table index_tbl_1 should be longer than table index_tbl_2.
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_tbl}
    """.format(output_tbl=output_tbl))
    
    cur.execute("""
    CREATE TABLE {output_tbl}
    AS
    SELECT
        tbl1.{id_col_1} AS idx
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
    