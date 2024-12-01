########################################################################
# This file contains utility functions specific to SQLite databases.
# These functions provide common operations such as retrieving schemas,
# tables, and columns, and validating schema and table names.
########################################################################

# TODO! consider using conn instead of cur


import sqlite3
import re
from typing import List

from .utils import split_schema_and_table, is_table_name_formally_correct
from .db_metadata import get_schemas_list, get_tables_list, get_columns_list


def is_valid_schema_name(schema_name: str) -> bool:
    """
    Validates if the given schema name matches SQLite's naming standards.

    Parameters:
        schema_name (str): The schema name to validate.

    Returns:
        bool: True if the schema name is valid, False otherwise.
    """
    if not schema_name:
        return False

    # SQLite schema naming standards (alphanumeric, underscores, no reserved keywords like 'sqlite_')
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", schema_name):
        return False
    if re.match(r"^sqlite_.*$", schema_name):
        return False
    return True


def is_valid_table_name(
    conn: sqlite3.Connection, table_name: str, check_exists: bool = True
) -> bool:
    """
    Validates the given table name, including its optional schema, against SQLite's standards.
    Optionally checks if the table already exists in the database.

    Parameters:
        conn (sqlite3.Connection): The SQLite connection object.
        table_name (str): The table name to validate.
        check_exists (bool): Whether to check if the table already exists in the database. Defaults to True.

    Returns:
        bool: True if the table name is valid, False otherwise.

    Raises:
        ValueError: If the schema in the table name does not exist,
        the table name is invalid, or the table exists (based on `check_exists`).
    """
    if not is_table_name_formally_correct(table_name):
        return False

    schema, tbl = split_schema_and_table(table_name)

    if schema:
        schemas = get_schemas_list(conn)
        if schema not in schemas:
            raise ValueError(f"Schema '{schema}' does not exist.")

    if check_exists:
        tables = get_tables_list(conn, schema=schema, table=tbl)
        if tables:
            raise ValueError(f"Table '{schema}.{tbl}' already exists in the database.")

    return True


def is_db_schema(cur: sqlite3.Cursor, schema: str) -> bool:
    """
    Checks if the given schema name exists.

    Parameters:
        cur (sqlite3.Cursor): The SQLite cursor object.
        schema (str): The schema name to check.

    Returns:
        bool: True if the schema exists, False otherwise.
    """
    cur.execute(
        """SELECT * FROM pragma_table_list() WHERE schema={schema}""".format(
            schema=schema
        )
    )
    if cur.fetchone():
        return True
    return False


def is_db_table(cur: sqlite3.Cursor, table_name: str) -> bool:
    """
    Checks if the given table exists in the database.

    Parameters:
        cur (sqlite3.Cursor): The SQLite cursor object.
        table_name (str): The name of the table to check.

    Returns:
        bool: True if the table exists, False otherwise.

    Raises:
        ValueError: If the schema in the table name does not exist.
    """
    schema, tbl = split_schema_and_table(table_name)
    if schema:
        if not is_db_schema(cur, schema):
            raise ValueError("Given database schema does not exist")
        else:
            cur.execute(
                """PRAGMA {schema}.table_info({table_name})""".format(
                    schema=schema, table_name=tbl
                )
            )
    else:
        cur.execute("""PRAGMA table_info({table_name})""".format(table_name=tbl))
    if cur.fetchone() is None:
        return False
    return True


def is_col_name(cur: sqlite3.Cursor, table_name: str, col_name: str) -> bool:
    """
    Checks if the column name exists in the given table.

    Parameters:
        cur (sqlite3.Cursor): The SQLite cursor object.
        table_name (str): The name of the table to check.
        col_name (str): The column name to verify.

    Returns:
        bool: True if the column exists, False otherwise.

    Raises:
        ValueError: If the schema in the table name does not exist.
    """
    schema, tbl = split_schema_and_table(table_name)
    if schema:
        if not is_db_schema(cur, schema):
            raise ValueError(
                "Database schema included in given table name does not exist, cannot check column name"
            )
        else:
            cur.execute(
                """PRAGMA {schema}.table_info({table_name})""".format(
                    schema=schema, table_name=tbl
                )
            )
    else:
        cur.execute("""PRAGMA table_info({table_name})""".format(table_name=table_name))
    columns = cur.fetchall()
    for column in columns:
        if column[1] == col_name:
            return True
    return False


def check_all_col_names(
    cur: sqlite3.Cursor, table_name: str, col_names: List[str]
) -> bool:
    """
    Iterates over column names provided in a list, checks if they exist in the given table.

    Parameters:
        cur (sqlite3.Cursor): The SQLite cursor object.
        table_name (str): The name of the table to check.
        col_names (List[str]): A list of column names to validate.

    Returns:
        bool: True if all column names exist in the table, False otherwise.
    """
    for col_name in col_names:
        if not is_col_name(cur, table_name, col_name):
            return False
    return True


def check_column_exists(
    conn: sqlite3.Connection, table_name: str, column_name: str
) -> bool:
    """
    Checks if a specific column exists in a given table.

    Parameters:
        conn (sqlite3.Connection): The SQLite connection object.
        table_name (str): The name of the table (with optional schema) to check.
        column_name (str): The name of the column to verify.

    Returns:
        bool: True if the column exists, False otherwise.

    Raises:
        ValueError: If the table or schema does not exist or are invalid.
    """

    schema, tbl = split_schema_and_table(table_name)

    columns = get_columns_list(conn, schema, tbl)

    return column_name in columns
