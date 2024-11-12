from sqlalchemy import Column, Integer, Text, Table, MetaData, text, select, insert

from sqlalchemy.schema import ForeignKey, UniqueConstraint, Index

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

# Define the transaction_head table
transaction_head_table = Table(
    "transaction_head",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sentence_id", Integer),
    Column("loc", Integer),
    Column("verb", Text),
    Column("verb_compound", Text),
    Column("deprel", Text),
    Column("feats", Text),
    Column("form", Text),
    Column("phrase", Text),
    Index("th_verb", "verb"),
    Index("th_verb_compound", "verb_compound"),
    Index("th_verb_verb_compound", "verb", "verb_compound"),
    Index("th_deprel", "deprel"),
    Index("th_feats", "form"),
)

# Define the transaction_row table
transaction_table = Table(
    "transaction_row",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("head_id", Integer, ForeignKey("transaction_head.id")),
    Column("loc", Integer),
    Column("loc_rel", Integer),
    Column("deprel", Text),
    Column("form", Text),
    Column("lemma", Text),
    Column("feats", Text),
    Column("pos", Text),
    Column("parent_loc", Integer),
    Index("tr_head_id", "head_id"),
    Index("tr_loc_rel", "loc_rel"),
    Index("tr_lemma", "lemma"),
    Index("tr_form", "form"),
    Index("tr_deprel", "deprel"),
    Index("tr_pos", "pos"),
    Index("tr_feats", "form"),
)


def reset_tables(engine):
    metadata.drop_all(engine)
    metadata.create_all(engine)


def copy_patterns_table(conn):
    sql = "CREATE TABLE `patterns` AS SELECT * FROM db_pat.`patterns`"
    conn.execute(text(sql))
    conn.commit()


def fill_table_verbs(conn):
    select_stmt = (
        select(
            text("verb_word as verb"),
            text("verb_compound"),
            text("GROUP_CONCAT(pat_id) as pat_ids"),
        )
        .select_from(text("patterns"))
        .group_by(text("verb_word"), text("verb_compound"))
        .order_by(text("verb_word"), text("verb_compound"), text("pat_id"))
    )
    insert_stmt = insert(verbs_table).from_select(
        [
            "verb",
            "verb_compound",
            "pat_ids",
        ],
        select_stmt,
    )

    conn.execute(insert_stmt)
    conn.commit()


def fill_table_verb_transactions(conn, verb_id, pat_ids):
    # leiame iga verbi kohta transaktsioonide ID-d, mis pole mustriga kaetud
    # leiame PATH_PATTERNS_DB baasis olevate andmete põhjal
    pat_ids_str = ",".join([str(id) for id in pat_ids])
    conn.execute(
        text(
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
    )
    conn.commit()


def fill_table_transaction_head(
    conn,
):
    # täidame transaction_head tabeli, võtab ca paarkümmend minutit aega
    column_names = [column.name for column in transaction_head_table.columns]
    columns_str1 = " ,".join([f"`{c}`" for c in column_names])
    columns_str2 = " ,".join([f"th.`{c}`" for c in column_names])

    sql = f"""
    INSERT INTO `transaction_head` ({columns_str1})
        SELECT {columns_str2} FROM db_tr.`transaction_head` th
        INNER JOIN verb_transactions v_th ON th.id = v_th.head_id
    ON CONFLICT(id) DO NOTHING;
    """
    conn.execute(text(sql))
    conn.commit()


def fill_table_transaction_row(conn):
    column_names = [column.name for column in transaction_table.columns]
    columns_str1 = " ,".join([f"`{c}`" for c in column_names])
    columns_str2 = " ,".join([f"tr.`{c}`" for c in column_names])

    sql = f"""
    INSERT INTO `transaction_row` ({columns_str1})
        SELECT {columns_str2} FROM db_tr.`transaction_row` tr
        INNER JOIN transaction_head th ON th.id = tr.head_id
    ON CONFLICT(id) DO NOTHING;
    """

    conn.execute(text(sql))
    conn.commit()


def show_verb_trans_stat(conn, verb):
    print('verb', verb)
    # compare data of
    #   db_pat
    #   db_tr
    #   kala777
    sql = (
        """
    SELECT COUNT(DISTINCT vm.head_id) AS total
    FROM db_pat.verb_matches AS vm
    WHERE vm.pat_id IN(%s)
    """
        % verb["pat_ids"]
    )
    total = conn.execute(text(sql)).scalar()

    print("db_pat total:", total)

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
    total = conn.execute(text(sql)).scalar()
    print("db_pat unmatched:", total)

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
    total = conn.execute(text(sql)).scalar()
    print("db_pat matched:", total)

    sql = """
    SELECT COUNT(DISTINCT th.id) AS total
    FROM db_tr.transaction_head AS th
    WHERE th.verb = :verb AND th.verb_compound = :verb_compound
    """
    total = conn.execute(
        text(sql), {"verb": verb["verb"], "verb_compound": verb["verb_compound"]}
    ).scalar()

    print("db_tr all:", total)

    sql = """
    SELECT COUNT(head_id) AS total
    FROM verb_transactions AS vt
    WHERE vt.verb_id = :verb_id
    """
    total = conn.execute(text(sql), {"verb_id": verb["verb_id"]}).scalar()

    print("kala77 all:", total)
    print(" ")
