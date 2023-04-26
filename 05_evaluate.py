#
#    Looks through all experiment configurations, and 
#    performs evaluations described in configuration 
#    files: compares predicted files to gold standard 
#    files and finds LAS/UAS scores or different types
#    of parsing errors (E1, E2, E3).
#
#    Supported settings:
#       * full_data
#       * multi_experiment (general)
#       * crossvalidation
#       * half_data
#       * smaller_data
#
#    Requires EstNLTK version 1.7.2+.
#

import sys
import csv, re
import os, os.path
from statistics import mean
import configparser
import warnings

import conllu

from estnltk.converters.conll.conll_importer import conll_to_text
from estnltk.converters.conll.conll_importer import add_layer_from_conll


def eval_main(conf_file, collected_results=None, ignore_missing=True, verbose=True, round=True, count_words=False):
    '''
    Performs evaluations described in given conf_file. Executes sections starting with prefix 
    'eval_'. If `ignore_missing` is set, then skips evaluation sections where input files (gold 
    standard or prediction files) are missing. 

    Evaluation results (train and test LAS/UAS scores, and gaps between train and test LAS) 
    will be saved into dictionary collected_results. 
    Use parameter collected_results to overwrite the dictionary with your own (in order to 
    collect evaluation results over multiple configuration files). If parameter is None, a 
    new dictionary will be created. 
    
    A special case: if the evaluation counts different types of parsing errors (the 
    configuration setting count_error_types=True), then the configuration must provide 
    output_csv_file and results will be saved right away into the given csv file; 
    in this case, nothing will be added to collected_results.

    Returns collected_results. 

    :param conf_file: configuration (INI) file defining evaluations
    :param collected_results: dictionary where to save evaluation results
    :param ignore_missing: if True, then missing evaluation files will be ignored. 
           Otherwise, an exception will be raised in case of a missing file.
    :param verbose: if True, then scores will be output to screen immediately after calculation.
    :param round: if True, then rounds scores to 4 decimals; otherwise collects unrounded scores.
    :param count_words: if True, then reports evaluation word counts (under keys 'train_words' 
           and 'test_words'). Note that evaluation excludes punctuation and null nodes from 
           scoring.
    '''
    if collected_results is None:
        collected_results = dict()
    config = configparser.ConfigParser()
    if len(config.read(conf_file)) != 1:
        raise ValueError("File {} is not accessible or is not in valid INI format".format(conf_file))
    for section in config.sections():
        # look for 'eval_' sections
        if section.startswith('eval_'):
            conf_path, conf_fname = os.path.split(conf_file)
            print(f'{conf_fname}: Checking {section} ...')
            experiment_type = config[section].get('experiment_type', 'full_data')
            experiment_type_clean = (experiment_type.strip()).lower()
            if experiment_type_clean not in ['full_data', 'crossvalidation', 'half_data', 'smaller_data', 'multi_experiment']:
                raise ValueError('(!) Unexpected experiment_type value: {!r}'.format(experiment_type))
            intermediate_results = []
            output_csv_file = None
            test_matrix = False
            if experiment_type_clean == 'full_data':
                # --------------------------------------------------------------
                # 'full_data'
                # --------------------------------------------------------------
                # ==============================================================
                #  Full-data experiment evaluation modes:
                #
                #  Default mode:
                #  * eval on train file, compute LAS and UAS (if not skip_train)
                #  * eval on test file, compute LAS and UAS
                #
                #  Error types mode:
                #  * eval on train file, count different types of errors (if not 
                #    skip_train)
                #  * eval on test file, count different types of errors
                # ==============================================================
                # gold_test and predicted_test with paths
                if not config.has_option(section, 'gold_test'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "gold_test" parameter.')
                gold_test = config[section]['gold_test']
                gold_test_exists = os.path.exists(gold_test)
                if not config.has_option(section, 'predicted_test'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "predicted_test" parameter.')
                predicted_test = config[section]['predicted_test']
                predicted_test_exists = os.path.exists(predicted_test)
                # skip_train: do not evaluate on train files
                skip_train = config[section].getboolean('skip_train', False)
                # gold_train and predicted_train with paths
                if skip_train:
                    # ignore train files. empty values as placeholders
                    gold_train = ''; gold_train_exists=True
                    predicted_train = ''; predicted_train_exists=True
                else:
                    # validate that train files have been provided
                    if not config.has_option(section, 'gold_train'):
                        raise ValueError(f'Error in {conf_file}: section {section!r} is missing "gold_train" parameter.')
                    gold_train = config[section]['gold_train']
                    gold_train_exists = os.path.exists(gold_train)
                    if not config.has_option(section, 'predicted_train'):
                        raise ValueError(f'Error in {conf_file}: section {section!r} is missing "predicted_train" parameter.')
                    predicted_train = config[section]['predicted_train']
                    predicted_train_exists = os.path.exists(predicted_train)
                # other parameters
                error_types_mode = config[section].getboolean('count_error_types', False)
                param_count_words = config[section].getboolean('count_words', count_words)
                experiment_name = config[section].get('name', section)
                exclude_punct = config[section].getboolean('exclude_punct', False)
                punct_tokens_file = config[section].get('punct_tokens_file', None)
                punct_tokens_set = load_punct_tokens( punct_tokens_file )  # Attempt to load from file. If None, return empty set
                output_csv_file = config[section].get('output_csv_file', None) # Output results to csv file right after evaluation
                if output_csv_file is None and error_types_mode:
                    raise ValueError(f'Error in {conf_file} section {section!r}: '+\
                                     f'count_error_types requires setting "output_csv_file" parameter.')
                # Sanity check to avoid accidental confusion with 'multi_experiment'
                if config.has_option(section, 'test_matrix') and config[section].getboolean('test_matrix', False):
                    raise ValueError(f'Error in {conf_file}, section {section!r}: '+\
                                     f'test_matrix option works only with experiment_type = multi_experiment.')
                all_files_exist = gold_train_exists and gold_test_exists and \
                                  predicted_train_exists and predicted_test_exists
                if all_files_exist:
                    format_string = ':.4f' if round else None
                    if not error_types_mode:
                        #
                        # Default eval mode (calculate LAS and UAS)
                        #
                        results = score_experiment( predicted_test, gold_test, predicted_train, gold_train, 
                                                    gold_path=None, predicted_path=None, format_string=format_string,
                                                    count_words=param_count_words, skip_train=skip_train, 
                                                    exclude_punct=exclude_punct, punct_tokens_set=punct_tokens_set )
                        if verbose:
                            print(results)
                        # find experiment directory closest to root in experiment path
                        exp_root = get_experiment_path_root(gold_test)
                        if exp_root not in collected_results.keys():
                            collected_results[exp_root] = dict()
                        collected_results[exp_root][experiment_name] = results
                        intermediate_results.append( (experiment_name, None, None, results) )
                    else:
                        #
                        # Error types eval mode (count E1, E2, E3)
                        #
                        exp_name_raw = experiment_name if experiment_name.endswith('_') else experiment_name+'_'
                        if not skip_train:
                            train_errors = calculate_errors(gold_train, predicted_train, punct_tokens_set=punct_tokens_set, 
                                                            remove_empty_nodes=True, add_counts=param_count_words, 
                                                            format_string=format_string)
                            if verbose:
                                print(f'{exp_name_raw}on_train |', train_errors)
                            intermediate_results.append( (f'{exp_name_raw}on_train', None, None, train_errors) )
                        test_errors = calculate_errors(gold_test, predicted_test, punct_tokens_set=punct_tokens_set, 
                                                       remove_empty_nodes=True, add_counts=param_count_words, 
                                                       format_string=format_string)
                        if verbose:
                            print(f'{exp_name_raw}on_test |', test_errors)
                        intermediate_results.append( (f'{exp_name_raw}on_test', None, None, test_errors) )
                else:
                    missing_files = [f for f in [predicted_test, gold_test, predicted_train, gold_train] if not os.path.exists(f)]
                    if ignore_missing:
                        print(f'Skipping evaluation because of missing files: {missing_files!r}')
                    else:
                        raise FileNotFoundError(f'(!) Cannot evaluate, missing evaluation files: {missing_files!r}')
            elif experiment_type_clean in ['crossvalidation', 'half_data', 'smaller_data', 'multi_experiment']:
                # --------------------------------------------------------------
                # 'multi_experiment' (general)
                # 'crossvalidation'
                # 'half_data'
                # 'smaller_data'
                # --------------------------------------------------------------
                # ==============================================================
                #  Multi-experiment evaluation modes (LAS, UAS):
                #
                #  Default mode:
                #  * eval each model on its train file (if not skip_train)
                #  * eval each model on its test file or on the global test file
                #
                #  Test matrix mode:
                #  * eval each model on its train file (if not skip_train)
                #  * eval each model on all test files
                # ==============================================================
                # gold_test and gold_splits_dir
                if not config.has_option(section, 'gold_test'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "gold_test" parameter.')
                gold_test = config[section]['gold_test']
                test_file_is_pattern = config[section].getboolean('test_file_is_pattern', False)
                if not config.has_option(section, 'gold_splits_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "gold_splits_dir" parameter.')
                gold_splits_dir = config[section]['gold_splits_dir']
                if not config.has_option(section, 'predictions_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "predictions_dir" parameter.')
                # Sanity check to avoid accidental confusion with 'full_data' experiments
                error_types_mode = config[section].getboolean('count_error_types', False)
                if error_types_mode:
                    raise NotImplementedError(f'Error in {conf_file}, section {section!r}: '+\
                                              f'count_error_types is not implemented for {experiment_type} evaluation.')
                predictions_dir = config[section]['predictions_dir']
                predictions_prefix = config[section].get('predictions_prefix', 'predicted_')
                macro_average = config[section].getboolean('macro_average', False)
                param_count_words = config[section].getboolean('count_words', count_words)
                experiment_name_prefix = config[section].get('name_prefix', section)
                if not experiment_name_prefix.endswith('_'):
                    experiment_name_prefix = experiment_name_prefix + '_'
                exclude_punct = config[section].getboolean('exclude_punct', False)
                punct_tokens_file = config[section].get('punct_tokens_file', None)
                punct_tokens_set = load_punct_tokens( punct_tokens_file ) # Attempt to load from file. If None, return empty set
                output_csv_file = config[section].get('output_csv_file', None) # Output results to csv file right after evaluation
                # Patterns for capturing names of training sub-experiment files
                train_file_pat = r'(?P<exp>\d+)_train_all.conllu'
                # Override sub-experiment patterns (if required)
                if config.has_option(section, 'train_file_pat'):
                    train_file_pat = config[section]['train_file_pat']
                # Convert train_file_pattern to regular experssion
                train_file_regex = None
                if not isinstance(train_file_pat, str):
                    raise TypeError('train_file_pat must be a string')
                try:
                    train_file_regex = re.compile(train_file_pat)
                except Exception as err:
                    raise ValueError(f'Unable to convert {train_file_pat!r} to regexp') from err
                if 'exp' not in train_file_regex.groupindex:
                    raise ValueError(f'Regexp {train_file_pat!r} is missing named group "exp"')
                # skip_train: do not evaluate on train files
                skip_train = config[section].getboolean('skip_train', False)
                test_file_regex = None
                if test_file_is_pattern:
                    if not isinstance(gold_test, str):
                        raise TypeError('gold_test must be a string')
                    try:
                        test_file_regex = re.compile(gold_test)
                    except Exception as err:
                        raise ValueError(f'Unable to convert {gold_test!r} to regexp') from err
                    if 'exp' not in test_file_regex.groupindex:
                        raise ValueError(f'Regexp {gold_test!r} is missing named group "exp"')
                # test_matrix evaluation mode: evaluate all models on all test files
                test_matrix = config[section].getboolean('test_matrix', False)
                if macro_average and test_matrix:
                    raise Exception('macro_average not implemented for test_matrix evaluation mode')
                # Validate main paths
                # Find out missing paths
                paths_to_check = [predictions_dir, gold_splits_dir]
                if not test_file_is_pattern:
                    paths_to_check.append(gold_test)
                missing_paths = []
                for input_path in paths_to_check:
                    if not os.path.exists(input_path):
                        missing_paths.append(input_path)
                if missing_paths:
                    # ==================================================
                    #  Report missing main paths
                    # ==================================================
                    if ignore_missing:
                        print(f'Skipping evaluation because of missing dirs/files: {missing_paths!r}')
                    else:
                        raise FileNotFoundError(f'(!) Cannot evaluate, missing evaluation dirs/files: {missing_paths!r}')
                else:
                    # ==================================================
                    #  Main paths are OK. Proceed with gathering files
                    # ==================================================
                    # Try to collect evaluation files
                    # Gold train files
                    all_gold_train_files = {}
                    for gold_file in sorted( os.listdir(gold_splits_dir) ):
                        if (gold_file.lower()).endswith('.conllu'):
                            m = train_file_regex.match(gold_file)
                            if m:
                                no = m.group('exp')
                                all_gold_train_files[no] = \
                                    os.path.join(gold_splits_dir, gold_file)
                    # Gold test files
                    all_gold_test_files = {}
                    if test_file_regex is not None:
                        # Multiple test files
                        for gold_file in sorted(os.listdir(gold_splits_dir)):
                            if (gold_file.lower()).endswith('.conllu'):
                                m2 = test_file_regex.match(gold_file)
                                if m2:
                                    no2 = m2.group('exp')
                                    all_gold_test_files[no2] = \
                                        os.path.join(gold_splits_dir, gold_file)
                    else:
                        # Single test file for all models
                        for cur_subexp in sorted( all_gold_train_files.keys() ):
                            all_gold_test_files[cur_subexp] = gold_test
                        # Exception if no gold train/test files are available
                        if len(all_gold_train_files.keys()) == 0:
                            raise Exception('(!) Unable to construct sub experiment names, '+\
                                            f'because no train files were found from {gold_splits_dir}. '+\
                                            f'Please check that {train_file_pat!r} is a proper regexp for '+\
                                            'recognizing train files from the directory.')
                    # Some sanity checks
                    if len(all_gold_train_files.keys()) > 0 or len(all_gold_test_files.keys()) > 0:
                        if not skip_train:
                            # Train and test set names must match
                            if not (all_gold_train_files.keys() == all_gold_test_files.keys()):
                                raise ValueError('(!) Mismatching train and test sub-experiment '+\
                                                 'names in gold_splits_dir. Missing any files? '+\
                                                 f'Train experiments: {list(all_gold_train_files.keys())!r}; '+\
                                                 f'Test experiments: {list(all_gold_test_files.keys())!r} ')
                        else:
                            if not len(all_gold_test_files.keys()) > 0:
                                raise ValueError(f'(!) No test files found from {gold_splits_dir}')
                    elif len(all_gold_train_files.keys()) == 0 and len(all_gold_test_files.keys()) == 0:
                        raise ValueError(f'(!) No train or test files found from {gold_splits_dir}')
                    # ==================================================
                    #  Iterate over sub experiments and evaluate
                    # ==================================================
                    evaluations_done = 0
                    results_macro_avg = dict()
                    for cur_subexp in sorted( all_gold_test_files.keys() ):
                        current_gold_test = all_gold_test_files[cur_subexp]
                        gold_train = all_gold_train_files.get(cur_subexp, None)
                        assert gold_train is not None or test_matrix
                        missing_prediction_files = []
                        # Find corresponding train prediction
                        target_predicted_train = f'{predictions_prefix}train_{cur_subexp}.conllu'
                        predicted_train = os.path.join(predictions_dir, target_predicted_train)
                        # Find corresponding test predictions
                        if test_matrix:
                            # Multiple test predictions (1 from each model)
                            predicted_test_files  = []
                            predicted_test_models = []
                            for model_subexp in sorted(all_gold_test_files.keys()):
                                test_output_fpath = os.path.join(predictions_dir, \
                                    f'{predictions_prefix}model_{model_subexp}_test_{cur_subexp}.conllu')
                                predicted_test_files.append( test_output_fpath )
                                predicted_test_models.append( model_subexp )
                        else:
                            # Single test prediction
                            target_predicted_test = f'{predictions_prefix}test_{cur_subexp}.conllu'
                            predicted_test_files  = [os.path.join(predictions_dir, target_predicted_test)]
                            predicted_test_models = [None]
                        # Check for existence of files
                        paths_to_check2 = []
                        if not skip_train:
                            paths_to_check2.append( predicted_train )
                        paths_to_check2.extend( predicted_test_files )
                        for predicted_path in paths_to_check2:
                            if not os.path.exists(predicted_path) or \
                               not os.path.isfile(predicted_path):
                                missing_prediction_files.append(predicted_path)
                        if len(missing_prediction_files) == 0:
                            # ==================================================
                            #   All required files exist: evaluate
                            # ==================================================
                            for predicted_test, model_subexp in zip(predicted_test_files, predicted_test_models):
                                results = score_experiment( predicted_test, current_gold_test, 
                                                            predicted_train, gold_train, 
                                                            format_string=None,
                                                            count_words=param_count_words,
                                                            skip_train=skip_train, 
                                                            exclude_punct=exclude_punct, 
                                                            punct_tokens_set=punct_tokens_set )
                                if macro_average:
                                    # Collect macro averages
                                    for k, v in results.items():
                                        if k not in results_macro_avg.keys():
                                            results_macro_avg[k] = []
                                        results_macro_avg[k].append(v)
                                if round:
                                    # Find rounded results
                                    format_string = ':.4f'
                                    results_rounded = dict()
                                    for k, v in results.items():
                                        if k not in ['train_words', 'test_words']:
                                            results_rounded[k] = ('{'+format_string+'}').format(v)
                                        else:
                                            results_rounded[k] = '{}'.format(v)
                                    results = results_rounded
                                # experiment name (depends on whether we use test matrix or not)
                                if not test_matrix:
                                    experiment_name = f'{experiment_name_prefix}{cur_subexp}'
                                else:
                                    experiment_name = f'{experiment_name_prefix}model_{model_subexp}_test_{cur_subexp}'
                                # find experiment directory closest to root in experiment path
                                exp_root = get_experiment_path_root(current_gold_test)
                                if exp_root not in collected_results.keys():
                                    collected_results[exp_root] = dict()
                                if verbose:
                                    print(exp_root, experiment_name, results)
                                collected_results[exp_root][experiment_name] = results
                                intermediate_results.append( (experiment_name, cur_subexp, model_subexp, results) )
                                evaluations_done += 1
                        else:
                            # Missing files
                            if ignore_missing:
                                print(f'Skipping evaluation because of missing files: {missing_prediction_files!r}')
                            else:
                                raise FileNotFoundError(f'(!) Cannot evaluate, missing evaluation files: {missing_prediction_files!r}')
                    if macro_average and evaluations_done > 1:
                        # Find macro averages
                        calculated_averages = dict()
                        for k, v in results_macro_avg.items():
                            calculated_averages[k] = mean(v)
                            if round:
                                if k not in ['train_words', 'test_words']:
                                    calculated_averages[k] = \
                                        ('{'+format_string+'}').format( calculated_averages[k] )
                                else:
                                    calculated_averages[k] = \
                                        ('{}').format( int(calculated_averages[k]) )
                        assert exp_root in collected_results.keys()
                        experiment_name = f'{experiment_name_prefix}{"AVG"}'
                        if verbose:
                            print(exp_root, experiment_name, calculated_averages)
                        collected_results[exp_root][experiment_name] = calculated_averages
                        intermediate_results.append( (experiment_name, None, None, calculated_averages) )
            # ==================================================
            #  Output intermediate results (optional)
            # ==================================================
            if output_csv_file is not None and intermediate_results:
                print(f'Writing evaluation results into {output_csv_file} ...')
                with open(output_csv_file, 'w', encoding='utf-8', newline='') as output_csv:
                    csv_writer = csv.writer(output_csv)
                    if test_matrix:
                        # Write matrix of results
                        # rows: test sets, columns: models
                        subexp_names = []
                        for r in intermediate_results:
                            if r[1] not in subexp_names:
                                subexp_names.append(r[1])
                        header = [''] + subexp_names
                        csv_writer.writerow( header )
                        values = []
                        lines_written = 0
                        for (full_exp_name, exp1, exp2, results) in intermediate_results:
                            if (exp1 is not None) and (exp2 is not None):
                                if not values:
                                    values.append(exp1)
                                values.append(results['LAS_test'])
                                assert exp1 == values[0]
                                assert exp2 == subexp_names[len(values)-2]
                                if len(values) == len(subexp_names) + 1:
                                    csv_writer.writerow( values )
                                    lines_written += 1
                                    values = []
                        assert lines_written == len(subexp_names)
                    else:
                        # Write listing of results
                        result_fields = list(intermediate_results[0][3].keys())
                        header = ['experiment'] + result_fields
                        csv_writer.writerow( header )
                        for (full_exp_name, exp1, exp2, results) in intermediate_results:
                            values = [full_exp_name]
                            for key in header[1:]:
                                values.append( results[key] )
                            assert len(values) == len(header)
                            csv_writer.writerow( values )
    return collected_results


def get_experiment_path_root( experiment_path ):
    '''Finds directory closest to the root from the given experiment path.'''
    closest_to_root = None
    while len(experiment_path) > 0:
        head, tail = os.path.split( experiment_path )
        if len(head) == 0:
            closest_to_root = tail
        experiment_path = head
    return closest_to_root

def load_punct_tokens( fname ):
    '''
    Loads set of punctuation tokens from given file.
    If file name is None, returns an empty set.
    If file is given but missing, raises an exception.
    Returns set of punctuation tokens.
    '''
    punct_tokens = set()
    if fname is not None:
        if not os.path.exists(fname):
            raise Exception(f'(!) Non-existend punct tokens file: {fname!r}')
        with open(fname, 'r', encoding='utf-8') as in_f:
            for line in in_f:
                line = line.strip()
                if len(line) > 0:
                    punct_tokens.add(line)
    return punct_tokens

def score_experiment( predicted_test, gold_test, predicted_train, gold_train, 
                      gold_path=None, predicted_path=None, format_string=None,
                      skip_train=False, count_words=False, exclude_punct=False, 
                      punct_tokens_set=None ):
    '''
    Calculates train and test LAS/UAS scores and gaps between train and test LAS 
    using given predicted and gold standard conllu files. 
    If `format_string` provided (not None), then uses it to reformat all calculated
    scores. For instance, if `format_string=':.4f'`, then all scores will be rounded 
    to 4 decimals.
    Returns dictionary with calculated scores (keys: "LAS_test", "LAS_train", 
    "LAS_gap", "UAS_test", "UAS_train").
    If `count_words=True`, then adds evaluation word counts (keys 'train_words' 
    and 'test_words') to the results.
    If `skip_train` is True, then calculates only test scores and returns dictionary 
    with calculated test scores (keys: "LAS_test", "UAS_test").
    '''
    # Check/validate input files 
    input_files = { \
        'predicted_test': predicted_test,
        'gold_test': gold_test, 
        'predicted_train': predicted_train, 
        'gold_train': gold_train }
    for name, fpath in input_files.items():
        if skip_train and name.endswith('_train'):
            # skip evaluation on train files
            continue
        full_path = fpath
        if fpath is None:
            raise FileNotFoundError(f'(!) Unexpected None value for {name} file name.')
        # Update full path (if required)
        if name.startswith('gold_') and gold_path is not None:
            full_path = os.path.join(gold_path, fpath)
        if name.startswith('predicted') and predicted_path is not None:
            full_path = os.path.join(predicted_path, fpath)
        if not os.path.isfile(full_path):
            raise FileNotFoundError(f'(!) {name} file cannot be found at {full_path!r}.')
        input_files[name] = full_path
    # Calculate scores
    test_scores = calculate_scores(input_files['gold_test'], 
                                   input_files['predicted_test'],
                                   count_words=count_words,
                                   exclude_punct=exclude_punct,
                                   punct_tokens_set=punct_tokens_set)
    if skip_train:
        train_scores = None
        results_dict = {'LAS_test' : test_scores['LAS'], 
                        'UAS_test' : test_scores['UAS']}
    else:
        train_scores = calculate_scores(input_files['gold_train'], 
                                        input_files['predicted_train'],
                                        count_words=count_words,
                                        exclude_punct=exclude_punct,
                                        punct_tokens_set=punct_tokens_set)
        results_dict = {'LAS_test' : test_scores['LAS'], 
                        'LAS_train' : train_scores['LAS'], 
                        'LAS_gap' : train_scores['LAS'] - test_scores['LAS'],
                        'UAS_test' : test_scores['UAS'], 
                        'UAS_train' : train_scores['UAS']}
    if format_string is not None:
        for k, v in results_dict.items():
            results_dict[k] = ('{'+format_string+'}').format(v)
    if count_words:
        results_dict['test_words'] = test_scores['total_words']
        if not skip_train:
            results_dict['train_words'] = train_scores['total_words']
    return results_dict


def calculate_scores(gold_path: str, predicted_path: str, count_words=False, exclude_punct=False, punct_tokens_set=None):
    '''
    Calculates LAS, UAS and LA scores based on gold annotations and predicted annotations 
    loaded from conllu files `gold_path` and `predicted_path`. 
    Assumes that there are no tokenization differences in the gold and predicted outputs. 
    If exclude_punct==True, then discards punctuation (tokens with xpos == 'Z', or alternatively, 
    tokens appearing in given punct_tokens_set) from calculations.
    Always discards null nodes (tokens with non-integer id-s) from calculations.
    Returns dictionary with scores (keys: "LAS", "UAS", "LA").
    If `count_words=True`, then adds evaluation word count (key 'total_words') to the results.
    
    Note: if exclude_punct==False, then the LAS calculated here is compatible with the LAS.f1 
    calculated in CoNLL 2018 Shared Task. However, there's an exception: in the CoNLL 2018 
    evaluation, language-specific deprel subtypes are truncated (e.g. 'acl:relcl' is reduced 
    to 'acl' in both predicted and gold), but we compare deprels as they are. As a result, 
    CoNLL 2018 evaluation can give higher scores than this method.
    '''
    # Load annotated texts from conllu files
    gold_sents = None
    predicted_sents = None
    with open(gold_path, 'r', encoding='utf-8') as in_f:
        gold_sents = conllu.parse(in_f.read())
    with open(predicted_path, 'r', encoding='utf-8') as in_f_2:
        predicted_sents = conllu.parse(in_f_2.read())
    assert len(gold_sents) == len(predicted_sents), \
        f'(!) Mismatching sizes: gold_sents: {len(gold_sents)}, predicted_sents: {len(predicted_sents)}'

    las_match_count = 0
    uas_match_count = 0
    la_match_count = 0
    total_words = 0

    for i, gold_sentence in enumerate(gold_sents):
        predicted_sentece = predicted_sents[i]
        gold_sentence_words = [w['form'] for w in gold_sentence]
        auto_sentence_words = [w['form'] for w in predicted_sentece]
        assert gold_sentence_words == auto_sentence_words, \
            f'Tokenization mismatch in {predicted_path!r} | {gold_sentence_words} vs {auto_sentence_words}'
        word_tracker = 0
        for gold_word in gold_sentence:
            if not isinstance(gold_word['id'], int):
                continue
            if exclude_punct:
                # Exclude punctuation from evaluation
                if punct_tokens_set is not None:
                    if gold_word['form'] in punct_tokens_set:
                        word_tracker += 1
                        continue
                if gold_word['xpos'] == 'Z':
                    word_tracker += 1
                    continue

            total_words += 1

            predicted_word = predicted_sentece[word_tracker]

            if predicted_word['deprel'] == gold_word['deprel'] and predicted_word['head'] == gold_word['head']:
                las_match_count += 1
                la_match_count += 1
                uas_match_count += 1
            elif predicted_word['deprel'] == gold_word['deprel']:
                la_match_count += 1
            elif predicted_word['head'] == gold_word['head']:
                uas_match_count += 1

            word_tracker += 1
    result = \
        {'LAS': las_match_count / total_words, 
         'UAS': uas_match_count / total_words, 
         'LA': la_match_count / total_words}
    if count_words:
        result['total_words'] = total_words
    return result


def calculate_errors(gold_file, predicted_file, punct_tokens_set=None, remove_empty_nodes=True, 
                     add_impact=True, add_rel_error=True, add_counts=True, root_outside_clause=True, 
                     format_string=None):
    '''
    Adds automatic clause annotations to the input text (via EstNLTK), and decomposes 
    errors made by the system according to dependency misplacements inside or outside 
    the clause. The following error types are distinguished:
    
    * E1 (local error): according to both gold standard and parser, the head of a word is 
    inside the same clause but gold standard and parser do not agree on the exact word 
    and/or deprel;
    
    * E2 (local-global error): according to gold standard, the head of a word is inside 
    the same clause, but parser thinks it is outside of the clause;
    
    * E3 (global error): according to gold standard, the word's head is outside of the 
    clause, and the parser got the head wrong (placed it either inside or outside the 
    clause);
    
    Discards punctuation (tokens with xpos == 'Z', or alternatively, tokens appearing 
    in given punct_tokens_set) from error calculations.
    
    Note: by default, root nodes (words with head==0) are always considered as being 
    "outside the clause". Use flag root_outside_clause=False to count root nodes as 
    being "inside the clause" (this will increase E1 errors while decreasing E2 and E3 
    errors).
    
    Returns dictionary with calculated error counts ('E1', 'E2', 'E3'), and 
    additional statistics (see parameters add_impact, add_rel_error and add_counts 
    below for details).
    
    Requires EstNLTK version 1.7.2+.

    Parameters
    -----------
    gold_file
        CONLL-U format input file with gold standard syntax annotations
    predicted_file
        CONLL-U format input file with automatically predicted syntax annotations
    punct_tokens_set
        set with tokens that are considered as punctionation and that will be 
        discarded from evaluation. Undefined by default.
    remove_empty_nodes
        If True (default), then null / empty nodes (of the enhanced representation) 
        will be removed from input files (and discarded from calculations).
    add_impact
        If True (default), then calculates impacts and adds 'E1_impact', 'E2_impact', 
        and 'E3_impact' to the returned dictionary. Impact is the percentage of the 
        error from all errors. 
    add_rel_error
        If True (default), then calculates relative errors and adds 'E1_rel_error', 
        'E2_rel_error', and 'E3_rel_error' to the returned dictionary. Relative error 
        is the percentage from all arcs that can lead to given error type.
    add_counts
        If True (default), then adds token counts 'total_no_punct', 'correct', 
        'gold_in_clause', 'gold_out_of_clause', 'total_words', 'punct', 
        'unequal_length' to the returned dictionary.
    root_outside_clause:
        If True (default), then root nodes (words with head==0) are always considered 
        as being "outside the clause". Otherwise, root nodes are considered as being 
        "inside the clause".
    format_string
        If `format_string` provided (not None), then uses it to reformat values of 
        impacts and relative errors. For instance, if `format_string=':.4f'`, then 
        impacts and relative errors will be rounded to 4 decimals.
    '''
    if punct_tokens_set is None:
        punct_tokens_set = set()
    # Load gold standard and automatic annotations into separate layers
    text = conll_to_text(gold_file, syntax_layer='gold', remove_empty_nodes=remove_empty_nodes)
    add_layer_from_conll(file=predicted_file, text=text, syntax_layer='parsed')
    # Validate input sizes
    assert len(text['gold']) == len(text['parsed']), \
        f"(!) Mismatching input sizes: gold_words: {len(text['gold'])}, predicted_words: {len(text['parsed'])}"
    # Add automatic clauses annotation
    text.tag_layer('clauses')
    # Count errors
    punct = 0
    e1 = 0
    e2 = 0
    e3 = 0
    correct = 0
    unequal_length = 0
    total = 0
    total_no_punct = 0
    gold_in_clause = 0
    gold_out_of_clause = 0
    for idx, clause in enumerate(text.clauses):
        wordforms = list(clause.gold.text)
        gold_heads = list(clause.gold.head)
        gold_deprel = list(clause.gold.deprel)
        gold_pos = list(clause.gold.xpostag)
        try:
            parsed_heads = list(clause.parsed.head)
            parsed_deprel = list(clause.parsed.deprel)
        except AssertionError:
            unequal_length += len(gold_heads)
            total += len(gold_heads)
            continue
        in_clause_heads = list(clause.gold.id)
        if not root_outside_clause:
            # Count root node as being "inside 
            # the clause" rather than "outside 
            # the clause" (which is default).
            # This shifts error distribution
            # from E2 & E3 to E1.
            in_clause_heads.append( 0 )
        for wordform, pos, gold_head, parsed_head, gold_dep, parsed_dep in zip(wordforms, gold_pos, gold_heads, parsed_heads, gold_deprel, parsed_deprel):
            total += 1
            if wordform in punct_tokens_set:
                punct += 1
                pass
            elif pos == 'Z':
                punct += 1
                pass
            else:
                total_no_punct += 1
                if gold_head in in_clause_heads:
                    gold_in_clause += 1
                    if gold_head == parsed_head and gold_dep == parsed_dep:
                        correct += 1
                    else:
                        if parsed_head in in_clause_heads:
                            # local error: misplaced dependency inside the clause
                            e1 += 1
                        else:
                            # overarcing error:
                            # misplaced dependency outside the clause, 
                            # although it should be inside the clause
                            e2 += 1
                else:
                    gold_out_of_clause += 1
                    if gold_head == parsed_head and gold_dep == parsed_dep:
                        correct += 1
                    else:
                        # global error: misplaced dependency which should be 
                        # outside the clause (but was placed incorrectly
                        # inside or outside the clause)
                        e3 += 1
    # Calculate impacts/relative errors and format results (if required)
    result = {'E1': e1, 'E2': e2, 'E3': e3}
    if add_impact:
        result['E1_impact'] = e1/(total_no_punct-correct)
        result['E2_impact'] = e2/(total_no_punct-correct)
        result['E3_impact'] = e3/(total_no_punct-correct)
    if add_rel_error:
        result['E1_rel_error'] = e1/gold_in_clause
        result['E2_rel_error'] = e2/gold_in_clause
        result['E3_rel_error'] = e3/gold_out_of_clause
    if add_counts:
        result['total_no_punct'] = total_no_punct
        result['correct'] = correct
        result['gold_in_clause'] = gold_in_clause
        result['gold_out_of_clause'] = gold_out_of_clause
        result['total_words'] = total
        result['punct'] = punct
        result['unequal_length'] = unequal_length
    if format_string is not None:
        # Reformat impacts and relative errors
        for k, v in result.items():
            if k.endswith(('_impact', '_rel_error')):
                result[k] = ('{'+format_string+'}').format(v)
    return result


# ========================================================================

if __name__ == '__main__':
    # 1) Try to get configuration files from input args
    # Optionally, user can also pass name of the output csv file
    conf_files = []
    output_csv_file = 'results.csv'
    for input_arg in sys.argv[1:]:
        if (input_arg.lower()).endswith('.ini'):
            conf_files.append( input_arg )
        elif (input_arg.lower()).endswith('.csv'):
            output_csv_file = input_arg
    if len(conf_files) == 0:
        # 2) Try to collect configuration files from the root dir
        root_dir = '.'
        for fname in sorted( os.listdir(root_dir) ):
            if (fname.lower()).endswith('.ini'):
                # Attempt to open experiment configuration from INI file
                conf_file = os.path.join(root_dir, fname)
                conf_files.append(conf_file)
    if len(conf_files) > 0:
        # Perform evaluations defined in configurations
        collected_results = dict()
        for conf_file in conf_files:
            eval_main(conf_file, collected_results=collected_results, ignore_missing=True, 
                      verbose=True, round=True, count_words=False)
        # Save collected results into experiment root directory csv file
        for exp_root in collected_results.keys():
            filename = os.path.join(exp_root, output_csv_file) if os.path.exists(exp_root) else f'results_{exp_root}.csv'
            print(f'Writing evaluation results into {filename} ...')
            with open(filename, 'w', encoding='utf-8', newline='') as output_csv:
                csv_writer = csv.writer(output_csv)
                header = None
                for exp_name in collected_results[exp_root].keys():
                    exp_fields = list(collected_results[exp_root][exp_name].keys())
                    if header is None:
                        header = ['experiment'] + exp_fields
                        csv_writer.writerow( header )
                    else:
                        assert header[1:] == exp_fields
                    values = [exp_name]
                    for key in header[1:]:
                        values.append( collected_results[exp_root][exp_name][key] )
                    assert len(values) == len(header)
                    csv_writer.writerow( values )
    else:
        raise Exception('(!) Could not found any configuration INI file from the root directory nor from input arguments')