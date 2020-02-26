import os
import subprocess
from collections import OrderedDict
from random import shuffle
from typing import List

import pandas as pd
from conllu import TokenList
from estnltk import Span, Layer
from estnltk.storage import PostgresStorage
from estnltk.storage.postgres.collection import PgCollection

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
GM_EXPERIMENTS = ['gm_experiment_1', 'gm_experiment_2', 'gm_experiment_3',
                  'gm_experiment_3_2', 'gm_experiment_4',
                  'gm_experiment_4_2', 'gm_experiment_5', 'gm_experiment_6',
                  'gm_experiment_6_2', 'gm_experiment_7', 'gm_experiment_7_2'
                                                          'gm_experiment_8', 'gm_experiment_8_2', 'gm_experiment_9',
                  'gm_experiment_10', 'gm_experiment_11',
                  'gm_experiment_12', 'gm_experiment_13', 'gm_experiment_14',
                  ]
GM_EXPERIMENTS_1 = ['gm_experiment_2', 'gm_experiment_3',
                    'gm_experiment_3_2', 'gm_experiment_4',
                    'gm_experiment_4_2', 'gm_experiment_5', 'gm_experiment_6',
                    'gm_experiment_6_2', 'gm_experiment_7', 'gm_experiment_7_2'
                                                            'gm_experiment_8', 'gm_experiment_8_2', 'gm_experiment_9',
                    'gm_experiment_10', 'gm_experiment_11',
                    'gm_experiment_12', 'gm_experiment_13', 'gm_experiment_14',
                    ]
TEST = ['syntax_gold']

def split(a: List[int], n: int) -> List[List[int]]:
    """
    Creates folds
    :param a: data from what to create the folds
    :param n: how many folds
    :return: list of folds
    """
    k, m = divmod(len(a), n)
    return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def save_splits_to_df(collection_name: str, splits: List[List[int]], model: str, experiment_layer: str) -> None:
    df_for_splits = pd.DataFrame({
        'model': model, 'split_1': [splits[0]], 'split_2': [splits[1]], 'split_3': [splits[2]], 'split_4': [splits[3]],
        'split_5': [splits[4]], 'split_6': [splits[5]], 'split_7': [splits[6]], 'split_8': [splits[7]],
        'split_9': [splits[8]],
        'split_10': [splits[9]]})
    df_for_splits.to_csv('output/%s/%s/%s/splits.csv' % (collection_name, experiment_layer, model))


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


def create_training_data(s: List[int], collection: PgCollection, experiment_layer: str, i: int, model: str,
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
    trainset = open('output/%s/%s/%s/train_%s.conllu' % (collection_name, experiment_layer, model, str(i)), 'w',
                    encoding='utf-8')
    testset = open('output/%s/%s/%s/test_%s.conllu' % (collection_name, experiment_layer, model, str(i)), 'w',
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


def arguments():
    path_to_model = 'resources/maltparser-1.9.2/maltparser-1.9.2.jar'
    path_to_malt_eval = 'resources/MaltEval-dist/dist-20141005/lib/MaltEval.jar'
    path_to_optimization_file = 'resources/finalOptionsFile.xml'
    feature_model = 'resources/addMergPOSTAGS0I0FORMInput1.xml'
    # TODO change iterations
    udpipe_options = 'iterations=1;embedding_upostag=20;embedding_feats=20;embedding_xpostag=0;embedding_form=50' \
                     ';embedding_form_file=resources/et_edt.skip.forms.50.vectors;embedding_lemma=0;embedding_deprel=20' \
                     ';learning_rate=0.01;learning_rate_final=0.001;l2=0.5;hidden_layer=200;batch_size=10' \
                     ';transition_system=projective;transition_oracle=dynamic;structured_interval=8;use_gold_tags=1'

    return {'udpipe_options': udpipe_options, 'feature_model': feature_model, 'path_to_model': path_to_model,
            'path_to_malt_eval': path_to_malt_eval, 'path_to_optimization_file': path_to_optimization_file}


def train(i: int, model: str, experiment_layer: str, collection_name: str) -> None:
    options = arguments()
    if model == 'malt':
        create_model = 'java -Xmx6g  -jar %s -c model_%s -i output/%s/%s/%s/train_%s.conllu -f %s -F %s  ' % (
            options['path_to_model'], i,
            collection_name, experiment_layer, model, i, options['path_to_optimization_file'], options['feature_model'])
        subprocess.call(create_model, shell=True)
        os.rename('model_%s.mco' % i, 'output/%s/%s/%s/model_%s.mco' % (collection_name, experiment_layer, model, i))

    elif model == 'udpipe':
        create_model = 'udpipe --train output/%s/%s/%s/model_%s.output --tokenizer=none --tagger=none --parser=%s ' \
                       'output/%s/%s/%s/train_%s.conllu' % (
                           collection_name, experiment_layer, model,
                           i, options['udpipe_options'], collection_name, experiment_layer, model, i)
        subprocess.call(create_model, shell=True)
    else:
        raise ValueError('Model must be malt or udpipe.')


def cross_validation(collection_name: str, experiment_layer: str, collection: PgCollection, model: str,
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
        os.mkdir('output/' + collection_name + "/" + experiment_layer + '/malt')

        os.mkdir('output/' + collection_name + "/" + experiment_layer + '/udpipe')
    if experiment_layer not in os.listdir('output/' + collection_name):
        os.mkdir('output/' + collection_name + "/" + experiment_layer)
        os.mkdir('output/' + collection_name + "/" + experiment_layer + '/malt')

        os.mkdir('output/' + collection_name + "/" + experiment_layer + '/udpipe')

    save_splits_to_df(collection_name, splits, model, experiment_layer)
    for i, s in enumerate(splits):
        create_training_data(s=s, collection=collection, experiment_layer=experiment_layer, i=i, model=model,
                             collection_name=collection_name)
        train(i=i, model=model, experiment_layer=experiment_layer, collection_name=collection_name)


if __name__ == '__main__':
    storage = PostgresStorage(pgpass_file='../db_conn.pgpass',
                              password='',
                              schema='syntaxexperiments'
                              )
    try:


        for experiment in GM_EXPERIMENTS:
            #ud = storage['est_ud']
            #cross_validation(collection_name='est_ud', experiment_layer=experiment, collection=ud, model='malt', files=len(ud))
            #cross_validation(collection_name='est_ud', experiment_layer=experiment, collection=storage['est_ud'], model='udpipe', files=11)
            edt = storage['edt']
            cross_validation(collection_name='edt', experiment_layer=experiment, collection=edt, model='malt', files=232)
            # cross_validation(collection_name='edt', experiment_layer=experiment, collection=storage['edt'], model='udpipe',files=11)

        storage.close()
    except:
        storage.close()
