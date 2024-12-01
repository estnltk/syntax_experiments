"""
This file contains utility functions for handling SQLite database operations,
including copying table structures and associated indexes between schemas or tables.
"""

import re
import sqlite3
import uuid
from typing import Optional

from .constants import SQL_ESCAPE_CHAR, SQL_ESCAPE_CHARS_END, SQL_ESCAPE_CHARS_START
from .utils import resolve_schema_and_table, is_table_name_formally_correct
from .db_metadata import get_tables_list, get_schemas_list


def __copy_indexes(
    conn: sqlite3.Connection,
    source_schema: str,
    source_table: str,
    target_schema: str,
    target_table: str,
    verbose: bool = False,
):
    """
    Copies indexes from the source table to the target table.
    Ignores foreign key constraints.
    Generates unique names for the copied indexes by appending a randomly
    generated prefix to the original index names.

    **WARNING**: This function is not fully tested and may not work correctly in all scenarios.

    Parameters:
        conn (sqlite3.Connection): The SQLite database connection object.
        source_schema (str): The schema of the source table.
        source_table (str): The name of the source table.
        target_schema (str): The schema of the target table.
        target_table (str): The name of the target table.
        verbose (bool): If True, enables verbose logging for debugging purposes.

    Raises:
        ValueError: If the source table or target table does not exist.

    """
    tables = get_tables_list(conn)

    if (source_schema, source_table) not in tables:
        raise ValueError(
            f"Source table '{source_schema}.{source_table}' does not exist."
        )
    if (target_schema, target_table) not in tables:
        raise ValueError(
            f"Target table '{target_schema}.{target_table}' does not exist."
        )

    if verbose:
        print(
            f"Copying indexes from '{source_schema}.{source_table}' to '{target_schema}.{target_table}'"
        )

    index_query = f"PRAGMA {SQL_ESCAPE_CHAR}{source_schema}{SQL_ESCAPE_CHAR}.index_list({SQL_ESCAPE_CHAR}{source_table}{SQL_ESCAPE_CHAR})"
    indexes = conn.execute(index_query).fetchall()

    unique_prefix = uuid.uuid4().hex[:8]

    for index in indexes:
        original_index_name = index[1]

        create_index_sql_result = conn.execute(
            f"""
            SELECT sql FROM {SQL_ESCAPE_CHAR}{source_schema}{SQL_ESCAPE_CHAR}.sqlite_master
            WHERE type = 'index' AND name = :index_name
            """,
            {"index_name": original_index_name},
        ).fetchone()

        if not create_index_sql_result or not create_index_sql_result[0]:
            if verbose:
                print(f"Skipping auto-index or undefined index: {original_index_name}")
            continue

        create_index_sql = create_index_sql_result[0]
        new_index_name = f"{unique_prefix}_{original_index_name}"

        esc_chars_start = re.escape(SQL_ESCAPE_CHARS_START)
        esc_chars_end = re.escape(SQL_ESCAPE_CHARS_END)

        esc_source_table = re.escape(source_table)
        updated_index_sql = re.sub(
            rf"ON [{esc_chars_start}]?{esc_source_table}[{esc_chars_end}]?",
            f"ON {SQL_ESCAPE_CHAR}{target_table}{SQL_ESCAPE_CHAR}",
            create_index_sql,
        )

        esc_orig_index_name = re.escape(original_index_name)
        esc_full_new_name = f"{SQL_ESCAPE_CHAR}{target_schema}{SQL_ESCAPE_CHAR}.{SQL_ESCAPE_CHAR}{new_index_name}{SQL_ESCAPE_CHAR}"
        updated_index_sql = re.sub(
            rf" INDEX\s+[{re.escape(esc_chars_start)}]?{esc_orig_index_name}[{re.escape(esc_chars_end)}]?",
            f" INDEX {esc_full_new_name}",
            updated_index_sql,
        )
        if verbose:
            print(updated_index_sql)

        conn.execute(updated_index_sql)
        if verbose:
            print(f"Index '{new_index_name}' created successfully.")


def copy_table_structure(
    conn: sqlite3.Connection,
    table_name: str,
    new_table_name: str,
    source_schema: Optional[str] = None,
    target_schema: Optional[str] = None,
    copy_data: bool = False,
    delete_if_exists: bool = False,
    copy_indexes: bool = False,
    verbose: bool = False,
):
    """
    Copies a table structure, optionally its data, and indexes in an SQLite database.

    Parameters:
    - conn: SQLite database connection object.
    - table_name (str): The source table name (optionally with schema).
    - new_table_name (str): The target table name (optionally with schema).
    - source_schema (Optional[str]): The schema of the source table. If None, it is parsed from the table name.
    - target_schema (Optional[str]): The schema of the target table. If None, it is parsed from the table name.
    - copy_data (bool): Whether to copy the data from the source table.
    - delete_if_exists (bool): Whether to delete the target table if it exists.
    - copy_indexes (bool): Whether to copy indexes from the source table.
    - verbose (bool): If True, prints detailed progress.

    Returns:
    - Tuple (schema, table_name) of the created table.
    """

    if source_schema:
        schema_source = source_schema
        source_table = table_name
    else:
        schema_source, source_table = resolve_schema_and_table(table_name)

    if target_schema:
        schema_target = target_schema
        target_table = new_table_name
    else:
        schema_target, target_table = resolve_schema_and_table(new_table_name)

    schemas = get_schemas_list(conn)
    tables = get_tables_list(conn)

    if (schema_source, source_table) == (schema_target, target_table):
        raise ValueError("Source and target tables are the same.")

    if schema_source not in schemas:
        raise ValueError(f"Source schema '{schema_source}' does not exist.")
    if schema_target not in schemas:
        raise ValueError(f"Target schema '{schema_target}' does not exist.")

    if (schema_source, source_table) not in tables:
        raise ValueError(
            f"Source table '{schema_source}.{source_table}' does not exist."
        )
    if (schema_target, target_table) in tables and not delete_if_exists:
        raise ValueError(
            f"Target table '{schema_target}.{target_table}' already exists."
        )

    if not is_table_name_formally_correct(target_table, with_schema=False):
        raise ValueError(f"Target table name is not valid table name '{target_table}'.")

    try:
        conn.execute("BEGIN")
        if (schema_target, target_table) in tables and delete_if_exists:
            conn.execute(f'DROP TABLE IF EXISTS "{schema_target}"."{target_table}"')
            if verbose:
                print(f"Deleted existing table '{schema_target}.{target_table}'.")

        schema_query = f"""
        SELECT sql FROM "{schema_source}".sqlite_master
        WHERE type='table' AND name=:table_name
        """
        schema_result = conn.execute(
            schema_query, {"table_name": source_table}
        ).fetchone()

        if not schema_result:
            raise ValueError(
                f"Source table '{schema_source}.{source_table}' does not exist."
            )

        esc_chars_start = re.escape(SQL_ESCAPE_CHARS_START)
        esc_chars_end = re.escape(SQL_ESCAPE_CHARS_END)
        esc_source_table = re.escape(source_table)

        create_table_sql = schema_result[0]
        create_table_sql = re.sub(r"FOREIGN KEY.*?,", "", create_table_sql)
        create_table_sql = re.sub(
            rf"CREATE TABLE\s+[{esc_chars_start}]?{esc_source_table}[{esc_chars_end}]? ",
            f"CREATE TABLE {SQL_ESCAPE_CHAR}{schema_target}{SQL_ESCAPE_CHAR}.{SQL_ESCAPE_CHAR}{target_table}{SQL_ESCAPE_CHAR} ",
            create_table_sql,
            count=1,
        )

        if verbose:
            print(create_table_sql)

        conn.execute(create_table_sql)
        if verbose:
            print(
                f"Created table '{schema_target}.{target_table}' (foreign keys ignored)."
            )

        if copy_data:
            copy_data_query = f"""
            INSERT INTO {SQL_ESCAPE_CHAR}{schema_target}{SQL_ESCAPE_CHAR}.{SQL_ESCAPE_CHAR}{target_table}{SQL_ESCAPE_CHAR}
            SELECT * FROM {SQL_ESCAPE_CHAR}{schema_source}{SQL_ESCAPE_CHAR}.{SQL_ESCAPE_CHAR}{source_table}{SQL_ESCAPE_CHAR}
            """
            conn.execute(copy_data_query)
            if verbose:
                print(
                    f"Data copied from '{schema_source}.{source_table}' to '{schema_target}.{target_table}'."
                )

        if copy_indexes:
            __copy_indexes(
                conn=conn,
                source_schema=schema_source,
                source_table=source_table,
                target_schema=schema_target,
                target_table=target_table,
                verbose=verbose,
            )

        conn.commit()
        return schema_target, target_table

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Transaction failed: {e}")
