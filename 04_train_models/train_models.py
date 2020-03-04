import os
import subprocess

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

READY = ['gm_experiment_1']


def arguments(experiment_layer, collection_name):
    path_to_model = 'resources/maltparser-1.9.2/maltparser-1.9.2.jar'
    path_to_malt_eval = 'resources/MaltEval-dist/dist-20141005/lib/MaltEval.jar'
    path_to_optimization_file = '../03_create_training_testing_data/output/%s/%s/finalOptionsFile.xml' % (
    collection_name,experiment_layer)
    feature_model = '../03_create_training_testing_data/output/%s/%s/featureModel.xml' % (
    collection_name,experiment_layer)
    udpipe_options = 'iterations=30;embedding_upostag=20;embedding_feats=20;embedding_xpostag=0;embedding_form=50' \
                     ';embedding_form_file=resources/et_edt.skip.forms.50.vectors;embedding_lemma=0;embedding_deprel=20' \
                     ';learning_rate=0.01;learning_rate_final=0.001;l2=0.5;hidden_layer=200;batch_size=10' \
                     ';transition_system=projective;transition_oracle=dynamic;structured_interval=8;use_gold_tags=1'

    return {'udpipe_options': udpipe_options, 'feature_model': feature_model, 'path_to_model': path_to_model,
            'path_to_malt_eval': path_to_malt_eval, 'path_to_optimization_file': path_to_optimization_file}


def train(i: int, model: str, experiment_layer: str, collection_name: str) -> None:
    options = arguments(experiment_layer, collection_name)
    if model == 'malt':
        create_model = 'java -Xmx6g  -jar %s -c model_%s -i ../03_create_training_testing_data/output/%s/%s/train_%s.conllu -f %s -F  %s' % (
            options['path_to_model'], i,
            collection_name, experiment_layer, i, options['path_to_optimization_file'], options['feature_model'])
        subprocess.call(create_model, shell=True)
        os.rename('model_%s.mco' % i, 'output/%s/%s/%s/model_%s.mco' % (collection_name, experiment_layer, model, i))

    elif model == 'udpipe':
        create_model = 'udpipe --train output/%s/%s/%s/model_%s.output --tokenizer=none --tagger=none --parser=%s ' \
                       'output/%s/%s/train_%s.conllu' % (
                           collection_name, experiment_layer,
                           i, options['udpipe_options'], collection_name, experiment_layer, model, i)
        subprocess.call(create_model, shell=True)
    else:
        raise ValueError('Model must be malt or udpipe.')


def cross_validation(collection_name: str, experiment_layer: str, model: str, ) -> None:
    """
    :param experiment_name
    :param experiment_layer:
    :param model:
    :return:
    """

    for i in range(10):
        train(i=i, model=model, experiment_layer=experiment_layer, collection_name=collection_name)


if __name__ == '__main__':

    for experiment in READY:
        if experiment not in os.listdir('output/edt/'):
            os.mkdir('output/edt/' + experiment)
        if experiment not in os.listdir('output/est_ud'):
            os.mkdir('output/est_ud/' + experiment)

        # cross_validation(collection_name='est_ud', experiment_layer=experiment, collection=ud, model='malt', files=len(ud))
        # cross_validation(collection_name='est_ud', experiment_layer=experiment, collection=storage['est_ud'], model='udpipe', files=11)
        if 'malt' not in os.listdir('output/edt/%s/' % experiment):
            os.mkdir('output/edt/%s/malt' % experiment)
        if 'malt' not in os.listdir('output/est_ud/%s/' % experiment):
            os.mkdir('output/est_ud/%s/malt'%experiment)
        cross_validation(collection_name='edt', experiment_layer=experiment, model='malt')

#        cross_validation(collection_name='est_ud', experiment_layer=experiment, model='malt')
        #cross_validation(collection_name='edt', experiment_layer=experiment, model='udpipe')
