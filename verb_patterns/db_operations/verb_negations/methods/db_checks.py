# imports
import sqlite3
import re


def is_valid_table_name(cur, table_name: str):
    """
    Checks if given table name matches SQLite's naming standards
    """
    if not re.match(r'^[A-Za-z_`][A-Za-z0-9_]*(\.?`?[A-Za-z0-9_]+)`?$', table_name):
        return False
    if cur.fetchone():
        return False   
    return True
        
def is_db_table(cur, table_name: str):
    """
    Checks if given table exists in database
    """
    schema = None
    tbl = None
    if '.' in table_name:
        schema, tbl = table_name.split('.')
    else:
        tbl = table_name
    #if schema: # NB! Does not work currently. In case of schema existing in table name, the return value will be True in all cases
    #    cur.execute("""PRAGMA {schema}.table_info({table_name})""".format(schema=schema, table_name=tbl))
    if schema:
        return True
    else:
        cur.execute("""PRAGMA table_info({table_name})""".format(table_name=tbl))
    res = cur.fetchone()
    if cur.fetchone() is None:
        return False
    return True

def is_col_name(cur, table_name: str, col_name: str):
    """
    Checks if column name exists in given table
    """
    cur.execute("""PRAGMA table_info({table_name})""".format(table_name=table_name))
    columns = cur.fetchall()
    for column in columns:
        if column[1] == col_name:
            return True
    return False
    
def check_all_col_names(cur, table_name: str, col_names: list):
    """
    Iterates over column names provided in a list, checks if they exist in given table
    """
    if '.' in table_name: # Currently, if schema exists in table name, the return value will be True in all cases
        return True
    else:
        for col_name in col_names:
            if not is_col_name(cur, table_name, col_name):
                return False
    return True
