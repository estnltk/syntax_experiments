"""
This file contains utility functions specific to SQLite databases.
These functions provide common operations such as retrieving schemas,
tables, and columns, and validating schema and table names.
"""

import sqlite3
from typing import List, Tuple, Optional
from .constants import SQL_ESCAPE_CHAR
from .utils import is_table_name_formally_correct, is_schema_name_formally_correct


def get_schemas_list(conn: sqlite3.Connection) -> List[str]:
    """
    Retrieves the list of schemas (databases) in the SQLite connection.

    Parameters:
        conn: The SQLite database connection object.

    Returns:
        list: A list of schema names available in the connection.
    """
    return [row[1] for row in conn.execute("PRAGMA database_list").fetchall()]


def get_tables_list(
    conn: sqlite3.Connection,
    schema: Optional[str] = None,
    table_name: Optional[str] = None,
) -> List[Tuple[str, str]]:
    """
    Retrieves the list of tables in the SQLite connection, optionally filtered by schema or table name.

    Parameters:
        conn (sqlite3.Connection): The SQLite database connection object.
        schema (str, optional): The schema to filter tables by. Defaults to None, meaning all schemas.
        table_name (str, optional): The specific table name to check. If provided, the function will only check if
                                    the table exists instead of retrieving all tables.

    Returns:
        List[Tuple[str, str]]: A list of tuples containing (schema, table) for each matching table.
    """
    if table_name and not is_table_name_formally_correct(table_name, with_schema=False):
        raise ValueError(f"Invalid table name: '{table_name}'")
    if schema and not is_schema_name_formally_correct(schema):
        raise ValueError(f"Invalid schema name: '{schema}'")

    if table_name:
        if schema:
            query = "SELECT * FROM pragma_table_list() WHERE schema = ? AND name = ?"
            rows = conn.execute(query, (schema, table_name)).fetchall()
        else:
            query = "SELECT * FROM pragma_table_list() WHERE name = ?"
            rows = conn.execute(query, (table_name,)).fetchall()
    elif schema:
        query = "SELECT * FROM pragma_table_list() WHERE schema = ?"
        rows = conn.execute(query, (schema,)).fetchall()
    else:
        query = "SELECT * FROM pragma_table_list()"
        rows = conn.execute(query).fetchall()

    return [(row[0], row[1]) for row in rows]  # (schema, table_name)


def get_columns_list(
    conn: sqlite3.Connection, schema: str, table_name: str
) -> List[str]:
    """
    Retrieves the list of columns for a specific table in a given schema.

    Parameters:
        conn: The SQLite database connection object.
        schema (str): The schema where the table is located. Defaults to 'main' if not specified.
        table_name (str): The table name for which columns are to be retrieved.

    Returns:
        list: A list of column names in the specified table.

    Raises:
        ValueError: If the specified table does not exist in the schema or names are invalid.
    """
    if not is_schema_name_formally_correct(schema):
        raise ValueError(f"Invalid schema name: '{schema}'")
    if not is_table_name_formally_correct(table_name):
        raise ValueError(f"Invalid table name: '{table_name}'")

    tables = get_tables_list(conn)
    if (
        not (
            schema,
            table_name,
        )
        in tables
    ):
        raise ValueError(f"Table '{schema}.{table_name}' does not exist.")

    return [
        row[1]
        for row in conn.execute(
            f"PRAGMA {SQL_ESCAPE_CHAR}{schema}{SQL_ESCAPE_CHAR}.table_info({SQL_ESCAPE_CHAR}{table_name}{SQL_ESCAPE_CHAR})"
        ).fetchall()
    ]
