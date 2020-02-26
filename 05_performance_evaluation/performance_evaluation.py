import subprocess

EXPERIMENTS = ['gm_experiment_1', 'am_experiment_1', 'gm_experiment_2', 'am_experiment_2', 'gm_experiment_3',
               'am_experiment_3', 'gm_experiment_3_2', 'am_experiment_3_2', 'gm_experiment_4', 'am_experiment_4',
               'gm_experiment_4_2', 'am_experiment_4_2', 'gm_experiment_5', 'am_experiment_5', 'gm_experiment_6',
               'am_experiment_6', 'gm_experiment_6_2', 'am_experiment_6_2', 'gm_experiment_7', 'am_experiment_7',
               'gm_experiment_8', 'am_experiment_8', 'gm_experiment_8_2', 'am_experiment_8_2', 'gm_experiment_9',
               'am_experiment_9', 'gm_experiment_10', 'am_experiment_10', 'gm_experiment_11', 'am_experiment_11',
               'gm_experiment_12', 'am_experiment_12', 'gm_experiment_13', 'am_experiment_13', 'gm_experiment_14',
               'am_experiment_14']

DONE = ['gm_experiment_1', 'gm_experiment_2']


def evaluate_model(experiment_layer: str, model: str, collection_name: str, i: int) -> None:
    """
    Ealuates malt and udpipe models
    :param experiment_layer: Experiment
    :param model: udpipe or malt
    :param i: split number
    :return: None
    """
    if model == 'malt':
        evaluate_test = 'java -jar ../03_train_models/resources/MaltEval-dist/dist-20141005/lib/MaltEval.jar -s ' \
                        '../03_train_models/output/%s/%s/%s/parsed_test_%s.conllu -g ' \
                        '../03_train_models/output/%s/%s/%s/test_%s.conllu ' \
                        '--Metric ' \
                        'LAS;UAS;LA > ../03_train_models/output/%s/%s/%s/output_test_%s.txt' % (
                            collection_name, experiment_layer, model, i, collection_name, experiment_layer, model, i,
                            collection_name, experiment_layer, model, i)
        evaluate_train = 'java -jar ../03_train_models/resources/MaltEval-dist/dist-20141005/lib/MaltEval.jar -s ' \
                         '../03_train_models/output/%s/%s/%s/parsed_train_%s.conllu -g ' \
                         '../03_train_models/output/%s/%s/%s/train_%s.conllu ' \
                         '--Metric ' \
                         'LAS;UAS;LA > ../03_train_models/output/%s/%s/%s/output_train_%s.txt' % (
                             collection_name, experiment_layer, model, i, collection_name, experiment_layer, model, i,
                             collection_name, experiment_layer, model, i)
    elif model == 'udpipe':
        evaluate_test = 'udpipe --accuracy --parse ../03_train_models/output/%s/%s/%s/model_%s.output ' \
                        '../03_train_models/output/%s/%s/%s/test_%s.conllu > ' \
                        '../03_train_models/output/%s/%s/%s/output_test_%s.txt' % (
                            collection_name,experiment_layer, model, i, collection_name,experiment_layer , model, i,
                            collection_name, experiment_layer, model, i)
        evaluate_train = 'udpipe --accuracy --parse ../03_train_models/output/%s/%s/%s/model_%s.output ' \
                         '../03_train_models/output/%s/%s/%s/train_%s.conllu > ' \
                         '../03_train_models/output/%s/%s/%s/output_train_%s.txt' % (
                             collection_name,experiment_layer,  model, i,collection_name, experiment_layer, model, i,
                             collection_name,experiment_layer, model, i)
    else:
        raise ValueError('Model must be malt or udpipe.')

    subprocess.call(evaluate_test, shell=True)
    subprocess.call(evaluate_train, shell=True)


if __name__ == '__main__':
    for i in range(10):
        for experiment in DONE:
            evaluate_model(experiment_layer=experiment, model='malt', collection_name='est_ud', i=i)
            #evaluate_model(experiment_layer=experiment, model='udpipe', collection_name='est_ud', i=i)

            #evaluate_model(experiment_layer=experiment, model='malt', collection_name='edt', i=i)
            #evaluate_model(experiment_layer=experiment, model='udpipe', collection_name='edt', i=i)
