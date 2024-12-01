"""
This file contains utility functions for handling SQLite database operations,
including copying table structures and associated indexes between schemas or tables.
"""

import re
import sqlite3
import uuid
from typing import Optional

from .utils import resolve_schema_and_table
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

    index_query = f"PRAGMA `{source_schema}`.index_list(`{source_table}`)"
    indexes = conn.execute(index_query).fetchall()

    unique_prefix = uuid.uuid4().hex[:8]

    for index in indexes:
        original_index_name = index[1]

        create_index_sql_result = conn.execute(
            f"""
            SELECT sql FROM `{source_schema}`.sqlite_master
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

        updated_index_sql = create_index_sql.replace(
            f' ON "{source_table}"',
            f' ON "{target_table}"',
        )

        updated_index_sql = updated_index_sql.replace(
            f'CREATE INDEX "{original_index_name}"',
            f'CREATE INDEX "{new_index_name}"',
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
    schema_source: Optional[str] = None,
    schema_target: Optional[str] = None,
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
    - schema_source (Optional[str]): The schema of the source table. If None, it is parsed from the table name.
    - schema_target (Optional[str]): The schema of the target table. If None, it is parsed from the table name.
    - copy_data (bool): Whether to copy the data from the source table.
    - delete_if_exists (bool): Whether to delete the target table if it exists.
    - copy_indexes (bool): Whether to copy indexes from the source table.
    - verbose (bool): If True, prints detailed progress.

    Returns:
    - Tuple (schema, table_name) of the created table.
    """

    if schema_source:
        source_schema = schema_source
        source_table = table_name
    else:
        source_schema, source_table = resolve_schema_and_table(table_name)

    if schema_target:
        target_schema = schema_target
        target_table = new_table_name
    else:
        target_schema, target_table = resolve_schema_and_table(new_table_name)

    schemas = get_schemas_list(conn)
    tables = get_tables_list(conn)

    # Validation checks
    if (source_schema, source_table) == (target_schema, target_table):
        raise ValueError("Source and target tables are the same.")

    if source_schema not in schemas:
        raise ValueError(f"Source schema '{source_schema}' does not exist.")
    if target_schema not in schemas:
        raise ValueError(f"Target schema '{target_schema}' does not exist.")
    if (source_schema, source_table) not in tables:
        raise ValueError(
            f"Source table '{source_schema}.{source_table}' does not exist."
        )
    if (target_schema, target_table) in tables and not delete_if_exists:
        raise ValueError(
            f"Target table '{target_schema}.{target_table}' already exists."
        )

    try:
        conn.execute("BEGIN")
        if (target_schema, target_table) in tables and delete_if_exists:
            conn.execute(f"DROP TABLE IF EXISTS `{target_schema}`.`{target_table}`")
            if verbose:
                print(f"Deleted existing table '{new_table_name}'.")

        schema_query = f"""
        SELECT sql FROM `{source_schema}`.sqlite_master
        WHERE type='table' AND name=:table_name
        """
        schema_result = conn.execute(
            schema_query, {"table_name": source_table}
        ).fetchone()

        if not schema_result:
            raise ValueError(f"Source table '{table_name}' does not exist.")

        create_table_sql = schema_result[0]
        create_table_sql = re.sub(r"FOREIGN KEY.*?,", "", create_table_sql)
        create_table_sql = create_table_sql.replace(
            f"CREATE TABLE `{source_table}`",
            f"CREATE TABLE `{target_schema}`.`{target_table}`",
            1,
        )

        if verbose:
            print(create_table_sql)

        conn.execute(create_table_sql)
        if verbose:
            print(f"Created table '{new_table_name}' (foreign keys ignored).")

        if copy_data:
            copy_data_query = f"""
            INSERT INTO `{target_schema}`.`{target_table}`
            SELECT * FROM `{source_schema}`.`{source_table}`
            """
            conn.execute(copy_data_query)
            if verbose:
                print(f"Data copied from '{table_name}' to '{new_table_name}'.")

        if copy_indexes:
            __copy_indexes(
                conn=conn,
                source_schema=source_schema,
                source_table=source_table,
                target_schema=target_schema,
                target_table=target_table,
                verbose=verbose,
            )

        conn.commit()
        return target_schema, target_table

    except Exception as e:
        conn.rollback()
        raise RuntimeError(f"Transaction failed: {e}")
