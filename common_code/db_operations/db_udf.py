"""
This file contains user-defined functions (UDFs) specifically for SQLite databases.
These functions can be registered to an SQLite connection, extending the database
with additional capabilities such as string transformations.
"""

import sqlite3


def udf_lower(input_str: str) -> str:
    """
    A user-defined function (UDF) for SQLite that returns the lowercase version of the input string.

    This function is necessary because SQLite's built-in LOWER() function does not
    fully support UTF-8 character lowercasing. By implementing this function, proper
    handling of UTF-8 strings is ensured.

    Parameters:
        input_str (str): The input string to convert to lowercase.

    Returns:
        str: The lowercase version of the input string, or None if the input is None.
    """
    if input_str is None:
        return None
    return input_str.lower()


def register_user_defined_functions(conn: sqlite3.Connection):
    """
    Registers user-defined functions with the given SQLite connection.

    Currently, this registers:
    - udf_lower: Converts a given string to lowercase.

    Parameters:
        conn (sqlite3.Connection): The SQLite connection to which the functions should be added.
    """
    conn.create_function("udf_lower", 1, udf_lower)
