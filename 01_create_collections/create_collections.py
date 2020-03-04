import os
from collections import defaultdict
from typing import List

from estnltk import Text
from estnltk.storage import PostgresStorage
from estnltk.storage.postgres import create_schema, PgCollection

from converters.conll_to_conllu_format import conll_to_conllu_text_list
from converters.conllu_importer import conllu_file_to_texts_list


def create_collections() -> None:
    """
    Creates 2 separate PostgreStorage collections for two data sources: EDT and EstUD
    :return: None
    """
    storage = PostgresStorage(pgpass_file='../db_conn.pgpass',
                              password='',
                              schema='syntaxexperiments'
                              )

    create_schema(storage)
    storage['est_ud'].meta = {'file': 'str', 'chunk': 'str', 'order': 'str'}
    storage['est_ud'].create('Collection containing Est-UD texts with syntax-gold and experiment layers.')
    storage['est_ud'].column_names += list(storage['est_ud'].meta.keys())
    collection = storage['est_ud']
    insert(datafolder='original_data/EstUD', collection=collection, collection_name='est_ud')

    storage['edt'].meta = {'file': 'str', 'chunk': 'str', 'order': 'str'}
    storage['edt'].create('Collection containing EDT texts with syntax-gold and experiment layers.')
    storage['edt'].column_names += list(storage['edt'].meta.keys())
    collection = storage['edt']
    insert(datafolder='original_data/EDT', collection=collection, collection_name='edt')
    storage.close()


def insert(datafolder: str, collection: PgCollection, collection_name: str) -> None:
    with collection.insert() as collection_insert:
        k = 0
        for i, file in enumerate(os.listdir(datafolder)):
            filename = os.fsdecode(file)
            print(filename)

            file_meta = filename.split('.')[0]
            chunk_meta = str(i)

            if collection_name == 'edt':
                text_list = conll_to_conllu_text_list(file=datafolder + '/' + file)
            elif collection_name == 'est_ud':
                text_list = conllu_file_to_texts_list(file=datafolder + '/' + file)
            for j, text in enumerate(text_list):

                if not iscycle(text):
                    try:
                        meta = {'file': file_meta, 'chunk': chunk_meta if collection_name == 'edt' else str(k),
                                'order': str(j)}
                        collection_insert(text=text, meta_data=meta)
                        k += 1
                    except:
                        print("Couldn't add. " + chunk_meta)


def iscycle(text: Text) -> bool:
    dic = defaultdict(list)
    for span in text.syntax_gold:
        dic[int(span.id)].append(int(span.head))
    visited = [False] * (len(dic) + 1)
    recstack = [False] * (len(dic) + 1)

    for val in range(1, len(dic)):
        if not visited[val]:
            if iscyclic(val=val, visited=visited, recstack=recstack, dic=dic):
                return True
    return False


def iscyclic(val: int, visited: List[int], recstack: List[int], dic: defaultdict) -> bool:
    visited[val] = True
    recstack[val] = True

    for nb in dic.get(val):
        if len(visited) >= nb and not visited[nb] and dic[nb] != []:
            if iscyclic(val=nb, visited=visited, recstack=recstack, dic=dic):
                return True
        elif len(recstack) >= nb and recstack[nb]:
            return True
    recstack[val] = False
    return False


if __name__ == '__main__':
    create_collections()
