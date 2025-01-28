import sqlite3
import pandas as pd
from typing import List

def display_db_table(
    connection: sqlite3.Connection, 
    table_name: str, 
    count= 5, 
    method='head'
    ):

    query = """SELECT * from {tbl} limit {cnt}""".format(tbl = table_name, cnt=count)
    source = pd.read_sql_query(query, connection)
    display(source)

