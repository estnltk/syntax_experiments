#
#    Applies MaltParser/UDPipe1 models to get predictions.
#    Implemented settings:
#       * full_data
#       * multi_experiment (general)
#       * crossvalidation
#       * half_data
#       * smaller_data
#
import os, os.path
import re
import sys
import shutil
from datetime import datetime
import subprocess
from collections import defaultdict
from decimal import Decimal, getcontext
from random import Random

import conllu
import configparser

# Change to local paths & files, if required
DEFAULT_MALTPARSER_DIR = 'MaltOptimizer-1.0.3'
DEFAULT_MALTPARSER_JAR = 'maltparser-1.9.2.jar'
#DEFAULT_UDPIPE_DIR = 'udpipe-1.2.0-bin\\bin-win64'
DEFAULT_UDPIPE_DIR = 'udpipe-1.2.0-bin/bin-linux64'

def run_models_main( conf_file, subexp=None, dry_run=False ):
    '''
    Runs MaltParser/UDPipe-1 models to get predictions based on 
    the configuration. 
    Settings/parameters of running models will be read from 
    the given `conf_file`. 
    Executes sections in the configuration starting with prefix 
    'predict_malt_' and 'predict_udpipe1_'. 
    
    Optinally, if `subexp` is defined, then predicts only 
    that sub-experiment and skips all other sub-experiments (in 
    crossvalidation, smaller_data and half_data experiments).
    '''
    # Parse configuration file
    config = configparser.ConfigParser()
    if conf_file is None or not os.path.exists(conf_file):
        raise FileNotFoundError("Config file {} does not exist".format(conf_file))
    if len(config.read(conf_file)) != 1:
        raise ValueError("File {} is not accessible or is not in valid INI format".format(conf_file))
    section_found = False
    for section in config.sections():
        if section.startswith('predict_malt_') or section.startswith('predict_udpipe1_'):
            parser = 'maltparser' if section.startswith('predict_malt_') else 'udpipe1'
            section_found = True
            subexp_str = '' if subexp is None else f' ({subexp})'
            print(f'Running {section}{subexp_str} ...')
            experiment_type = config[section].get('experiment_type', 'full_data')
            experiment_type_clean = (experiment_type.strip()).lower()
            if experiment_type_clean not in ['full_data', 'crossvalidation', 'half_data', 'smaller_data', 'multi_experiment']:
                raise ValueError('(!) Unexpected experiment_type value: {!r}'.format(experiment_type))
            if experiment_type_clean == 'full_data':
                # ------------------------------------------
                # 'full_data'
                # ------------------------------------------
                # train_file with path
                if not config.has_option(section, 'train_file'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "train_file" parameter.')
                train_file = config[section]['train_file']
                if not os.path.isfile(train_file):
                    raise FileNotFoundError(f'Error in {conf_file}: invalid "train_file" value {train_file!r} in {section!r}.')
                # test_file with path
                if not config.has_option(section, 'test_file'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "test_file" parameter.')
                test_file = config[section]['test_file']
                if not os.path.isfile(test_file):
                    raise FileNotFoundError(f'Error in {conf_file}: invalid "test_file" value {test_file!r} in {section!r}.')
                # output_dir
                if not config.has_option(section, 'output_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
                output_dir = config[section]['output_dir']
                output_prefix = config[section].get('output_file_prefix', 'predicted_')
                if not output_prefix.endswith('_'):
                    output_prefix += '_'
                # use multiple models as an ensemble
                use_ensemble = config[section].getboolean('use_ensemble', False)
                use_majority_voting = config[section].getboolean('use_majority_voting', False)
                aggregation_algorithm = 'las_coherence' if not use_majority_voting else 'majority_voting'
                scores_seed = config[section].getint('scores_seed', 3)
                # Get model file or files
                model_file = None
                model_files = []
                if use_ensemble:
                    # predict with ensemble: get models_dir
                    if not config.has_option(section, 'models_dir'):
                        raise ValueError(f'Error in {conf_file}: section {section!r} is missing "models_dir" parameter.')
                    models_dir = config[section]['models_dir']
                    if not os.path.isdir(models_dir):
                        raise FileNotFoundError(f'Error in {conf_file}: invalid "models_dir" value {models_dir!r} in {section!r}.')
                    # collect all model files from the directory
                    if parser == 'maltparser':
                        model_file_name_pattern = 'model_(.+).mco'
                    else:
                        model_file_name_pattern = 'model_(.+).udpipe'
                    model_file_name_pattern = re.compile(model_file_name_pattern)
                    for fname in os.listdir(models_dir):
                        if model_file_name_pattern.match(fname):
                            model_files.append( os.path.join(models_dir, fname) )
                    if len(model_files) == 0:
                        raise Exception( f'Error in {conf_file}: section {section!r}: Did not find any model files for '+\
                                          'the ensemble tagger from models_dir={models_dir!r}.' )
                else:
                    # predict with a single model: get model file with path
                    default_model = 'model.mco' if parser == 'maltparser' else 'model.udpipe'
                    model_file = config[section].get('model_file', default_model)
                    if not os.path.isfile(model_file):
                        raise FileNotFoundError(f'Error in {conf_file}: invalid "model_file" value {model_file!r} in {section!r}.')
                # other parameters
                dry_run = config[section].getboolean('dry_run', dry_run)
                # MaltParser options
                maltparser_dir = config[section].get('maltparser_dir', DEFAULT_MALTPARSER_DIR)
                maltparser_jar = config[section].get('maltparser_jar', DEFAULT_MALTPARSER_JAR)
                # UDPipe-1 options
                udpipe_dir = config[section].get('udpipe_dir', DEFAULT_UDPIPE_DIR)
                if not dry_run:
                    if parser == 'maltparser':
                        # Predict on train
                        output_file = f'{output_prefix}train.conllu'
                        if not use_ensemble:
                            predict_maltparser(model_file, train_file, output_file, output_dir, 
                                               maltparser_dir=maltparser_dir,
                                               maltparser_jar=maltparser_jar)
                        else:
                            predict_ensemble(parser, model_files, train_file, output_file, output_dir, 
                                             aggregation_algorithm = aggregation_algorithm, 
                                             random_pick_max_score_seed = scores_seed, 
                                             maltparser_dir=maltparser_dir, 
                                             maltparser_jar=maltparser_jar)
                        # Predict on test
                        output_file = f'{output_prefix}test.conllu'
                        if not use_ensemble:
                            predict_maltparser(model_file, test_file, output_file, output_dir, 
                                               maltparser_dir=maltparser_dir,
                                               maltparser_jar=maltparser_jar)
                        else:
                            predict_ensemble(parser, model_files, test_file, output_file, output_dir, 
                                             aggregation_algorithm = aggregation_algorithm, 
                                             random_pick_max_score_seed = scores_seed, 
                                             maltparser_dir=maltparser_dir, 
                                             maltparser_jar=maltparser_jar)
                    elif parser == 'udpipe1':
                        # Predict on train
                        output_file = f'{output_prefix}train.conllu'
                        if not use_ensemble:
                            predict_udpipe1(model_file, train_file, output_file, output_dir, 
                                            udpipe_dir=udpipe_dir)
                        else:
                            predict_ensemble(parser, model_files, train_file, output_file, output_dir, 
                                             aggregation_algorithm = aggregation_algorithm, 
                                             random_pick_max_score_seed = scores_seed, 
                                             udpipe_dir=udpipe_dir)
                        # Predict on test
                        output_file = f'{output_prefix}test.conllu'
                        if not use_ensemble:
                            predict_udpipe1(model_file, test_file, output_file, output_dir, 
                                            udpipe_dir=udpipe_dir)
                        else:
                            predict_ensemble(parser, model_files, test_file, output_file, output_dir, 
                                             aggregation_algorithm = aggregation_algorithm, 
                                             random_pick_max_score_seed = scores_seed, 
                                             udpipe_dir=udpipe_dir)
                    else:
                        raise Exception(f'Unexpected parser name: {parser!r}')
            elif experiment_type_clean in ['crossvalidation', 'half_data', 'smaller_data', 'multi_experiment']:
                # ------------------------------------------
                # 'multi_experiment' (general)
                # 'crossvalidation'
                # 'half_data'
                # 'smaller_data'
                # ------------------------------------------
                # input_dir
                if not config.has_option(section, 'input_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_dir" parameter.')
                input_dir = config[section]['input_dir']
                if not os.path.isdir(input_dir):
                    raise FileNotFoundError(f'Error in {conf_file}: invalid "input_dir" value {input_dir!r} in {section!r}.')
                # output_dir
                if not config.has_option(section, 'output_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
                output_dir = config[section]['output_dir']
                # models_dir
                if not config.has_option(section, 'models_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "models_dir" parameter.')
                models_dir = config[section]['models_dir']
                if not os.path.isdir(models_dir):
                    raise FileNotFoundError(f'Error in {conf_file}: invalid "models_dir" value {models_dir!r} in {section!r}.')
                models_dir_files = [ fname for fname in os.listdir(models_dir) ]
                if len(models_dir_files) == 0:
                    raise Exception(f'(!) No files found from models_dir {models_dir!r}')
                # test_file with full path, or a pattern for finding test file from input_dir
                if not config.has_option(section, 'test_file'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "test_file" parameter.')
                test_file = config[section]['test_file']
                test_file_is_pattern = config[section].getboolean('test_file_is_pattern', False)
                if not test_file_is_pattern and not os.path.isfile(test_file):
                    raise FileNotFoundError(f'Error in {conf_file}: invalid "test_file" value {test_file!r} in {section!r}.')
                # Common options
                dry_run = config[section].getboolean('dry_run', dry_run)
                output_file_prefix = config[section].get('output_file_prefix', 'predicted_')
                if not output_file_prefix.endswith('_'):
                    output_file_prefix += '_'
                # Train file pattern
                train_file_pat = r'(?P<exp>\d+)_train.conllu'
                train_file_re = None
                if config.has_option(section, 'train_file_pat'):
                    train_file_pat = config[section]['train_file_pat']
                train_file_re = _create_regexp_pattern(train_file_pat, 'train_file_pat')
                # Test file pattern (if provided)
                test_file_re = None
                if test_file_is_pattern:
                    test_file_re = _create_regexp_pattern(test_file, 'test_file')
                # skip_train: do not predict on train files
                skip_train = config[section].getboolean('skip_train', False)
                # test_matrix prediction mode: run all models on all test files
                test_matrix = config[section].getboolean('test_matrix', False) 
                if test_matrix and test_file_re is None:
                    raise ValueError(f'(!) test_matrix can only be used if test file name is a regular expression')
                # MaltParser options
                maltparser_dir = config[section].get('maltparser_dir', DEFAULT_MALTPARSER_DIR)
                maltparser_jar = config[section].get('maltparser_jar', DEFAULT_MALTPARSER_JAR)
                # UDPipe-1 options
                udpipe_dir = config[section].get('udpipe_dir', DEFAULT_UDPIPE_DIR)
                # Collect input data
                # Collect all train files
                all_train_files = {}
                for in_fname in sorted(os.listdir(input_dir)):
                    if in_fname.endswith('.conllu'):
                        m1 = train_file_re.match(in_fname)
                        if m1:
                            train_fpath = os.path.join(input_dir, in_fname)
                            subexp = m1.group('exp')
                            all_train_files[subexp] = train_fpath
                # Collect all test files
                all_test_files = {}
                if test_file_re is not None:
                    # If test_file regex is provided, then collect test files via regexp
                    for in_fname in sorted(os.listdir(input_dir)):
                        if in_fname.endswith('.conllu'):
                            m2 = test_file_re.match(in_fname)
                            if m2:
                                test_file_subexp = m2.group('exp')
                                assert test_file_subexp not in all_test_files.keys(), \
                                    f'Duplicate test files for experiment {test_file_subexp}'
                                all_test_files[test_file_subexp] = \
                                    os.path.join(input_dir, in_fname)
                else:
                    # If test_file regex is missing, assign a single test file for 
                    # all experiments (global testing)
                    for cur_subexp in sorted( all_train_files.keys() ):
                        all_test_files[cur_subexp] = test_file
                # Sanity checks
                if len(all_test_files.keys()) > 0 and len(all_train_files.keys()) > 0:
                    if not (all_train_files.keys() == all_test_files.keys()):
                        raise ValueError('(!) Mismatching train and test sub-experiment '+\
                                         f'names. Train experiments: {all_train_files.keys()!r}; '+\
                                         f'Test experiments: {all_test_files.keys()!r} ')
                elif len(all_test_files.keys()) == 0 and len(all_train_files.keys()) == 0:
                    raise ValueError(f'(!) No train or test files found from {input_dir}')
                #
                # Iterate over input files and predict
                #
                for cur_subexp in sorted( all_test_files.keys() ):
                    cur_test_file = all_test_files[cur_subexp]
                    cur_train_file = all_train_files.get(cur_subexp, None)
                    assert cur_train_file is not None or test_matrix
                    if parser == 'maltparser':
                        model_file = f'model_{cur_subexp}.mco'
                    else:
                        model_file = f'model_{cur_subexp}.udpipe'
                    # Try to find corresponding model from the models subdirectory
                    if model_file not in models_dir_files:
                        raise Exception(f'(!) Could not find model file {model_file!r} for experiment '+\
                                        f'{cur_subexp!r} from {models_dir!r}.')
                    model_path = os.path.join(models_dir, model_file)
                    # Run model for predictions
                    if not dry_run:
                        train_output_file = f'{output_file_prefix}train_{cur_subexp}.conllu'
                        test_output_file  = f'{output_file_prefix}test_{cur_subexp}.conllu'
                        if parser == 'maltparser':
                            # Predict on train data (optional, can be skipped)
                            if cur_train_file is not None and not skip_train:
                                predict_maltparser(model_path, cur_train_file, train_output_file, output_dir, 
                                                   maltparser_dir=maltparser_dir,
                                                   maltparser_jar=maltparser_jar)
                            # Predict on test
                            if not test_matrix:
                                predict_maltparser(model_path, cur_test_file, test_output_file, output_dir, 
                                                   maltparser_dir=maltparser_dir,
                                                   maltparser_jar=maltparser_jar)
                            else:
                                # predict on all test files
                                for test_subexp in sorted(all_test_files.keys()):
                                    test_output_fpath = os.path.join(output_path, \
                                        f'{output_file_prefix}model_{cur_subexp}_test_{test_subexp}.conllu')
                                    cur_test_file = all_test_files[test_subexp]
                                    predict_maltparser(model_path, cur_test_file, test_output_fpath, output_dir, 
                                                       maltparser_dir=maltparser_dir,
                                                       maltparser_jar=maltparser_jar)
                        elif parser == 'udpipe1':
                            # Predict on train data (optional, can be skipped)
                            if cur_train_file is not None and not skip_train:
                                predict_udpipe1(model_path, cur_train_file, train_output_file, output_dir, 
                                                udpipe_dir=udpipe_dir)
                            # Predict on test
                            if not test_matrix:
                                predict_udpipe1(model_path, cur_test_file, test_output_file, output_dir, 
                                                udpipe_dir=udpipe_dir)
                            else:
                                # predict on all test files
                                for test_subexp in sorted(all_test_files.keys()):
                                    test_output_fpath = os.path.join(output_path, \
                                        f'{output_file_prefix}model_{cur_subexp}_test_{test_subexp}.conllu')
                                    cur_test_file = all_test_files[test_subexp]
                                    predict_udpipe1(model_path, cur_test_file, test_output_fpath, output_dir, 
                                                    udpipe_dir=udpipe_dir)
                        else:
                            raise Exception(f'Unexpected parser name: {parser!r}')
    if not section_found:
        print(f'No section starting with "predict_malt_" or "predict_udpipe1_" in {conf_file}.')


def _create_regexp_pattern(fpattern, pattern_var_name):
    # Convert file pattern to regular experssion
    if not isinstance(fpattern, str):
        raise TypeError(f'{pattern_var_name} must be a string')
    regexp = None
    try:
        regexp = re.compile(fpattern)
    except Exception as err:
        raise ValueError(f'Unable to convert {fpattern!r} to regexp') from err
    if 'exp' not in regexp.groupindex:
        raise ValueError(f'Regexp {fpattern!r} is missing named group "exp"')
    return regexp


# ===============================================================
#  Predict MaltParser
# ===============================================================

def check_maltparser_requirements(maltparser_dir=DEFAULT_MALTPARSER_DIR,
                                  maltparser_jar=DEFAULT_MALTPARSER_JAR):
    '''
    Check that MaltParser's required folders and jar files are present.
    Raises an expection if anything is missing.
    '''
    if not os.path.isdir(maltparser_dir):
        raise Exception( ('Missing directory: \%s. Please get MaltParser from: https://maltparser.org/index.html') % (maltparser_dir) )
    malt_dir_files = list(os.listdir(maltparser_dir))
    if maltparser_jar not in malt_dir_files:
        jar_path = os.path.join(maltparser_dir, maltparser_jar)
        raise Exception( ('Missing jar file: \%s. Please get MaltParser from: https://maltparser.org/index.html') % (jar_path) )
    if 'lib' not in malt_dir_files:
        lib_path = os.path.join(maltparser_dir, 'lib')
        raise Exception( ('Missing java libraries dir: \%s. Please get MaltParser from: https://maltparser.org/index.html') % (lib_path) )
    return True

def predict_maltparser(model_path, test_corpus, output_file, output_dir, maltparser_dir=DEFAULT_MALTPARSER_DIR, 
                       maltparser_jar=DEFAULT_MALTPARSER_JAR):
    '''
    Runs MaltParser on given test_corpus to get predictions and saves results as conllu into output_file.
    output_file should be a file name, use output_dir to specify its location.
    '''
    check_maltparser_requirements(maltparser_dir=maltparser_dir, maltparser_jar=maltparser_jar)
    # Make input file paths absolute
    if test_corpus != os.path.abspath(test_corpus):
        test_corpus = os.path.abspath(test_corpus)
    if model_path != os.path.abspath(model_path):
        model_path = os.path.abspath(model_path)
    # Note: Maltparser's model must be at the same directory as maltparser jar,
    # otherwise we'll run into error "Couldn't find the MaltParser configuration 
    # file". Copy the model.
    model_copied = False
    model_dir, model_name = os.path.split(model_path)
    if len(model_dir) > 0 and model_dir not in maltparser_dir:
        shutil.copyfile(model_path, os.path.join(maltparser_dir, model_name))
        model_copied = True
    # Construct command
    predict_command = \
        ('java -jar {jar} -c {model} -i {test_corpus} -o {output_file} -m parse').\
            format(jar=maltparser_jar, model=model_name, test_corpus=test_corpus, output_file=output_file)
    # Execute
    subprocess.call(predict_command, shell=True, cwd=maltparser_dir)
    # Remove copied model
    if model_copied:
        os.remove( os.path.join(maltparser_dir, model_name) )
    # Relocate output
    if output_dir is not None:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        # Remove old file
        if os.path.exists(os.path.join(output_dir, output_file)):
            os.remove(os.path.join(output_dir, output_file))
        # Move predicted file to output dir
        os.rename(os.path.join(maltparser_dir, output_file), 
                  os.path.join(output_dir, output_file))

# ===============================================================
#  Predict UDPipe1
# ===============================================================

def check_if_udpipe_is_in_path(udpipe_cmd='udpipe'):
    ''' Checks whether given udpipe is in system's PATH. Returns True, there is
        a file with given name (udpipe_cmd) in the PATH, otherwise returns False;
        The idea borrows from:  http://stackoverflow.com/a/377028
    '''
    if os.getenv("PATH") == None:
        return False
    for path in os.environ["PATH"].split(os.pathsep):
        path1 = path.strip('"')
        file1 = os.path.join(path1, udpipe_cmd)
        if os.path.isfile(file1) or os.path.isfile(file1 + '.exe'):
            return True
    return False

def predict_udpipe1(model_path, test_corpus, output_file, output_dir, udpipe_dir=DEFAULT_UDPIPE_DIR):
    '''
    Runs UDPipe-1 on given test_corpus to get predictions and saves results as conllu into output_file.
    '''
    udpipe_dir_exists = udpipe_dir is not None and os.path.isdir(udpipe_dir)
    udpipe_is_in_path = check_if_udpipe_is_in_path()
    if not udpipe_dir_exists and not udpipe_is_in_path:
        raise Exception('(!) Could not find UDPipe executable. '+\
                        'Please make sure udpipe is installed and available in system PATH. '+\
                        'Or, alternatively, provide location of UDPipe via variable udpipe_dir. '+\
                        'You can download udpipe from: https://ufal.mff.cuni.cz/udpipe/1/')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    udpipe_cmd = 'udpipe'
    if udpipe_dir_exists:
        udpipe_cmd = os.path.join(udpipe_dir, udpipe_cmd)
    output_path = os.path.join(output_dir, output_file)
    predict_command = \
        ('{udpipe_cmd} --parse {model_path} {test_corpus} --output=conllu --outfile={output_path} ').\
            format(udpipe_cmd=udpipe_cmd, model_path=model_path, test_corpus=test_corpus,
                   output_path=output_path)
    # Execute
    subprocess.call(predict_command, shell=True)

# ===============================================================
#  Predict with MaltParser or UDPipe1 ensemble
# ===============================================================

def predict_ensemble(parser, model_files, test_corpus, output_file, output_dir, aggregation_algorithm = 'las_coherence', 
                                                                                random_pick_max_score_seed = 3,
                                                                                udpipe_dir=DEFAULT_UDPIPE_DIR, 
                                                                                maltparser_dir=DEFAULT_MALTPARSER_DIR, 
                                                                                maltparser_jar=DEFAULT_MALTPARSER_JAR):
    '''
    Runs an ensemble of MaltParser or UDPipe1 models on given test_corpus to get predictions and saves 
    results as conllu into output_file.
    output_file should be a file name, use output_dir to specify its location.
    '''
    assert parser in ['maltparser', 'udpipe1']
    assert aggregation_algorithm in ['las_coherence', 'majority_voting']
    # 1) Collect predictions from all of the models
    temp_prediction_files = []
    for model_id, model_file in enumerate(model_files):
        if parser == 'maltparser':
            # Predict on train
            temp_output_file = f'temp_malt_predict_{model_id}.conllu'
            predict_maltparser(model_file, test_corpus, temp_output_file, output_dir, 
                               maltparser_dir=maltparser_dir,
                               maltparser_jar=maltparser_jar)
        elif parser == 'udpipe1':
            # Predict on train
            temp_output_file = f'temp_udpipe_predict_{model_id}.conllu'
            predict_udpipe1(model_file, test_corpus, temp_output_file, output_dir, 
                            udpipe_dir=udpipe_dir)
        output_fpath = os.path.join(output_dir, temp_output_file)
        temp_prediction_files.append( output_fpath )
    # 2) Load corresponding predicted conllu contents
    predicted_docs = []
    for temp_output_file in temp_prediction_files:
        assert os.path.exists(temp_output_file), \
            f'(!) Missing {parser} output file {temp_output_file!r}.'
        with open(temp_output_file, 'r', encoding='utf-8') as conllu_file:
            predicted_docs.append( conllu.parse(conllu_file.read()) )
    # 2.x) Validate that all docs have equal number of sentences
    number_of_sentences = 0
    for i in range(0, len(predicted_docs), 2):
        if i+1 < len( predicted_docs ):
            doc1_file = temp_prediction_files[i]
            doc2_file = temp_prediction_files[i+1]
            doc1 = predicted_docs[i]
            doc2 = predicted_docs[i+1]
            if len(doc1) != len(doc2):
                raise ValueError( f'(!) Number of sentences differ in predicted output files: '+\
                                  f' {doc1_file}: {len(doc1)} vs {doc2_file}: {len(doc2)}.' )
            number_of_sentences = len(doc1)
    # Random generator for choosing one dependency label if there are multiple labes with maximum scores
    random_shuffler = Random()
    random_shuffler.seed(random_pick_max_score_seed)
    # 3) Iterate over all sentences and get aggregate predictions of each sentence
    output_doc = []
    for sent_id in range(number_of_sentences):
        all_sent_predictions = []
        for doc in predicted_docs:
            all_sent_predictions.append(doc[sent_id])
        if aggregation_algorithm == 'las_coherence':
            # Find pairwise las scores for all sentences
            lases_table = defaultdict(dict)
            for model_a, sent_a in enumerate( all_sent_predictions ):
                for model_b, sent_b in enumerate( all_sent_predictions ):
                    lases_table[model_a][model_b] = sentence_LAS(sent_a, sent_b)
            # Find average LAS for each model
            sent_scores = dict()
            getcontext().prec = 4
            for base_model, score in lases_table.items():
                decimals = list(map(Decimal, score.values()))
                avg_score = sum(decimals) / Decimal(len(all_sent_predictions))
                sent_scores[base_model] = avg_score
            # Pick sentence with the highest avg LAS (the highest coherence)
            max_score = max(sent_scores.values())
            max_score_count = 0
            max_score_models = []
            for model, score in sent_scores.items():
                if score == max_score:
                    max_score_count += 1
                    max_score_models.append(model)
            random_shuffler.shuffle( max_score_models )
            output_doc.append ( all_sent_predictions[ max_score_models[0] ] )
        elif aggregation_algorithm == 'majority_voting':
            sentence_length = len(all_sent_predictions[0])
            extracted_words = []
            # Get deprel with maximal votes for each token
            for token_id in range(sentence_length):
                voting_table = defaultdict(int)
                label_token_map = {}
                for sentence in all_sent_predictions:
                    token = sentence[token_id]
                    label = '{}__{}'.format(token['deprel'], token['head'])
                    voting_table[label] += 1
                    if label not in label_token_map.keys():
                        label_token_map[label] = []
                    label_token_map[label].append(token)
                # Find maximum voting score and corresponding tokens
                max_votes = max( voting_table.values() )
                max_votes_labels = [l for l, v in voting_table.items() if v==max_votes]
                max_votes_tokens = []
                for label, tokens in label_token_map.items():
                    if label in max_votes_labels:
                        max_votes_tokens.extend(tokens)
                # In case of a tie, pick a token randomly
                random_shuffler.shuffle(max_votes_tokens)
                extracted_words.append(max_votes_tokens[0])
            assert len(extracted_words) == sentence_length
            # Construct new sentence
            new_sentence = all_sent_predictions[0].copy()
            for token_id in range(sentence_length):
                new_sentence[token_id] = extracted_words[token_id].copy()
            output_doc.append( new_sentence )
    assert len(output_doc) == number_of_sentences
    # 4) Output picked sentences
    final_output_fpath = os.path.join(output_dir, output_file)
    with open(final_output_fpath, 'w', encoding='utf-8') as out_f:
        for sentence in output_doc:
            out_f.write( sentence.serialize() )
    # 5) Finally, remove conllu files with temporary predictions
    for temp_file in temp_prediction_files:
        os.remove(temp_file)


def sentence_LAS(sent1, sent2):
    '''Calculates LAS between two conllu sentences.'''
    wrong = 0
    correct = 0
    for tok1, tok2 in zip(sent1, sent2):
        if tok1['xpos'] != 'Z':
            if tok1['head'] == tok2['head'] and tok1['deprel'] == tok2['deprel']:
                correct += 1
            else:
                wrong += 1
    if wrong == 0 and correct == 0:
        return 1
    else:
        return correct / (correct + wrong)

# ========================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    conf_file = sys.argv[1]
    subexp = None
    if len(sys.argv) > 2:
        subexp = sys.argv[2]
    run_models_main( conf_file, subexp=subexp )
