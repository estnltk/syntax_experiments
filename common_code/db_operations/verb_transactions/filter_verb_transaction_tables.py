import sqlite3
import pandas as pd
import timeit

from ..utils import resolve_schema_and_table
from ..db_checks import check_column_exists
from ..db_table_ops import copy_table_structure
from ..constants import SQL_ESCAPE_CHAR


def filter_verb_transaction_tables(
    conn: sqlite3.Connection,
    source_schema: str = None,
    transaction_head: str = "transaction_head",
    transaction_row: str = "transaction_row",
    target_schema: str = None,
    new_transaction_head: str = None,
    new_transaction_row: str = None,
    ids_schema: str = None,
    ids_table: str = "head_ids",
    ids_column: str = "head_id",
    delete_if_exists: bool = False,
    copy_indexes: bool = True,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Filters and copies data from transaction tables based on head IDs.

    TODO:
    - Add check that target tables new_transaction_head and new_transaction_row are not same.
    - Add check that transaction_head table contains `id` column.
    - Add check that transaction_row table contains `head_id` column.


    Parameters:
    - conn: SQLite database connection object.
    - head_ids_table: The table containing the head IDs to filter by.
    - head_ids_column: The column in `head_ids_table` containing the relevant head IDs.
    - source_schema: The schema containing the source transaction tables.
    - transaction_head: The name of the source transaction head table.
    - transaction_row: The name of the source transaction row table.
    - target_schema: The schema for the new filtered tables.
    - new_transaction_head: The name of the new filtered transaction head table.
    - new_transaction_row: The name of the new filtered transaction row table.
    - delete_if_exists: Whether to delete existing filtered tables before recreating.
    - copy_indexes: Whether to copy indexes when creating new tables.
    - verbose: Whether to print detailed logs of the process.

    Returns:
    - Pandas Dataframe object, with statistics of created tables and function execution times.
    """

    overall_start = timeit.default_timer()
    stat_create = {}
    stat_insert = {}

    if not new_transaction_head:
        new_transaction_head = transaction_head
    if not new_transaction_row:
        new_transaction_row = transaction_row

    if source_schema:
        schema_source_head = source_schema
        schema_source_row = source_schema
        table_source_head = transaction_head
        table_source_row = transaction_row
    else:
        schema_source_head, table_source_head = resolve_schema_and_table(
            transaction_head
        )
        schema_source_row, table_source_row = resolve_schema_and_table(transaction_row)

    if target_schema:
        schema_target_head = target_schema
        schema_target_row = target_schema
        table_target_head = new_transaction_head
        table_target_row = new_transaction_row
    else:
        schema_target_head, table_target_head = resolve_schema_and_table(
            new_transaction_head
        )
        schema_target_row, table_target_row = resolve_schema_and_table(
            new_transaction_row
        )

    # those checks are performed also in copy_table_structure function, but we wan't to check both tables before copying
    if (schema_source_head, table_source_head) == (
        schema_target_head,
        table_target_head,
    ):
        raise ValueError(
            "Source and target transaction tables are the same "
            f" {schema_source_head}.{table_source_head} {schema_target_head}.{table_target_head}."
        )

    if (schema_source_row, table_source_row) == (schema_target_row, table_target_row):
        raise ValueError(
            f"Source and target transaction tables are the same {schema_source_row}."
            f" {table_source_row} {schema_target_row}.{table_target_row}."
        )

    schema_ids = None
    table_ids = None
    if ids_schema:
        schema_ids = ids_schema
        table_ids = ids_table
    elif ids_table:
        schema_ids, table_ids = resolve_schema_and_table(ids_table)

    column_ids = None
    if ids_column:
        # Validate head_ids_table and head_ids_column
        if not check_column_exists(
            conn=conn, table_name=f"{schema_ids}.{table_ids}", column_name=ids_column
        ):
            raise ValueError(
                f"Column '{ids_column}' does not exist in table '{schema_ids}.{table_ids}'."
            )
        column_ids = ids_column

    if not table_ids or not column_ids:
        raise ValueError("'ids_table' and 'ids_column' must be provided.")
    create_head_start = timeit.default_timer()
    # Copy structure of transaction head table
    schema_target_head, table_target_head = copy_table_structure(
        conn,
        source_schema=schema_source_head,
        table_name=table_source_head,
        target_schema=schema_target_head,
        new_table_name=table_target_head,
        delete_if_exists=delete_if_exists,
        verbose=verbose,
        copy_indexes=copy_indexes,
    )
    stat_create[
        (
            schema_target_head,
            table_target_head,
        )
    ] = (
        timeit.default_timer() - create_head_start
    )

    create_rows_start = timeit.default_timer()
    schema_target_row, table_target_row = copy_table_structure(
        conn,
        source_schema=schema_source_row,
        table_name=table_source_row,
        target_schema=schema_target_row,
        new_table_name=table_target_row,
        delete_if_exists=delete_if_exists,
        verbose=verbose,
        copy_indexes=copy_indexes,
    )
    stat_create[
        (
            schema_target_row,
            table_target_row,
        )
    ] = (
        timeit.default_timer() - create_rows_start
    )

    insert_head_start = timeit.default_timer()
    # Populate data in new transaction head table
    sql_head = f"""
    INSERT INTO "{schema_target_head}"."{table_target_head}"
    SELECT th_source.*
    FROM "{schema_source_head}"."{table_source_head}" AS th_source
    INNER JOIN "{schema_ids}"."{table_ids}" AS heads_table
    ON th_source.id = heads_table."{column_ids}"
    ON CONFLICT(id) DO NOTHING;
    """
    if verbose:
        print(sql_head)
    conn.execute(sql_head)
    stat_insert[
        (
            schema_target_head,
            table_target_head,
        )
    ] = (
        timeit.default_timer() - insert_head_start
    )

    insert_row_start = timeit.default_timer()
    # Populate data in new transaction row table
    sql_row = f"""
    INSERT INTO "{schema_target_row}"."{table_target_row}"
    SELECT tr_source.*
    FROM "{schema_source_row}"."{table_source_row}" AS tr_source
    INNER JOIN "{schema_ids}"."{table_ids}" AS heads_table
    ON tr_source.head_id = heads_table."{column_ids}"
    ON CONFLICT(id) DO NOTHING;
    """
    if verbose:
        print(sql_row)
    conn.execute(sql_row)
    stat_insert[
        (
            schema_target_row,
            table_target_row,
        )
    ] = (
        timeit.default_timer() - insert_row_start
    )

    db_commit_start = timeit.default_timer()
    conn.commit()
    db_commit_duration = timeit.default_timer() - db_commit_start

    cur = conn.cursor()
    stats = []
    db_stat_start = timeit.default_timer()
    # collect stats
    for sh, tbl in (
        (
            schema_ids,
            table_ids,
        ),
        (
            schema_source_head,
            table_source_head,
        ),
        (
            schema_source_row,
            table_source_row,
        ),
        (
            schema_target_head,
            table_target_head,
        ),
        (
            schema_target_row,
            table_target_row,
        ),
    ):
        stats.append(
            (
                "",
                sh,
                tbl,
                __count_table_rows(cur=cur, schema=sh, table_name=tbl),
                (
                    round(
                        stat_create[
                            (
                                sh,
                                tbl,
                            )
                        ],
                        3,
                    )
                    if (sh, tbl) in stat_create
                    else ""
                ),
                (
                    round(
                        stat_insert[
                            (
                                sh,
                                tbl,
                            )
                        ],
                        3,
                    )
                    if (sh, tbl) in stat_insert
                    else ""
                ),
            )
        )

    stats.append(
        (
            "fetching rows count",
            "---",
            "---",
            "---",
            "---",
            round(timeit.default_timer() - db_stat_start, 3),
        )
    )
    stats.append(
        ("db commit", "---", "---", "---", "---", round(db_commit_duration, 3))
    )
    stats.append(
        (
            "total time",
            "---",
            "---",
            "---",
            "---",
            round(timeit.default_timer() - overall_start, 3),
        )
    )

    df_stats = pd.DataFrame(
        stats,
        columns=[
            "",
            "Schema",
            "Table",
            "Rows Total",
            "Create Structure (sec)",
            "Insert Data / Execution Time (sec)",
        ],
    )
    return df_stats


def __count_table_rows(cur: sqlite3.Cursor, schema: str, table_name: str):
    """
    For internal use only. Does not validate schema and table names.
    """
    cur.execute(
        f"SELECT COUNT(*) FROM {SQL_ESCAPE_CHAR}{schema}{SQL_ESCAPE_CHAR}.{SQL_ESCAPE_CHAR}{table_name}{SQL_ESCAPE_CHAR}"
    )
    return cur.fetchone()[0]
