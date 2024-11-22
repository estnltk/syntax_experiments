import re


def __get_schemas_list(conn):
    return [row[1] for row in conn.execute("PRAGMA database_list").fetchall()]


def __get_tables_list(conn):
    return [
        (
            row[0],
            row[1],
        )
        for row in conn.execute("PRAGMA table_list").fetchall()
    ]


def __get_columns_list(conn, schema, table):
    if not schema:
        schema = "main"
    tables = __get_tables_list(conn)
    if (
        not (
            schema,
            table,
        )
        in tables
    ):
        raise ValueError(f"Table '{schema}.{table}' does not exist.")

    return [
        row[1]
        for row in conn.execute(f"PRAGMA `{schema}`.table_info(`{table}`)").fetchall()
    ]


def __parse_table_name(table_name: str):
    if "." in table_name:
        schema, table = table_name.split(".")
    else:
        schema, table = "main", table_name
    return schema, table


def __copy_indexes(
    conn,
    source_schema: str,
    source_table: str,
    target_schema: str,
    target_table: str,
    verbose: bool = False,
):
    """
    Isn't stable yet
    """
    if (
        source_schema,
        source_table,
    ) not in __get_tables_list(conn):
        raise ValueError(
            f"Source table '{source_schema}.{source_table}' does not exist. (copy_indexes)"
        )

    if (
        target_schema,
        target_table,
    ) in __get_tables_list(conn):
        raise ValueError(
            f"Target table '{target_schema}.{target_table}' does not exist. (copy_indexes)"
        )

    # Retrieve all indexes from the source table
    if verbose:
        print(
            f"Copying indexes from '{source_schema}.{source_table}' to '{target_schema}.{target_table}'"
        )

    index_query = f"PRAGMA `{source_schema}`.index_list(`{source_table}`)"
    indexes = conn.execute(index_query).fetchall()
    for index in indexes:
        index_name = index[1]  # Index name

        create_index_sql = conn.execute(
            f"""
            SELECT sql FROM `{source_schema}`.sqlite_master 
            WHERE type = 'index' AND name = :index_name
            """,
            {"index_name": index_name},
        ).fetchone()

        # Skip if no SQL definition is found (e.g., auto-indexes)
        if not create_index_sql or not create_index_sql[0]:
            if verbose:
                print(f"Skipping auto-index or undefined index: {index_name}")
            continue

        # Modify the SQL to point to the new table
        create_index_sql = create_index_sql[0].replace(source_table, target_table)
        print("create_index_sql", create_index_sql)
        # Execute the modified CREATE INDEX statement
        conn.execute(create_index_sql)
        if verbose:
            print(f"Index '{index_name}' recreated  successfully.")


def copy_table(
    conn,
    table_name: str,
    new_table_name: str,
    copy_data: bool = False,
    delete_if_exists: bool = False,
    copy_indexes: bool = True,
    verbose: bool = False,
):
    # TODO! add checks from db_checks.py - does schema exists, table exists, is valid table name etc
    # TODO! add rollback in case of failing or remove commit
    """
    Copies a table structure without foreign key constraints and optionally its data in an SQLite database,
    supporting schemas.


    Parameters:
    - conn: connection object to the SQLite database.
    - table_name (str): The name of the source table to copy, with optional schema (e.g., 'schema.table').
    - new_table_name (str): The name of the new table to create, with optional schema (e.g., 'schema.table_copy').
    - copy_data (bool): Whether to copy the data from the source table.
    - delete_if_exists (bool): Whether to delete the target table if it already exists.

    Returns:
    - schema, table_name of created table (Tuple)
    """

    # Extract schema and table names
    source_schema, source_table = __parse_table_name(table_name)
    target_schema, target_table = __parse_table_name(new_table_name)

    # Check if schemas exist
    schemas = __get_schemas_list(conn=conn)
    tables = __get_tables_list(conn=conn)

    if (
        source_schema,
        source_table,
    ) == (
        target_schema,
        target_table,
    ):
        raise ValueError(
            f"Source table is same table as target table '{source_schema}.{source_table} == {target_schema}.{target_table}'."
        )

    if source_schema not in schemas:
        raise ValueError(f"Source schema '{source_schema}' does not exist.")

    if target_schema not in schemas:
        raise ValueError(f"Target schema '{target_schema}' does not exist.")

    if (
        source_schema,
        source_table,
    ) not in tables:
        raise ValueError(f"Source table '{table_name}' does not exist.")

    if (
        target_schema,
        target_table,
    ) in tables and not delete_if_exists:
        raise ValueError(f"Source table '{new_table_name}' already exists.")
    try:
        # Start a transaction
        conn.execute("BEGIN")
        if (
            target_schema,
            target_table,
        ) in tables and delete_if_exists:
            conn.execute(f"DROP TABLE IF EXISTS `{target_schema}`.`{target_table}`")
            if verbose:
                print(f"Table '{new_table_name}' deleted successfully.")

        # Get the schema of the source table
        schema_query = f"""
        SELECT sql FROM `{source_schema}`.sqlite_master
        WHERE type='table' AND name=:table_name AND (tbl_name=:table_name)
        """

        schema_result = conn.execute(
            schema_query, {"table_name": source_table}
        ).fetchone()

        # should never get here
        if not schema_result:
            raise ValueError(f"Table '{table_name}' does not exist.")

        # Extract the CREATE TABLE statement
        create_table_sql = schema_result[0]

        # Remove Foreign key constraints
        create_table_sql = re.sub(
            r"FOREIGN KEY.*?,", "", create_table_sql
        )  # Remove FOREIGN KEY constraints
        create_table_sql = create_table_sql.replace(
            f"CREATE TABLE `{source_table}`",
            f"CREATE TABLE `{target_schema}`.`{target_table}`",
            1,
        )

        if verbose:
            print(create_table_sql)

        # Create the new table
        conn.execute(create_table_sql)

        if verbose:
            print(
                f"Table '{new_table_name}' created successfully (foreign key constraints were ignored)."
            )

        # Copy the data if requested
        if copy_data:
            copy_data_query = f"INSERT INTO `{target_schema}`.`{target_table}` SELECT * FROM `{source_schema}`.`{source_table}`"
            conn.execute(copy_data_query)
            if verbose:
                print(f"Data copied from '{table_name}' to '{new_table_name}'.")

        if copy_indexes:
            __copy_indexes(
                conn=conn,
                target_schema="temp",
                source_schema=source_schema,
                target_table=target_table,
                source_table=source_table,
                verbose=verbose,
            )
        conn.commit()
        return (
            target_schema,
            target_table,
        )

    except Exception as e:
        conn.rollback()
        print(f"Transaction rolled back due to error: {e}")


def make_verb_transactions_tables(
    conn,
    head_ids_table: str,
    head_ids_column: str,
    transaction_head: str,
    transaction_row: str,
    new_transaction_head: str,
    new_transaction_row: str,
    delete_if_exists: bool = False,
    copy_indexes: bool = True,
    verbose: bool = False,
):
    tables = __get_tables_list(conn=conn)

    # check that head_ids_table table exists and  head_ids_column exists
    heads_schema, heads_table = __parse_table_name(head_ids_table)
    if (
        not (
            heads_schema,
            heads_table,
        )
        in tables
    ):
        raise ValueError(
            f"Head IDs table '{heads_schema}.{heads_table}' does not exist."
        )

    # Check if column exist
    if head_ids_column not in __get_columns_list(
        conn=conn, schema=heads_schema, table=heads_table
    ):
        raise ValueError(
            f"Column '{head_ids_column}' does not exist in table '{heads_schema}.{heads_table}'."
        )

    # Create new_transaction_head
    (
        target_head_schema,
        target_head_name,
    ) = copy_table(
        conn=conn,
        table_name=transaction_head,
        new_table_name=new_transaction_head,
        delete_if_exists=delete_if_exists,
        verbose=verbose,
        copy_indexes=copy_indexes,
    )

    # Create new_transaction_row
    (
        target_row_schema,
        target_row_name,
    ) = copy_table(
        conn=conn,
        table_name=transaction_row,
        new_table_name=new_transaction_row,
        delete_if_exists=delete_if_exists,
        verbose=verbose,
        copy_indexes=copy_indexes,
    )

    (
        source_head_schema,
        source_head_name,
    ) = __parse_table_name(transaction_head)

    # Populate data in new_transaction_head table
    sql = f"""
    INSERT INTO `{target_head_schema}`.`{target_head_name}` AS th_target
        SELECT th_source.* FROM `{source_head_schema}`.`{source_head_name}` AS th_source
        INNER JOIN `{heads_schema}`.`{heads_table}` AS heads_table ON th_source.id = heads_table.`{head_ids_column}`
    ON CONFLICT(id) DO NOTHING;
    """
    if verbose:
        print(sql)
    conn.execute(sql)

    (
        source_row_schema,
        source_row_name,
    ) = __parse_table_name(transaction_row)

    # Populate data in new_transaction_row_table
    sql = f"""
    INSERT INTO `{target_row_schema}`.`{target_row_name}` AS tr_target
        SELECT tr_source.* FROM `{source_row_schema}`.`{source_row_name}` AS tr_source
        INNER JOIN `{heads_schema}`.`{heads_table}` AS heads_table ON tr_source.head_id = heads_table.`{head_ids_column}`
    ON CONFLICT(id) DO NOTHING;
    """
    if verbose:
        print(sql)
    conn.execute(sql)

    conn.commit()
