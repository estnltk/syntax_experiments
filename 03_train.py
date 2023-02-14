#
#    Trains models according to experiment settings.
#    Supported models:
#       * stanza syntax (depparse)
#    Implemented settings:
#       * full_data
#       * multi_experiment (general)
#       * crossvalidation
#       * half_data
#       * smaller_data
#
import os
import os.path
import sys
import re
import argparse
from datetime import datetime

from stanza.models.parser import main as stanza_main

from stanza.utils.conll18_ud_eval import load_conllu_file as stanza_load_conllu_file
from stanza.utils.conll18_ud_eval import evaluate
from stanza.utils.conll18_ud_eval import build_evaluation_table

import configparser

# ===============================================================
#  Train Stanza for syntax (MAIN)
# ===============================================================

def train_models_main( conf_file, subexp=None, dry_run=False ):
    '''
    Trains models based on the configuration. 
    Settings/parameters of the training will be read from the given 
    `conf_file`. 
    Executes sections in the configuration starting with prefix 
    'train_stanza_'. 
    
    Optinally, if `subexp` is defined, then trains and evaluates only 
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
        # ------------------------------------------
        #  s t a n z a
        # ------------------------------------------
        if section.startswith('train_stanza_'):
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
                # eval_file with path
                if not config.has_option(section, 'eval_file'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "eval_file" parameter.')
                eval_file = config[section]['eval_file']
                if not os.path.isfile(eval_file):
                    raise FileNotFoundError(f'Error in {conf_file}: invalid "eval_file" value {eval_file!r} in {section!r}.')
                # output_dir
                if not config.has_option(section, 'output_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
                output_model_dir = config[section]['output_dir']
                # other parameters
                output_model_file = config[section].get('model_file', ' model.pt')
                extra_args = config[section].get('args', '')
                dry_run = config[section].getboolean('dry_run', dry_run)
                predict_after = config[section].getboolean('predict_after', False)
                parser = 'stanza'
                eval_path, eval_file_name = os.path.split(eval_file)
                output_file = os.path.join( output_model_dir, 'train_output_'+eval_file_name )
                output_eval_score_file = 'eval_'+(eval_file_name.replace('.conllu', '_score.txt'))
                output_eval_score_file = os.path.join(output_model_dir, output_eval_score_file)

                print(f'Training {parser} parser with {train_file}, {eval_file} --> {output_file}, '+
                      f'{output_model_dir}/{output_model_file}')
                print(f'Parameters: {extra_args}')

                train_stanza( train_file, eval_file, output_model_dir, output_model_file, \
                              output_file, args=extra_args, dry_run=dry_run )
                if predict_after:
                    predict_eval_with_stanza(eval_file, output_model_dir, output_model_file, output_file, 
                                             dry_run=dry_run)
                    run_conll18_ud_eval(eval_file, output_file, return_type='las_f1', 
                                        save_results_file=output_eval_score_file, dry_run=dry_run)
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
                output_model_dir = config[section]['output_dir']
                extra_args = config[section].get('args', '')
                dry_run = config[section].getboolean('dry_run', dry_run)
                predict_after = config[section].getboolean('predict_after', False)
                parser = 'stanza'
                # Patterns for capturing names of sub-experiment files
                train_file_pat = r'(?P<exp>\d+)_train.conllu'
                dev_file_pat   = r'(?P<exp>\d+)_dev.conllu'
                test_file_pat  = r'(?P<exp>\d+)_dev.conllu'
                # Override sub-experiment patterns (if required)
                if config.has_option(section, 'train_file_pat'):
                    train_file_pat = config[section]['train_file_pat']
                if config.has_option(section, 'dev_file_pat'):
                    dev_file_pat = config[section]['dev_file_pat']
                if config.has_option(section, 'test_file_pat'):
                    test_file_pat = config[section]['test_file_pat']
                # Launch experiments
                bulk_train( input_dir, train_file_pat, dev_file_pat, test_file_pat, 
                            output_model_dir, subexp=subexp, parser=parser, 
                            predict_after=predict_after, args=extra_args, 
                            dry_run=dry_run )
    if not section_found:
        print(f'No section starting with "train_stanza_" in {conf_file}.')


# ========================================================================
#  Bulk training (for crossvalidation, half-data etc.)
# ========================================================================

def bulk_train( data_folder, train_file_pat, dev_file_pat, test_file_pat, output_path, 
                subexp=None, parser='stanza', predict_after=True, args='', dry_run=False ):
    '''
    Trains models of multiple sub-experiments on (train/dev) files from `data_folder`. 
    Optinally, also evaluates each sub-experiment model (on test files). 
    Outputs trained models and evaluation results to `output_path`. 
    
    Parameters `train_file_pat`, `dev_file_pat` and `test_file_pat` must be strings 
    compilable into regexp patterns that can be used to detect data sets of all sub-
    experiments. 
    Each of these patterns must have the named group 'exp', indicating part of the 
    pattern matching sub-experiment name. 
    
    Use parameter `subexp` to restrict training and evaluation only to a single 
    sub-experiment instead of performing all sub-experiments. 
    This is useful when multiple instances of the Python are launched for 
    parallelization. 
    
    Additional (training) parameters for parser can be provided via `args`.
    '''
    # Validate input arguments
    supported_parsers = ['stanza']
    if not isinstance(parser, str) or parser.lower() not in supported_parsers:
        raise ValueError( f'(!) Unexpected parser: {parser!r}. '+\
                          f'Supported parsers: {supported_parsers!r}' )
    parser = parser.lower()
    if not os.path.exists(data_folder) or not os.path.isdir(data_folder):
        raise Exception(f'(!) Missing or invalid input directory {data_folder!r}')
    file_patterns = [ ['train', train_file_pat], 
                      ['dev',   dev_file_pat],
                      ['test',  test_file_pat] ]
    # Convert file patterns to regular experssions
    regexp_file_patterns = []
    for subset, file_pat in file_patterns:
        if not isinstance(file_pat, str):
            raise TypeError(f'{subset}_file_pat must be a string')
        regexp = None
        try:
            regexp = re.compile(file_pat)
        except Exception as err:
            raise ValueError(f'Unable to convert {file_pat!r} to regexp') from err
        if 'exp' not in regexp.groupindex:
            raise ValueError(f'Regexp {file_pat!r} is missing named group "exp"')
        regexp_file_patterns.append( [subset, regexp] )
    # Collect experiment input files
    experiment_data = { 'train':[], 'dev':[], 'test':[], 'numbers':[] }
    for fname in sorted( os.listdir(data_folder) ):
        for [subset, regex_file_pat] in regexp_file_patterns:
            m = regex_file_pat.match(fname)
            if m:
                if not (fname.lower()).endswith('.conllu'):
                    raise Exception( f'(!) invalid file {fname}: {subset} file '+\
                                      'must have extension .conllu' )
                fpath = os.path.join(data_folder, fname)
                experiment_data[subset].append( fpath )
                no = m.group('exp')
                if no not in experiment_data['numbers']:
                    experiment_data['numbers'].append(no)
    # Validate that we have all required files
    for [subset, file_pat] in file_patterns:
        if len(experiment_data[subset]) == 0:
            raise Exception(f'Unable to find any {subset} files '+\
                            f'matching {file_pat!r} in dir {data_folder!r}.')
        if len(experiment_data[subset]) != len(experiment_data['numbers']):
            no1 = len(experiment_data[subset])
            no2 = len(experiment_data['numbers'])
            raise Exception(f'Number of {subset} files ({no1}) does not match '+\
                            f'the number of experiments ({no2}).')
    if subexp is not None:
        if subexp not in experiment_data['numbers']:
            raise ValueError( f'(!) sub-experiment {subexp!r} not in collected '+\
                              f'experiment names: {experiment_data["numbers"]}.' )
    # Launch experiments
    start_time = datetime.now()
    for i in range( len(experiment_data['numbers']) ):
        exp_no     = experiment_data['numbers'][i]
        train_file = experiment_data['train'][i]
        dev_file   = experiment_data['dev'][i]
        test_file  = experiment_data['test'][i]
        if subexp is not None and exp_no != subexp:
            # Skip other experiments
            continue
        output_model_dir  = output_path
        output_model_file = f"model_{exp_no}.pt"
        test_path, test_file_name = os.path.split(test_file)
        output_file = os.path.join( output_model_dir, 'train_output_'+test_file_name )
        output_eval_score_file = 'eval_'+(test_file_name.replace('.conllu', '_score.txt'))
        output_eval_score_file = os.path.join(output_model_dir, output_eval_score_file)

        print('='*(len(exp_no)*2))
        print(f' {exp_no}')
        print('='*(len(exp_no)*2))
        print(f'Training {parser} parser with {train_file}, {dev_file}, {test_file} --> '+
              f'{output_file}, {output_model_dir}/{output_model_file}')
        print(f'Parameters: {args}')

        if parser == 'stanza':
            train_stanza( train_file, dev_file, output_model_dir, output_model_file, \
                          output_file, args=args, dry_run=dry_run )
            if predict_after:
                predict_eval_with_stanza(test_file, output_model_dir, output_model_file, output_file, 
                                         dry_run=dry_run)
                las = run_conll18_ud_eval(test_file, output_file, return_type='las_f1', 
                                          save_results_file=output_eval_score_file, 
                                          dry_run=dry_run)
                #print(f'Best model eval score: {las}')
        print()
    print()
    print(f'Total time elapsed: {datetime.now()-start_time}')

# ========================================================================
#  Stanza interface: training models and predicting on eval set           
# ========================================================================

def train_stanza(train_file, eval_file, output_model_dir, output_model_file, output_file, 
                 lang='et', treebank='et_edt', args='', dry_run=False):
    '''
    Trains single stanza model on `train_file` using `eval_file` for parameter tuning 
    and model evaluation. 
    
    Note: in previous experiments, in addition to `eval_file`, a separate parameter 
    `gold_file` was defined. Here, we assume that `gold_file` == `eval_file`, so only 
    parameter `eval_file` is required. 
    
    Uses parameters of stanza parser:
    --save_dir : Root dir for saving models (output_model_dir)
    --save_name : File name to save the model (output_model_file)
    --train_file : Input file for data loader.
    --eval_file :  Input file for data loader.
    --no_pretrain : Turn off pretrained embeddings.
    --output_file : Output CoNLL-U file.
    --gold_file   : Output CoNLL-U file. (gold labels for eval_file)
    --lang : Language
    --shorthand : Treebank shorthand
    --mode : choices=['train', 'predict']
    --batch_size : default=5000
    '''
    if not os.path.exists(output_model_dir):
        os.makedirs(output_model_dir, exist_ok=True)
    stanza_args = \
        f'--save_dir {output_model_dir} --save_name {output_model_file} --train_file {train_file} --eval_file {eval_file} --no_pretrain '+\
        f'--output_file {output_file} --gold_file {eval_file} --lang {lang} --shorthand {treebank} --mode train {args}'
    if dry_run:
        return
    stanza_main( args=stanza_args.split() )


def predict_eval_with_stanza(eval_file, output_model_dir, output_model_file, output_file, 
                             lang='et', treebank='et_edt', args='', dry_run=False):
    '''
    Uses existing stanza's model `output_model_file` to predict labels for `eval_file`.
    
    Note: in previous experiments, in addition to `eval_file`, a separate parameter 
    `gold_file` was defined. Here, we assume that `gold_file` == `eval_file`, so only 
    parameter `eval_file` is required. 
    
    Uses parameters of stanza parser:
    --save_dir : Root dir for saving models (output_model_dir)
    --save_name : File name to save the model (output_model_file)
    --eval_file :  Input file for data loader.
    --no_pretrain : Turn off pretrained embeddings.
    --output_file : Output CoNLL-U file.
    --gold_file   : Output CoNLL-U file. (gold labels for eval_file)
    --lang : Language
    --shorthand : Treebank shorthand
    --mode : choices=['train', 'predict']
    '''
    if not os.path.exists(output_model_dir):
        raise ValueError(f'(!) Non-existent model path: {output_model_dir}/{output_model_file}')
    stanza_args = \
        f'--save_dir {output_model_dir} --save_name {output_model_file} --no_pretrain --eval_file {eval_file} '+\
        f'--output_file {output_file} --gold_file {eval_file} --lang {lang} --shorthand {treebank} --mode predict '+\
        f'{args}'
    if dry_run:
        return
    stanza_main( args=stanza_args.split() )


# ========================================================================
#  Stanza interface: evaluation                                           
# ========================================================================

def run_conll18_ud_eval(gold_file, system_file, return_type='las_f1', save_results_file=None, dry_run=False):
    '''
    Calculates CONLL-2018 evaluation scores based on given `gold_file` and `system_file`.
    If return_type == 'las_f1' (default), then returns LAS score (as string).
    If return_type == 'table' (default), then returns CONLL-2018 evaluation table (as string).
    Optionally, if `save_results_file` is provided, saves returned value into given file.
    '''
    if not isinstance(return_type, str) or \
       return_type.lower() not in ['las_f1', 'table']:
        raise ValueError(f'(!) Unexpected return type {return_type!r}')
    if dry_run:
        return None
    # Evaluate
    # The following code is based on:    
    #   https://github.com/stanfordnlp/stanza/blob/main/stanza/utils/conll18_ud_eval.py#L658-L673
    treebank_type = {}
    treebank_type['no_gapping'] = 0
    treebank_type['no_shared_parents_in_coordination'] = 0
    treebank_type['no_shared_dependents_in_coordination'] = 0
    treebank_type['no_control'] = 0
    treebank_type['no_external_arguments_of_relative_clauses'] = 0
    treebank_type['no_case_info'] = 0
    treebank_type['no_empty_nodes'] = False
    treebank_type['multiple_roots_okay'] = False
    # Load CoNLL-U files
    gold_ud = stanza_load_conllu_file(gold_file, treebank_type)
    system_ud = stanza_load_conllu_file(system_file, treebank_type)
    eval_result = evaluate(gold_ud, system_ud)
    # Format results
    if return_type.lower() == 'las_f1':
        # result is LAS f1 score
        result = f'{(100*eval_result["LAS"].f1):.2f}'
    elif return_type.lower() == 'table':
        # result is a table of scores
        result = build_evaluation_table(eval_result, True, False, True)
    if save_results_file is not None:
        # Save results if needed
        assert isinstance(save_results_file, str) and len(save_results_file) > 0
        with open(save_results_file, 'w', encoding='utf-8') as out_f:
            out_f.write(str(result))
    return result


# ========================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    conf_file = sys.argv[1]
    subexp = None
    if len(sys.argv) > 2:
        subexp = sys.argv[2]
    train_models_main( conf_file, subexp=subexp )