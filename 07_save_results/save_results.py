import os
import re
from collections import defaultdict, namedtuple

import pandas as pd
from estnltk import Layer
from estnltk.converters.conll_importer import conll_to_texts_list
from estnltk.storage import PostgresStorage
from estnltk.storage.postgres import PgCollection

from converters.conllu_importer import conllu_file_to_texts_list
from syntaxsplitter import split_syntax_by_sentences

RowMapperRecord = namedtuple('RowMapperRecord', ['layer', 'meta'])


def save_udpipe_output(file: str, results: pd.DataFrame, experiment_name: str) -> pd.DataFrame:
    split = file.split('_')[-1].replace('.txt', '')
    parsed = file.split('_')[-2]
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')[0].split(' ')
    LA = '-'
    ACC = '-'
    LAS = lines[-1]
    UAS = lines[-3]
    results = results.append(
        {'Experiment': experiment_name, 'Model': 'udpipe', 'Parsed file': parsed, 'Split': split, 'LAS': LAS,
         'ACC': ACC,
         'LA': LA, 'UAS': UAS}, ignore_index=True)
    return results


def save_malt_output(file, results, experiment_name):
    split = file.split('_')[-1].replace('.txt', '')
    parsed = file.split('_')[-2]
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    result = re.sub(r' +', ' ', lines[11])
    result = result.split(' ')
    LA = result[0].strip()
    ACC = result[1].strip()
    LAS = result[2].strip()
    results = results.append(
        {'Experiment': experiment_name, 'Model': 'malt', 'Parsed file': parsed, 'Split': split, 'LAS': LAS, 'ACC': ACC,
         'LA': LA, 'UAS': '-'}, ignore_index=True)
    return results


def add_to_dictionary(dic: defaultdict, file: str, splits: pd.DataFrame, experiment: str, model: str) -> defaultdict:
    """
    käime läbi faili, lisame kaasaantud dictionary teksti as key and layer as value
    :param dic: where to save the output layers (key is the text of the Text object)
    :param file: file where to get the text objects
    :param splits: how the data is splitted
    :param experiment:
    :param model:
    :return:
    """
    split = 'split_' + str(int(file.split('_')[-1].replace('.conllu', '')) + 1)
    # for saving the split as meta to
    layer_name = experiment + '_' + model + '_result'
    text_list = conllu_file_to_texts_list(file, layer_name)
    #text_list = split_syntax_by_sentences(conll_to_texts_list(file, layer_name)[0], layer_name)
    for i, text in enumerate(text_list):
        dic[text.text] = text[layer_name]
    return dic


def add_parsed(dic: defaultdict, collection: PgCollection, layer: str):
    data_iter = [(i[0], i[1], dic.get(i[1].text)) for i in collection.select(collection_meta=['chunk'])]
    print(data_iter[0])

    #collection.create_layer(layer_name=layer, data_iterator=data_iter, row_mapper=createRowMapperRecord)


def createRowMapperRecord(row):
    layer = row[2]
    meta = {}
    return RowMapperRecord(layer=layer, meta=meta)


def save_results(collection: PgCollection, collection_name: str) -> None:
    """
    Iterates over all the generated files during training, predicting and evaluating and saves the important parts
    :param collection: Collection where to save the parsed conll-u files as a new layer
    :return: None
    """
    results_df = pd.DataFrame(columns=['Experiment', 'Model', 'Parsed file', 'Split', 'LAS', 'ACC', 'LA', 'UAS'])

    for experiment in os.listdir('../04_train_models/output/%s/' % collection_name):
        splits = pd.read_csv('../03_create_training_testing_data/output/%s/%s/splits.csv' % (collection_name, experiment))


        layers = defaultdict(Layer)

        for file in os.listdir('../03_train_models/output/%s/%s/malt/' % (collection_name, experiment)):
            if 'output_' in file:
                results_df = save_malt_output(
                    '../03_train_models/output/%s/%s/malt/%s' % (collection_name, experiment, file), results_df,
                    experiment)
            if 'parsed_test' in file:
                layers = add_to_dictionary(layers, '../03_train_models/output/%s/%s/malt/%s' % (
                    collection_name, experiment, file),
                                           splits, experiment, 'malt')
        add_parsed(dic=layers, collection=collection, layer=experiment + '_malt_result')

        layers = defaultdict(Layer)
        for file in os.listdir('../03_train_models/output/%s/%s/udpipe/' % (collection_name, experiment)):

            if 'output_' in file:
                results_df = save_udpipe_output(
                    '../03_train_models/output/%s/%s/udpipe/%s' % (collection_name, experiment, file),
                    results_df, experiment)

            if 'parsed_test' in file:
                layers = add_to_dictionary(layers, '../03_train_models/output/%s/%s/udpipe/%s' % (
                    collection_name, experiment, file),
                                           splits, experiment, 'udpipe')
        add_parsed(dic=layers, collection=collection, layer=experiment + '_udpipe_result')

    results_df.to_csv("all_results.csv")


if __name__ == '__main__':
    storage = PostgresStorage(pgpass_file='../db_conn.pgpass',
                              password='',
                              schema='syntaxexperiments'
                              )

    collection = storage['edt']
    save_results(collection, 'edt')
    collection = storage['est_ud']
    save_results(collection, 'est_ud')
    storage.close()
