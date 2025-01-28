import sqlite3
from typing import List

def update_table(
    connection: sqlite3.Connection, 
    table_name: str, 
    column_name: str, 
    new_value: str, 
    condition: str
    ):
    """
    Updates one column value to a given value in a table on a condition.
    Parameters:
        connection: sqlite3.Connection - The SQLite database connection object.
        table_name: str - The name of the source table.
        column_name: str - The name of the column that is updated.
        new_value: str - The new value for the column.
        condition: str - The condition(s) for updating the value.
    """
    c = connection.cursor()
    
    c.execute("""
    UPDATE {table}
    SET {column} = {value}
    WHERE {condition}
    """.format(table=table_name, column=column_name, value=new_value, condition=condition)
            )
    connection.commit()


def create_count_table_distinct(
    connection: sqlite3.Connection, 
    source_table_name: str, 
    result_table_name: str, 
    selected_columns: List[str], 
    count_column: str, 
    count_col_name: str, 
    condition: str, 
    group_by_columns: List[str]
    ):

    """
    Creates a new table with selected columns and one distinct count column.

    Parameters:
        connection: sqlite3.Connection - The SQLite database connection object.
        source_table_name: str - The name of the source table.
        result_table_name: str - The name of the reulting table.
        selected_columns: list - List of already existing columns to be selected.
        count_column: str - Name of the column that is used for distinct count.
        count_col_name: str - Name of the resulting count column.
        condition: str - The condition for the selected.
        group_by_columns: list - List of columns that are used for grouping.
    """

    c = connection.cursor()
    c.execute("""DROP TABLE IF EXISTS {table}""".format(table=result_table_name))
    
    select_columns = ",".join(selected_columns)
    group_columns = ",".join(group_by_columns)
    
    query = """
    Create table {new_table} as
    SELECT distinct {select_columns}, count(distinct {count_col}) as {count_name}
    FROM 
    {source}
    where {condition}
    group by {group_columns}
    """.format(new_table=result_table_name, select_columns = select_columns,
               count_col = count_column, count_name = count_col_name,
              source = source_table_name, condition = condition, group_columns = group_columns
              )
    
    #print(query)
    c.execute(query)
    connection.commit()


def create_count_table(
    connection: sqlite3.Connection, 
    source_table_name: str, 
    result_table_name: str, 
    selected_columns: List[str], 
    count_column: str, 
    count_col_name: str, 
    condition: str, 
    group_by_columns: List[str]
    ):
    
    """
    Creates a new table with selected columns and one non distinct count column.

    Parameters:
    connection: sqlite3.Connection - The SQLite database connection object.
    source_table_name: str - The name of the source table.
    result_table_name: str - The name of the reulting table.
    selected_columns: list - List of already existing columns to be selected.
    count_column: str - Name of the column that is used for count.
    count_col_name: str - Name of the resulting count column.
    condition: str - The condition for select.
    group_by_columns: list - List of columns that are used for grouping.
    """

    c = connection.cursor()
    c.execute("""DROP TABLE IF EXISTS {table}""".format(table=result_table_name))
    
    select_columns = ",".join(selected_columns)
    group_columns = ",".join(group_by_columns)
    
    query = """
    Create table {new_table} as
    SELECT {select_columns}, count({count_col}) as {count_name}
    FROM 
    {source}
    where {condition}
    group by {group_columns}
    """.format(new_table=result_table_name, select_columns = select_columns,
               count_col = count_column, count_name = count_col_name,
              source = source_table_name, condition = condition, group_columns = group_columns
              )
    
    #print(query)
    c.execute(query)
    connection.commit()


def create_left_join_table(
    connection: sqlite3.Connection, 
    source_tbl1: str, 
    source_tbl2: str, 
    result_table: str, 
    selected_columns: List[str], 
    condition: str
    ):

    """
    Creates a new table with left join of two tables.

    Parameters:
        connection: sqlite3.Connection - The SQLite database connection object.
        source_tbl1: str - The name of the first source table.
        source_tbl2: str - The name of the second source table.
        result_table: list - The name of the resulting table.
        selected_columns: list - List of columns to be selected.
        condition: str - The condition for select.
    """

    c = connection.cursor()
    c.execute("""DROP TABLE IF EXISTS {table}""".format(table=result_table))
    
    select_columns = ",".join(selected_columns)

    query = """
    CREATE TABLE {new_table} AS
    select {select_columns} from 
    {s1} as tbl1
    left join
    {s2} as tbl2
    on {condition}
    """.format(new_table=result_table, select_columns = select_columns,
               s1 = source_tbl1, s2 = source_tbl2, condition = condition
              )
    
    #print(query)
    c.execute(query)
    connection.commit()