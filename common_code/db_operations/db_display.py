import sqlite3
import pandas as pd

def display_sqlite_as_dataframe(db_path: str, table_name: str, n_rows: int):
    """
    Displays rows of given database table as a pandas DataFrame.
    
    Parameters:
        db_path - path to database file
        table_name - database table name
        n_rows - number of rows to be displayed
    
    Returns:
        Result of the query as a Pandas DataFrame.
    """
    
    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM {table_name} LIMIT {n_rows}"
    df = pd.read_sql_query(query, conn)
    
    return df