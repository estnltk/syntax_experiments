from sqlalchemy import Column, Integer, Text, Table, MetaData

from sqlalchemy.schema import UniqueConstraint, Index

# tables defined for quick creation

metadata = MetaData()
verbs_table = Table(
    "verbs",
    metadata,
    Column("verb_id", Integer, primary_key=True, autoincrement=True),
    Column("verb", Text),
    Column("verb_compound", Text),
    Column("pat_ids", Text),
    Index("ix_v_verb_verb_compound", "verb", "verb_compound"),
)

verb_transactions = Table(
    "verb_transactions",
    metadata,
    Column("verb_id", Integer, primary_key=True),
    Column("head_id", Integer, primary_key=True),
    UniqueConstraint("verb_id", "head_id", name="uix_verb_head"),
)


def reset_tables(engine):
    metadata.drop_all(engine)
    metadata.create_all(engine)


def fill_table_verbs(conn):
    conn.execute(
        """
        INSERT INTO verbs (verb, verb_compound, pat_ids)
        SELECT 
            verb_word AS verb,
            verb_compound,
            GROUP_CONCAT(pat_id) AS pat_ids
        FROM patterns
        GROUP BY verb_word, verb_compound
        ORDER BY verb_word, verb_compound, pat_id;"""
    )
    conn.commit()


def fill_table_verb_transactions(conn, verb_id, pat_ids):
    # leiame iga verbi kohta transaktsioonide ID-d, mis pole mustriga kaetud
    # leiame PATH_PATTERNS_DB baasis olevate andmete põhjal
    pat_ids_str = ",".join([str(id) for id in pat_ids])
    conn.execute(
        """
        INSERT INTO verb_transactions (verb_id, head_id)
        SELECT %i, h.head_id FROM
            (SELECT DISTINCT head_id
        FROM verb_matches
        WHERE pat_id IN (%s)
        AND head_id NOT IN (
            SELECT head_id
            FROM verb_phrase_matches
            WHERE pat_id IN (%s)
            )) as h;
            """
        % (
            verb_id,
            pat_ids_str,
            pat_ids_str,
        )
    )
    conn.commit()


def show_verb_trans_stat(conn, verb, trx_source_schema, patterns_src_schema):
    print("verb", verb)
    # compare data of
    #   {trx_source_schema}
    #   {trx_source_schema}
    #   uncovered_transactions
    sql = (
        f"""
    SELECT COUNT(DISTINCT vm.head_id) AS total
    FROM {patterns_src_schema}.verb_matches AS vm
    WHERE vm.pat_id IN(%s)
    """
        % verb["pat_ids"]
    )
    total = conn.execute(sql).fetchone()[0]

    print(f"{patterns_src_schema} total:", total)

    sql = """
    SELECT COUNT(DISTINCT head_id)
    FROM verb_matches
    WHERE pat_id IN (%s)
        AND head_id NOT IN (
            SELECT head_id
            FROM verb_phrase_matches
            WHERE pat_id IN (%s)
    )
    """ % (
        verb["pat_ids"],
        verb["pat_ids"],
    )
    total = conn.execute(sql).fetchone()[0]
    print(f"{patterns_src_schema} unmatched:", total)

    sql = """
    SELECT COUNT(DISTINCT head_id)
    FROM verb_matches
    WHERE pat_id IN (%s)
        AND head_id IN (
            SELECT head_id
            FROM verb_phrase_matches
            WHERE pat_id IN (%s)
    )
    """ % (
        verb["pat_ids"],
        verb["pat_ids"],
    )
    total = conn.execute(sql).fetchone()[0]
    print(f"{patterns_src_schema} matched:", total)

    sql = f"""
    SELECT COUNT(DISTINCT th.id) AS total
    FROM {trx_source_schema}.transaction_head AS th
    WHERE th.verb = :verb AND th.verb_compound = :verb_compound
    """
    total = conn.execute(
        sql, {"verb": verb["verb"], "verb_compound": verb["verb_compound"]}
    ).fetchone()[0]

    print(f"{trx_source_schema} all:", total)

    sql = """
    SELECT COUNT(head_id) AS total
    FROM verb_transactions AS vt
    WHERE vt.verb_id = :verb_id
    """
    total = conn.execute(sql, {"verb_id": verb["verb_id"]}).fetchone()[0]

    print("uncovered_transactions all:", total)
    print(" ")
