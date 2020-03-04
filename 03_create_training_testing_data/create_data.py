import os
from collections import OrderedDict
from random import shuffle
from typing import List

import pandas as pd
from conllu import TokenList
from estnltk import Span, Layer
from estnltk.storage import PostgresStorage
from estnltk.storage.postgres import PgCollection

ALL_EXPERIMENTS = ['gm_experiment_1', 'am_experiment_1', 'gm_experiment_2', 'am_experiment_2', 'gm_experiment_3',
                   'am_experiment_3', 'gm_experiment_3_2', 'am_experiment_3_2', 'gm_experiment_4', 'am_experiment_4',
                   'gm_experiment_4_2', 'am_experiment_4_2', 'gm_experiment_5', 'am_experiment_5', 'gm_experiment_6',
                   'am_experiment_6', 'gm_experiment_6_2', 'am_experiment_6_2', 'gm_experiment_7', 'am_experiment_7',
                   'gm_experiment_7_2', 'am_experiment_7_2'
                                        'gm_experiment_8', 'am_experiment_8', 'gm_experiment_8_2', 'am_experiment_8_2',
                   'gm_experiment_9',
                   'am_experiment_9', 'gm_experiment_10', 'am_experiment_10', 'gm_experiment_11', 'am_experiment_11',
                   'gm_experiment_12', 'am_experiment_12', 'gm_experiment_13', 'am_experiment_13', 'gm_experiment_14',
                   'am_experiment_14']


def split(a: List[int], n: int) -> List[List[int]]:
    """
    Creates folds
    :param a: data from what to create the folds
    :param n: how many folds
    :return: list of folds
    """
    k, m = divmod(len(a), n)
    return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def sentence_to_conll(sentence_span: Span, conll_layer: Layer) -> str:
    get_conll = conll_layer.get
    tokens = []

    for word in sentence_span:
        a = get_conll(word).annotations[0]
        token = OrderedDict([('id', a.id),
                             ('form', a.text),
                             ('lemma', a.lemma),
                             ('upostag', a.upostag),
                             ('xpostag', a.xpostag),
                             ('feats', a.feats),
                             ('head', a.head),
                             ('deprel', a.deprel),
                             ('deps', a.deps),
                             ('misc', a.misc)])
        tokens.append(token)

    result = TokenList(tokens).serialize()

    return result.replace('=|', '|')


def save_splits_to_df(collection_name: str, splits: List[List[int]], experiment_layer: str) -> None:
    df_for_splits = pd.DataFrame({
        'split_1': [splits[0]], 'split_2': [splits[1]], 'split_3': [splits[2]], 'split_4': [splits[3]],
        'split_5': [splits[4]], 'split_6': [splits[5]], 'split_7': [splits[6]], 'split_8': [splits[7]],
        'split_9': [splits[8]],
        'split_10': [splits[9]]})
    df_for_splits.to_csv('output/%s/%s/splits.csv' % (collection_name, experiment_layer))


def create_opt_data(collection: PgCollection, experiment_layer: str, collection_name: str) -> None:
    """
    Creates conll file for the MaltOptimizer
    :param collection: PostgreStorage with collections
    :param experiment_layer: experiment layer where to take the info
    :param collection_name: name of the collection to save file to correct folder
    :return: Nothing
    """
    opt_data = open('output/%s/%s/malt_opt.conll' % (collection_name, experiment_layer), 'w',
                    encoding='utf-8')

    for i, text in collection.select(layers=[experiment_layer, 'sentences']):
        try:
            t = sentence_to_conll(text.sentences[0], text[experiment_layer])
            opt_data.write(t)
        except:
            print("Couldn't write ")


def create_data(s: List[int], collection: PgCollection, experiment_layer: str, i: int,
                collection_name: str) -> None:
    """
    Saves training files for the parsers
    :param i: split number
    :param s: test set texts' ids
    :param collection: colelction where the text objects are
    :param experiment_layer: experiment layer attached to texts
    :param model: Malt or udpipe
    :return: Nothing
    """
    assert experiment_layer in collection.selected_layers
    trainset = open('output/%s/%s/train_%s.conllu' % (collection_name, experiment_layer, str(i)), 'w',
                    encoding='utf-8')
    testset = open('output/%s/%s/test_%s.conllu' % (collection_name, experiment_layer, str(i)), 'w',
                   encoding='utf-8')

    for i, text, meta in collection.select(collection_meta=['chunk'], layers=[experiment_layer, 'sentences']):
        chunk_nr = int(meta.get('chunk'))
        try:
            t = sentence_to_conll(text.sentences[0], text[experiment_layer])

            testset.write(t) if chunk_nr in s else trainset.write(t)
        except AttributeError as e:
            print(e)
            print(text)

    trainset.close()
    testset.close()


def create_splits(collection_name: str, experiment_layer: str, collection: PgCollection,
                  files: int) -> None:
    """
    :param collection_name:
    :param experiment_layer:
    :param collection:
    :param model:
    :param files:
    :return:
    """
    chunks = [i for i in range(files)]
    shuffle(chunks)
    splits = split(chunks, 10)

    collection.selected_layers.append(experiment_layer)
    if collection_name not in os.listdir('output'):
        os.mkdir('output/' + collection_name)
        os.mkdir('output/' + collection_name + "/" + experiment_layer)

    if experiment_layer not in os.listdir('output/' + collection_name):
        os.mkdir('output/' + collection_name + "/" + experiment_layer)


    save_splits_to_df(collection_name, splits, experiment_layer)
    create_opt_data(collection=collection, experiment_layer=experiment_layer, collection_name=collection_name)
    for i, s in enumerate(splits):
        create_data(s=s, collection=collection, experiment_layer=experiment_layer, i=i,
                    collection_name=collection_name)


if __name__ == '__main__':
    storage = PostgresStorage(pgpass_file='../db_conn.pgpass',
                              password='tLNzbPBKIF6ea2EX',
                              schema='syntaxexperiments'
                              )
    edt = storage['edt']
    ud = storage['est_ud']
    for experiment in ALL_EXPERIMENTS:
        print("Creating data for %s" % (experiment))
        create_splits('edt', experiment, edt, 232)
        create_splits('est_ud', experiment, ud, len(ud))
