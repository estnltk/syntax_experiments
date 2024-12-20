import os
import sqlite3
from typing import List
from estnltk.storage.postgres import PostgresStorage
import pandas as pd

def get_transaction_examples(
    connection: sqlite3.Connection, 
    transactions: str, 
    transaction_head: str, 
    mainverb: str, 
    comp: str, 
    kaane: str,
    only_elus:bool,
    only_koht:bool,
    num_samples:int 
    ):
    """
    Fetches transaction information for given verb and case.
    Parameters:
        connection: sqlite3.Connection - The SQLite database connection object.
        transactions: str - The name of the transaction table.
        transaction_head: str - The name of the transaction_head table.
        mainverb: str - The main verb word.
        comp: str - Verb compound.
        kaane: str - Verb case.
        only_elus: bool - Select only elus=YES examples.
        only_koht: bool - Select only koht=YES examples.
        num_samples:int - Number of random samples. If value is -1 then all samples are given.
    Returns pandas dataframe.
    """

    query = """
    SELECT distinct 
        head.id as head_id,
        head.sentence_id as sentence_id,
        head.verb,
        head.verb_compound as verb_compound,
        head.loc as verb_loc,
        head.form as verb_form,
        tr.deprel as root_deprel,
        '{kaane1}' as kaane,
        tr.lemma as root_lemma,
        tr.form as root_form,
        tr.loc as root_loc,
        tr.loc_rel as root_loc_rel,
        tr.parent_loc as root_parent_loc,
        tr.koht as koht,
        tr.elus as elus
    from 
    (select * from entrans.{enrich}
    where deprel = 'obl'
    and INSTR(',' || feats || ',', ',' || '{kaane1}' || ',') > 0) as tr
    join 
    (select * from trans.{head}
    where verb == '{mainverb}'
    and verb_compound == '{comp}') as head
    on head.id = tr.head_id
    """.format(kaane1 = kaane, enrich=transactions, head=transaction_head, mainverb=mainverb,comp=comp)

    df= pd.read_sql_query(query, connection)

    if only_elus:
        df = df[df["elus"]=='YES']
    elif only_koht:
        df = df[df["koht"]=='YES']
    
    if num_samples!= -1:
        if num_samples>len(df):
            num_samples = len(df)
        df = df.sample(n=num_samples, random_state=1)

    return df


def get_koondkorpus_examples(
    collection: PostgresStorage,
    examples: pd.DataFrame
    ):
    """
    Fetches sentences from koondkorpus based on sentence_id column in given dataframe.
    Parameters:
        collection: PostgresStorage - Koondkorpus collection.
        examples. pandas dataframe of example verbs and root words.
    Returns modified pandas dataframe.
    """
    
    sentence_ids = list(examples["sentence_id"])
    sentences = []
    for sentid in sentence_ids:
        sentences.append(collection[sentid].text)

    examples["sentence"] = sentences

    return examples


