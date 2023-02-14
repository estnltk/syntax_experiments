#
#    Looks through all experiment configurations, and 
#    performs evaluations described in configuration 
#    files: compares predicted files to gold standard 
#    files and finds LAS/UAS scores.
#
#    Supported settings:
#       * full_data
#       * multi_experiment (general)
#       * crossvalidation
#       * half_data
#       * smaller_data
#

import sys
import csv, re
import os, os.path
from statistics import mean
import configparser
import warnings

import conllu


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
            if experiment_type_clean == 'full_data':
                # ------------------------------------------
                # 'full_data'
                # ------------------------------------------
                # gold_train and gold_test with paths
                if not config.has_option(section, 'gold_train'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "gold_train" parameter.')
                gold_train = config[section]['gold_train']
                if not config.has_option(section, 'gold_test'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "gold_test" parameter.')
                gold_test = config[section]['gold_test']
                gold_train_exists = os.path.exists(gold_train)
                gold_test_exists  = os.path.exists(gold_test)
                # predicted_train and predicted_test with paths
                if not config.has_option(section, 'predicted_train'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "predicted_train" parameter.')
                predicted_train = config[section]['predicted_train']
                if not config.has_option(section, 'predicted_test'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "predicted_test" parameter.')
                predicted_test = config[section]['predicted_test']
                predicted_train_exists = os.path.exists(predicted_train)
                predicted_test_exists  = os.path.exists(predicted_test)
                param_count_words = config[section].getboolean('count_words', count_words)
                experiment_name = config[section].get('name', section)
                punct_tokens_file = config[section].get('punct_tokens_file', None)
                punct_tokens_set = load_punct_tokens( punct_tokens_file )  # Attempt to load from file. If None, return empty set
                all_files_exist = gold_train_exists and gold_test_exists and \
                                  predicted_train_exists and predicted_test_exists
                if all_files_exist:
                    format_string = ':.4f' if round else None
                    results = score_experiment( predicted_test, gold_test, predicted_train, gold_train, 
                                                gold_path=None, predicted_path=None, format_string=format_string,
                                                count_words=param_count_words, punct_tokens_set=punct_tokens_set )
                    if verbose:
                        print(results)
                    # find experiment directory closest to root in experiment path
                    exp_root = get_experiment_path_root(gold_test)
                    if exp_root not in collected_results.keys():
                        collected_results[exp_root] = dict()
                    collected_results[exp_root][experiment_name] = results
                else:
                    missing_files = [f for f in [predicted_test, gold_test, predicted_train, gold_train] if not os.path.exists(f)]
                    if ignore_missing:
                        print(f'Skipping evaluation because of missing files: {missing_files!r}')
                    else:
                        raise FileNotFoundError(f'(!) Cannot evaluate, missing evaluation files: {missing_files!r}')
            elif experiment_type_clean in ['crossvalidation', 'half_data', 'smaller_data', 'multi_experiment']:
                # ------------------------------------------
                # 'multi_experiment' (general)
                # 'crossvalidation'
                # 'half_data'
                # 'smaller_data'
                # ------------------------------------------
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
                predictions_dir = config[section]['predictions_dir']
                predictions_prefix = config[section].get('predictions_prefix', 'predicted_')
                macro_average = config[section].getboolean('macro_average', False)
                param_count_words = config[section].getboolean('count_words', count_words)
                experiment_name_prefix = config[section].get('name_prefix', section)
                punct_tokens_file = config[section].get('punct_tokens_file', None)
                punct_tokens_set = load_punct_tokens( punct_tokens_file )  # Attempt to load from file. If None, return empty set
                if not experiment_name_prefix.endswith('_'):
                    experiment_name_prefix = experiment_name_prefix + '_'
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
                # Try to collect evaluation files
                evaluation_files = []
                if os.path.exists(predictions_dir) and os.path.exists(gold_splits_dir) and \
                   (test_file_regex is not None or os.path.exists(gold_test)):
                    evaluations_done = 0
                    results_macro_avg = dict()
                    for gold_file in sorted( os.listdir(gold_splits_dir) ):
                        m = train_file_regex.match(gold_file)
                        if m:
                            if not (gold_file.lower()).endswith('.conllu'):
                                raise Exception( f'(!) invalid file {gold_file}: train file '+\
                                                  'must have extension .conllu' )
                            no = m.group('exp')
                            experiment_name = f'{experiment_name_prefix}{no}'
                            missing_files = []
                            gold_train = os.path.join(gold_splits_dir, gold_file)
                            current_gold_test = gold_test
                            if test_file_regex is not None:
                                # Find gold_test corresponding to gold_train
                                gold_test_found = False
                                for gold_file_2 in sorted(os.listdir(gold_splits_dir)):
                                    m2 = test_file_regex.match(gold_file_2)
                                    if m2:
                                        no2 = m2.group('exp')
                                        if no == no2:
                                            current_gold_test = \
                                                os.path.join(gold_splits_dir, gold_file_2)
                                            gold_test_found = True
                                            break
                                if not gold_test_found:
                                    warnings.warn(f'Unable to find test file corresponding to '+\
                                                  f'train file {gold_file!r} from {gold_splits_dir!r}.')
                                    missing_files.append( current_gold_test )
                            predicted_train = None
                            predicted_test = None
                            # Find corresponding train prediction
                            target_predicted_train = f'{predictions_prefix}train_{no}.conllu'
                            predicted_train = os.path.join(predictions_dir, target_predicted_train)
                            # Find corresponding test prediction
                            target_predicted_test = f'{predictions_prefix}test_{no}.conllu'
                            predicted_test = os.path.join(predictions_dir, target_predicted_test)
                            # Find out whether prediction files exist
                            for predicted_path in [predicted_train, predicted_test]:
                                if not os.path.exists(predicted_path) or \
                                   not os.path.isfile(predicted_path):
                                    missing_files.append(predicted_path)
                            if len(missing_files) == 0:
                                # All required files exist: evaluate
                                results = score_experiment( predicted_test, current_gold_test, 
                                                            predicted_train, gold_train, 
                                                            format_string=None,
                                                            count_words=param_count_words,
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
                                # find experiment directory closest to root in experiment path
                                exp_root = get_experiment_path_root(current_gold_test)
                                if exp_root not in collected_results.keys():
                                    collected_results[exp_root] = dict()
                                if verbose:
                                    print(exp_root, experiment_name, results)
                                collected_results[exp_root][experiment_name] = results
                                evaluations_done += 1
                            else:
                                # Missing files
                                if ignore_missing:
                                    print(f'Skipping evaluation because of missing files: {missing_files!r}')
                                else:
                                    raise FileNotFoundError(f'(!) Cannot evaluate, missing evaluation files: {missing_files!r}')
                    if evaluations_done > 1:
                        if macro_average:
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
                    else:
                        # Report no eval files found
                        print(f'Could not find any gold train files matching pattern {train_file_pat!r} from {gold_splits_dir!r}.')
                else:
                    # Find out missing paths
                    missing_paths = []
                    for input_path in [predictions_dir, gold_splits_dir, gold_test]:
                        if not os.path.exists(input_path):
                            missing_paths.append(input_path)
                    # Report missing paths
                    if ignore_missing:
                        print(f'Skipping evaluation because of missing dirs/files: {missing_paths!r}')
                    else:
                        raise FileNotFoundError(f'(!) Cannot evaluate, missing evaluation dirs/files: {missing_paths!r}')
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
                      count_words=False, punct_tokens_set=None ):
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
    '''
    # Check/validate input files 
    input_files = { \
        'predicted_test': predicted_test,
        'gold_test': gold_test, 
        'predicted_train': predicted_train, 
        'gold_train': gold_train }
    for name, fpath in input_files.items():
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
                                   punct_tokens_set=punct_tokens_set)
    train_scores = calculate_scores(input_files['gold_train'], 
                                    input_files['predicted_train'],
                                    count_words=count_words,
                                    punct_tokens_set=punct_tokens_set)
    LAS_test = test_scores['LAS']
    UAS_test = test_scores['UAS']
    LAS_train = train_scores['LAS']
    UAS_train = train_scores['UAS']
    results_dict = {'LAS_test' : LAS_test, 
                    'LAS_train' : LAS_train, 
                    'LAS_gap' : LAS_train - LAS_test,
                    'UAS_test' : UAS_test, 
                    'UAS_train' : UAS_train}
    if format_string is not None:
        for k, v in results_dict.items():
            results_dict[k] = ('{'+format_string+'}').format(v)
    if count_words:
        results_dict['test_words'] = test_scores['total_words']
        results_dict['train_words'] = train_scores['total_words']
    return results_dict


def calculate_scores(gold_path: str, predicted_path: str, count_words=False, punct_tokens_set=None):
    '''
    Calculates LAS, UAS and LA scores based on gold annotations and predicted annotations 
    loaded from conllu files `gold_path` and `predicted_path`. 
    Discards punctuation (tokens with xpos == 'Z', or alternatively, tokens appearing in given 
    punct_tokens_set) and null nodes (tokens with non-integer id-s) from calculations.
    Returns dictionary with scores (keys: "LAS", "UAS", "LA").
    If `count_words=True`, then adds evaluation word count (key 'total_words') to the results.
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
        word_tracker = 0
        for gold_word in gold_sentence:
            if not isinstance(gold_word['id'], int):
                continue
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