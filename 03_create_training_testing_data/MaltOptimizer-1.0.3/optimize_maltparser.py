import subprocess
import os
"""
Runnable only with python2.7 
"""

EXPERIMENTS = ['gm_experiment_1', 'am_experiment_1', 'gm_experiment_2', 'am_experiment_2', 'gm_experiment_3',
               'am_experiment_3', 'gm_experiment_3_2', 'am_experiment_3_2', 'gm_experiment_4', 'am_experiment_4',
               'gm_experiment_4_2', 'am_experiment_4_2', 'gm_experiment_5', 'am_experiment_5', 'gm_experiment_6',
               'am_experiment_6', 'gm_experiment_6_2', 'am_experiment_6_2', 'gm_experiment_7', 'am_experiment_7',
               'gm_experiment_8', 'am_experiment_8', 'gm_experiment_8_2', 'am_experiment_8_2', 'gm_experiment_9',
               'am_experiment_9', 'gm_experiment_10', 'am_experiment_10', 'gm_experiment_11', 'am_experiment_11',
               'gm_experiment_12', 'am_experiment_12', 'gm_experiment_13', 'am_experiment_13', 'gm_experiment_14',
               'am_experiment_14']
TEST = ['gm_experiment_1', 'gm_experiment_2', 'am_experiment_1', 'am_experiment_2']

def optimize_maltparser(collection_name, experiment_name):
    phase1 = 'java -jar MaltOptimizer.jar -p 1 -m ..\..\\03_train_models\\resources\maltparser-1.9.2\maltparser-1.9.2.jar -c ..\output\%s\%s\malt_opt.conll' % (
    collection_name, experiment_name)
    subprocess.call(phase1, shell=True, cwd='MaltOptimizer-1.0.3')


    phase2 = 'java -jar MaltOptimizer.jar -p 2 -m ..\..\\03_train_models\\resources\maltparser-1.9.2\maltparser-1.9.2.jar -c ..\output\%s\%s\malt_opt.conll' % (
    collection_name, experiment_name)
    subprocess.call(phase2, shell=True, cwd='MaltOptimizer-1.0.3')

    phase3 = 'java -jar MaltOptimizer.jar -p 3 -m ..\..\\03_train_models\\resources\maltparser-1.9.2\maltparser-1.9.2.jar -c ..\output\%s\%s\malt_opt.conll' % (
    collection_name, experiment_name)
    subprocess.call(phase3, shell=True, cwd='MaltOptimizer-1.0.3')

    with open('MaltOptimizer-1.0.3\\phase3_optFile.txt', 'r' ) as f:
        lines = f.read().split('\n')
    feature_model = lines[-1].split(':')[-1]

    # move the files to correct place:
    os.rename('MaltOptimizer-1.0.3\\finalOptionsFile.xml', 'output\%s\%s\\finalOptionsFile.xml' % (collection_name, experiment_name))
    os.rename('MaltOptimizer-1.0.3\\'+ feature_model, 'output\%s\%s\\featureFile.xml') % (collection_name, experiment_name)


if __name__ == '__main__':
    for experiment in TEST:
        optimize_maltparser(experiment_name=experiment, collection_name='edt')
        optimize_maltparser(experiment_name=experiment, collection_name='est_ud')
