import sqlite3
from ..utils import resolve_schema_and_table
from ..db_checks import check_column_exists
from ..db_table_ops import copy_table_structure


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
) -> tuple[str, str]:
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
    - Tuple of names for the new filtered transaction head and row tables.
    """

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

    # Populate data in new transaction head table
    sql_head = f"""
    INSERT INTO "{schema_target_head}"."{table_target_head}"
    SELECT th_source.*
    FROM "{schema_source_head}"."{table_target_head}" AS th_source
    INNER JOIN "{schema_ids}"."{table_ids}" AS heads_table
    ON th_source.id = heads_table."{column_ids}"
    ON CONFLICT(id) DO NOTHING;
    """
    if verbose:
        print(sql_head)
    conn.execute(sql_head)

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

    conn.commit()
    return True
