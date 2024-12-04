
def update_table(connection, table_name, column_name, new_value, condition):
        c = connection.cursor()
        
        c.execute("""
        UPDATE {table}
        SET {column} = {value}
        WHERE {condition}
        """.format(table=table_name, column=column_name, value=new_value, condition=condition)
                )
        connection.commit()


def create_count_table_distinct(connection, source_table_name, result_table_name, selected_columns, 
                      count_column, count_col_name, condition, group_by_columns):
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


def create_count_table(connection, source_table_name, result_table_name, selected_columns, 
                      count_column, count_col_name, condition, group_by_columns):
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


def create_left_join_table(connection, source_tbl1, source_tbl2, result_table, selected_columns, condition):
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