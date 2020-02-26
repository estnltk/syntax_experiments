import subprocess

EXPERIMENTS = ['gm_experiment_1', 'am_experiment_1', 'gm_experiment_2', 'am_experiment_2', 'gm_experiment_3',
               'am_experiment_3', 'gm_experiment_3_2', 'am_experiment_3_2', 'gm_experiment_4', 'am_experiment_4',
               'gm_experiment_4_2', 'am_experiment_4_2', 'gm_experiment_5', 'am_experiment_5', 'gm_experiment_6',
               'am_experiment_6', 'gm_experiment_6_2', 'am_experiment_6_2', 'gm_experiment_7', 'am_experiment_7',
               'gm_experiment_8', 'am_experiment_8', 'gm_experiment_8_2', 'am_experiment_8_2', 'gm_experiment_9',
               'am_experiment_9', 'gm_experiment_10', 'am_experiment_10', 'gm_experiment_11', 'am_experiment_11',
               'gm_experiment_12', 'am_experiment_12', 'gm_experiment_13', 'am_experiment_13', 'gm_experiment_14',
               'am_experiment_14']
READY = ['gm_experiment_1', 'gm_experiment_2']

def predict(model: str, experiment_layer: str, collection_name: str, i: int) -> None:
    if model == 'malt':
        predict_maltparser(experiment_layer=experiment_layer, model=model, collection_name=collection_name, i=i)
    elif model == 'udpipe':
        predict_udpipe(experiment_layer=experiment_layer, model=model, collection_name=collection_name, i=i)


def predict_udpipe(experiment_layer: str, model: str, collection_name: str, i: int) -> None:
    parse_test = 'udpipe --parse ../03_train_models/output/%s/%s/%s/model_%s.output ' \
                 '../03_train_models/output/%s/%s/%s/test_%s.conllu > ' \
                 '../03_train_models/output/%s/%s/%s/parsed_test_%s.conllu 	 ' % (
                     collection_name, experiment_layer, model, i, collection_name, experiment_layer, model, i,
                     collection_name, experiment_layer,
                     model, i)
    parse_train = 'udpipe --parse ../03_train_models/output/%s/%s/%s/model_%s.output ' \
                  '../03_train_models/output/%s/%s/%s/train_%s.conllu > ' \
                  '../03_train_models/output/%s/%s/%s/parsed_train_%s.conllu ' % (
                      collection_name, experiment_layer, model, i, collection_name, experiment_layer, model, i,
                      collection_name, experiment_layer, model, i)
    subprocess.call(parse_test, shell=True)
    subprocess.call(parse_train, shell=True)


def predict_maltparser(experiment_layer: str, model: str, collection_name: str, i: int) -> None:
    options = arguments()
    parse_test = 'java  -jar %s -c model_%s -i test_%s.conllu ' \
                 '-o parsed_test_%s.conllu -m parse ' % (
                     options["path_to_model"], i,
                     i, i)
    parse_train = 'java  -jar %s -c model_%s -i train_%s.conllu ' \
                  '-o parsed_train_%s.conllu -m parse' % (
                      options['path_to_model'], i, i, i)

    subprocess.call(parse_test, shell=True,
                    cwd='../03_train_models/output/%s/%s/%s/' % (collection_name, experiment_layer, model))
    subprocess.call(parse_train, shell=True,
                    cwd='../03_train_models/output/%s/%s/%s/' % (collection_name, experiment_layer, model))


def arguments():
    path_to_model = '../../../../resources/maltparser-1.9.2/maltparser-1.9.2.jar'
    return {'path_to_model': path_to_model}


if __name__ == '__main__':
    for experiment in READY:
        for i in range(10):
            #predict('malt', experiment, 'edt', i)
            #predict('udpipe', experiment, 'edt', i)

            predict('malt', experiment, 'est_ud', i)
            #predict('udpipe', experiment, 'est_ud', i)
