# imports
import sqlite3
#from .db_checks import is_valid_table_name, is_db_table, check_all_col_names


def extract_negations(cur, transaction_head: str, transaction_row: str, patterns: str, output_table: str, overwrite=False):
    """
    Extracts negation phrase indexes from given transactions according to negation patterns.
    Saves negation pattern IDs and IDs of negation phrase matches in output table.
    
    Parameters
    ----------
    cur:
        database Cursor object
    transaction_head: str
        transaction head table name
    transaction_row: str
        transaction row table name
    patterns: str
        negation patterns table name
    output_table: str
        name of output table being created
    overwrite: bool
        whether an already existing output table should be overwritten
    
    Result
    ------
    New table that contains negation pattern IDs and IDs of negation phrase matches.
    
    Andmebaasi/tabelite struktuur on kirjeldatud (link)
    """
    
    # check the validity of all table names
    if not is_valid_table_name(cur, transaction_head):
        raise ValueError("Invalid transaction head table name")
    if not is_valid_table_name(cur, transaction_row):
        raise ValueError("Invalid transaction row table name")
    if not is_valid_table_name(cur, patterns):
        raise ValueError("Invalid patterns table name")
    if not is_valid_table_name(cur, output_table):
        raise ValueError("Invalid output table name")
        
    # check if input tables exist
    if not is_db_table(cur, transaction_head):
        raise ValueError("Transaction head table does not exist")
    if not is_db_table(cur, transaction_row):
        raise ValueError("Transaction row table does not exist")
    if not is_db_table(cur, patterns):
        raise ValueError("Patterns table does not exist")
    
    # check the validity of all column names of tables
    if not check_all_col_names(cur, transaction_head, ['id', 'form', 'deprel', 'feats']):
        raise ValueError("Not all required transaction head table column names exist")
    if not check_all_col_names(cur, transaction_row, ['head_id', 'form', 'deprel', 'feats']):
        raise ValueError("Not all required transaction row table column names exist")
    if not check_all_col_names(cur, patterns, ['pat_id', 'form', 'deprel']):
        raise ValueError("Not all required patterns table column names exist")
        
    # check if output table already exists and if it can be overwritten
    if is_db_table(cur, output_table):
        if overwrite:
            cur.execute("""
            DROP TABLE IF EXISTS {output_table}
            """.format(output_table=output_table))
        else:
            raise ValueError("Output table already exists")
    
    # creating output table
    cur.execute("""
       CREATE TABLE {output_table} AS
       SELECT DISTINCT
           pat_id,
           head_id
       FROM
           {patterns} AS pat
       INNER JOIN
           {transaction_row} AS phrases
       ON
           pat.form = phrases.form
       AND
           pat.deprel = phrases.deprel
       AND
           instr(phrases.feats, 'neg') > 0
       """.format(output_table=output_table, patterns=patterns, transaction_row=transaction_row))

    cur.execute("""
       INSERT INTO {output_table}
       SELECT DISTINCT
           pat_id,
           verbs.id AS head_id
       FROM
           {patterns} AS pat
       INNER JOIN
           {transaction_head} AS verbs
       ON
           pat.form = verbs.form
       AND
           pat.deprel = verbs.deprel
       AND
           instr(verbs.feats, 'neg') > 0
       """.format(output_table=output_table, patterns=patterns, transaction_head=transaction_head))
    
    cur.connection.commit()