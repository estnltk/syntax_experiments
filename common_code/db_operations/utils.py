"""
This file contains utility functions for validating and parsing SQLite schema and table names.
"""

import re
from typing import Tuple, Optional


def resolve_schema_and_table(
    table_name: str, default_schema: str = "main"
) -> Tuple[str, str]:
    """
    Extracts schema name and table name from given table name string.

    Parameters:
        table_name (str): The table name, optionally prefixed with a schema (e.g., 'schema.table').

    Returns:
        tuple: A tuple (schema, table) where schema is 'main' if not explicitly provided.

    Raises:
        ValueError: If the table name is empty or contain invalid characters.
    """
    if not table_name.strip():
        raise ValueError("Table name cannot be empty.")

    if "." in table_name:
        schema, table = table_name.split(".")
    else:
        schema, table = default_schema, table_name
    return schema, table


def is_schema_name_formally_correct(schema_name: str) -> bool:
    """
    Checks if the given schema name is formally correct according to SQLite standards.

    TODO! Check what about ::memory:: schema name validation.

    Parameters:
        schema_name (str): The schema name to validate.

    Returns:
        bool: True if the schema name is formally correct, False otherwise.
    """
    if not schema_name or not schema_name.strip():
        return False
    # SQLite schema names must start with a letter or underscore, followed by alphanumeric or underscores
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", schema_name))


def is_table_name_formally_correct(table_name: str, with_schema: bool = True) -> bool:
    """
    Checks if the given table name is formally correct according to SQLite standards.
    The `with_schema` parameter indicates whether the table name can include a schema part.

    Parameters:
        table_name (str): The table name to validate.
        with_schema (bool): Whether the table name is allowed to include a schema part (e.g., 'schema.table_name').
                            Defaults to True.

    Returns:
        bool: True if the table name is formally correct, False otherwise.
    """
    if not table_name or not table_name.strip():
        return False

    # Check if the table name includes a schema part
    if "." in table_name:
        if not with_schema:
            return False  # Table name should not include a schema part
        schema, tbl = split_schema_and_table(table_name)
        # Validate schema part
        if not is_schema_name_formally_correct(schema):
            return False
    else:
        tbl = table_name

    # Validate table name format
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", tbl):
        return False

    # Exclude reserved table names
    if re.match(r"^sqlite_.*$", tbl):
        return False

    return True


def split_schema_and_table(
    table_name: str, default_schema: Optional[str] = "main"
) -> tuple[Optional[str], str]:
    """
    Splits a fully qualified table name into schema and table components.

    Parameters:
        table_name (str): The table name, optionally prefixed with a schema (e.g., 'schema.table').
        default_schema (Optional[str]): The default schema to use if not specified.

    Returns:
        tuple[Optional[str], str]: A tuple (schema, table) where schema is None or a valid schema name.
    """
    if not table_name.strip():
        raise ValueError("Table name cannot be empty.")

    if "." in table_name:
        schema, table = table_name.split(".")
        return schema, table
    else:
        return default_schema, table_name
