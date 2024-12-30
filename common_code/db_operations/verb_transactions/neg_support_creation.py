# imports
import sqlite3

def create_verb_neg_support_table(cur, transaction_head: str, verb_neg_matches: str, output_table: str):
    """
    Finds total and negated form frequecies of verbs / verb compounds and calculates relative negation support for each verb (compound). Creates a new table containing this information.
    
    Parameters:
            cur - SQLite Cursor-object
            transaction_head - transaction head table name
            verb_neg_matches - name of table containing negation pattern matches found from transactions
            output_table - output table name
            
    """
    cur.execute("""
    DROP TABLE IF EXISTS {output_table}
    """.format(output_table=output_table))

    cur.execute("""
    CREATE TABLE {output_table} AS
    SELECT
        tbl2.verb,
        tbl2.verb_compound,
        all_matches,
        neg_matches,
        CAST(neg_matches AS REAL) / CAST(all_matches AS REAL) * 100 AS relative_support
    
    FROM
    (
        SELECT
            id,
            verb,
            verb_compound,
            count(*) as all_matches
        FROM
            {transaction_head}
        GROUP BY
            verb, verb_compound
    ) as tbl1
    INNER JOIN
    (
        SELECT
            id,
            verb,
            verb_compound,
            count(*) as neg_matches
        FROM
            {verb_neg_matches} as verb_neg
        INNER JOIN
            {transaction_head} as tr_head2
        ON
            verb_neg.head_id=tr_head2.id
        GROUP BY
            verb, verb_compound
    ) as tbl2
    ON
        tbl1.id = tbl2.id
    GROUP BY
        tbl2.verb, tbl2.verb_compound
    ORDER BY
        relative_support DESC
    """.format(output_table=output_table, transaction_head=transaction_head, verb_neg_matches=verb_neg_matches))