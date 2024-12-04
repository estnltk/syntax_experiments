# imports
import sqlite3
#from .db_checks import is_valid_table_name, is_db_table, check_all_col_names

def create_verb_neg_table(cur, verb_matches: str, transaction_head: str, output_table: str):
    cur.execute("""
    DROP TABLE IF EXISTS {output_table}
    """.format(output_table=output_table))

    cur.execute("""
    CREATE TABLE {output_table} AS
    SELECT DISTINCT
        id,
        verb,
        verb_compound,
        form,
        deprel,
        feats    
    FROM
    (
        SELECT
            head_id
        FROM
            {verb_matches}
        INNER JOIN
            {transaction_head} as tr_head
        ON
            head_id = tr_head.id
    ) as tbl
    INNER JOIN
        {transaction_head} as tr_head2
    ON
        tbl.head_id = tr_head2.id
    WHERE
        instr(tr_head2.feats, 'neg') > 0
    """.format(output_table=output_table, verb_matches=verb_matches, transaction_head=transaction_head))


def create_verb_neg_phrase_table(cur, verb_neg: str, transaction_row: str, output_table: str):
    cur.execute("""
    DROP TABLE IF EXISTS {output_table}
    """.format(output_table=output_table))

    cur.execute("""
    CREATE TABLE {output_table} AS
    SELECT
        head_id,
        loc,
        loc_rel,
        tr.deprel,
        tr.form,
        lemma,
        tr.feats,
        parent_loc,
        pos
    FROM
        {verb_neg} as verb_neg
    INNER JOIN
        {transaction_row} as tr
    ON
        verb_neg.id = tr.head_id
    """.format(output_table=output_table, verb_neg=verb_neg, transaction_row=transaction_row))


def create_verb_neg_support_table(cur, verb_matches: str, transaction_head: str, verb_neg: str, output_table: str):
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
            head_id,
            verb,
            verb_compound,
            count(*) as all_matches
        FROM
            {verb_matches}
        INNER JOIN
            {transaction_head} as tr_head
        ON
            head_id = tr_head.id
        GROUP BY
            tr_head.verb, tr_head.verb_compound
    ) as tbl1
    INNER JOIN
    (
        SELECT
            id,
            verb,
            verb_compound,
            count(*) as neg_matches
        FROM
            {verb_neg} as verb_neg
        GROUP BY
            verb_neg.verb, verb_neg.verb_compound
    ) as tbl2
    ON
        tbl1.head_id = tbl2.id
    GROUP BY
        tbl2.verb, tbl2.verb_compound
    ORDER BY
        relative_support DESC
    """.format(output_table=output_table, verb_matches=verb_matches, transaction_head=transaction_head, verb_neg=verb_neg))


def create_neg_patterns_table(cur, verb_neg: str, verb_neg_phrases: str, output_table: str):
    cur.execute("""
    DROP TABLE IF EXISTS {output_table}
    """.format(output_table=output_table))

    cur.execute("""
    CREATE TABLE {output_table} (
        pat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        form TEXT,
        deprel TEXT
    )
    """.format(output_table=output_table))

    cur.execute("""
    INSERT INTO {output_table} (
        form,
        deprel
    )
    SELECT DISTINCT
        form,
        deprel
    FROM
        {verb_neg}
    WHERE
        verb='olema'
    AND
        instr(form, 'pol') > 0
    OR
        instr(form, 'Pol') > 0
    """.format(output_table=output_table, verb_neg=verb_neg))

    cur.execute("""
    INSERT INTO {output_table} (
        form,
        deprel
    )
    SELECT DISTINCT
        form,
        deprel
    FROM
        {verb_neg_phrases}
    WHERE
        lemma='ei'
    AND
        instr(feats, 'neg') > 0
    AND
        deprel='aux'
    """.format(output_table=output_table, verb_neg_phrases=verb_neg_phrases))

    cur.execute("""
    INSERT INTO {output_table} (
        form,
        deprel
    )
    SELECT DISTINCT
        form,
        deprel
    FROM
        {verb_neg_phrases}
    WHERE
        lemma='ära'
    AND
        instr(feats, 'neg') > 0
    AND
        deprel='aux'
    """.format(output_table=output_table, verb_neg_phrases=verb_neg_phrases))
    cur.connection.commit()


def create_neg_feats_table(cur, neg_patterns: str, verb_neg: str, verb_neg_phrases: str, output_table: str):
    cur.execute("""
    DROP TABLE IF EXISTS {output_table}
    """.format(output_table=output_table))

    cur.execute("""
    CREATE TABLE {output_table} (
        pat_id INTEGER,
        feats TEXT
    )
    """.format(output_table=output_table))

    cur.execute("""
    INSERT INTO {output_table} (
        pat_id,
        feats
        )
    SELECT DISTINCT
        pat_id,
        feats
    FROM
    (
        SELECT
            pat_id,
            form,
            deprel
        FROM
            {neg_patterns} AS pat
    ) AS tbl
    INNER JOIN
        {verb_neg} AS verb_neg
    ON
        (tbl.form=verb_neg.form AND tbl.deprel=verb_neg.deprel)   
    WHERE
        verb_neg.verb='olema'
    AND
        instr(verb_neg.form, 'pol') > 0
    OR
        instr(verb_neg.form, 'Pol') > 0
    """.format(output_table=output_table, neg_patterns=neg_patterns, verb_neg=verb_neg))

    cur.execute("""
    INSERT INTO {output_table} (
        pat_id,
        feats
    )
    SELECT DISTINCT
        pat_id,
        feats
    FROM
    (
        SELECT
            pat_id,
            form,
            deprel
        FROM
            {neg_patterns} AS pat
    ) as tbl
    INNER JOIN
        {verb_neg_phrases} AS phrases
    ON
        (tbl.form=phrases.form AND tbl.deprel=phrases.deprel)
    WHERE
        lemma='ei'
    AND
        instr(feats, 'neg') > 0
    AND
        phrases.deprel='aux'
    """.format(output_table=output_table, neg_patterns=neg_patterns, verb_neg_phrases=verb_neg_phrases))

    cur.execute("""
    INSERT INTO {output_table} (
        pat_id,
        feats
    )
    SELECT DISTINCT
        pat_id,
        feats
    FROM
    (
        SELECT
            pat_id,
            form,
            deprel
        FROM
            {neg_patterns} AS pat
    ) AS tbl
    INNER JOIN
        {verb_neg_phrases} AS phrases
    ON
        (tbl.form=phrases.form AND tbl.deprel=phrases.deprel)
    WHERE
        lemma='ära'
    AND
        instr(feats, 'neg') > 0
    AND
        phrases.deprel='aux'
    """.format(output_table=output_table, neg_patterns=neg_patterns, verb_neg_phrases=verb_neg_phrases))
    cur.connection.commit()

def create_neg_tables(cur, verb_matches: str, transaction_head: str, transaction_row: str):
    create_verb_neg_table(cur, verb_matches, transaction_head, 'verb_neg')
    create_verb_neg_phrase_table(cur, 'verb_neg', transaction_row, 'verb_neg_phrases')
    create_verb_neg_support_table(cur, verb_matches, transaction_head, 'verb_neg', 'verb_neg_support')
    create_neg_patterns_table(cur, 'verb_neg', 'verb_neg_phrases', 'neg_patterns')
    create_neg_feats_table(cur, 'neg_patterns', 'verb_neg', 'verb_neg_phrases', 'neg_feats')