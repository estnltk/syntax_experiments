import re

from pandas import DataFrame

EXPERIMENTS = ['gm_experiment_1']


def write_all_results(experiment: str, model: str, collection: str):
    results_df = DataFrame(data=None, columns=['File', 'LA', 'UAS', 'LAS'])
    for i in range(10):
        i = str(i)
        with open('../04_train_models/output/%s/%s/%s/result_train_%s.txt' % (collection, experiment, model, i)) as f:
            split_result_train = f.read().split('\n')
        with open('../04_train_models/output/%s/%s/%s/result_test_%s.txt' % (collection, experiment, model, i)) as f:
            split_result_test = f.read().split('\n')

        result_train = re.sub(r' +', ' ', split_result_train[11]).split(' ')
        LA_train = result_train[0].strip()
        UAS_train = result_train[1].strip()
        LAS_train = result_train[2].strip()

        result_test = re.sub(r' +', ' ', split_result_test[11]).split(' ')
        LA_test = result_test[0].strip()
        UAS_test = result_test[1].strip()
        LAS_test = result_test[2].strip()

        results_df = results_df.append(
            {'File': 'train_%s' % i, 'LA': LA_train,
             'UAS': UAS_train, 'LAS': LAS_train}, ignore_index=True)
        results_df = results_df.append(
            {'File': 'test_%s' % i, 'LA': LA_test,
             'UAS': UAS_test, 'LAS': LAS_test}, ignore_index=True)

    results_df.to_csv(experiment + '_malt_%s.csv' % collection)


if __name__ == '__main__':
    for experiment in EXPERIMENTS:
        # write_all_results(experiment=experiment, model='malt', collection='edt')
        write_all_results(experiment=experiment, model='malt', collection='est_ud')
