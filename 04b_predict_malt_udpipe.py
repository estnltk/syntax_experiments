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

from conllu import parse_incr
from conllu.serializer import serialize_field

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
                # other parameters
                dry_run = config[section].getboolean('dry_run', dry_run)
                default_model = 'model.mco' if parser == 'maltparser' else 'model.udpipe'
                model_file = config[section].get('model_file', default_model)
                # MaltParser options
                maltparser_dir = config[section].get('maltparser_dir', DEFAULT_MALTPARSER_DIR)
                maltparser_jar = config[section].get('maltparser_jar', DEFAULT_MALTPARSER_JAR)
                # UDPipe-1 options
                udpipe_dir = config[section].get('udpipe_dir', DEFAULT_UDPIPE_DIR)
                if not dry_run:
                    if parser == 'maltparser':
                        # Predict on train
                        output_file = f'{output_prefix}train.conllu'
                        predict_maltparser(model_file, train_file, output_file, output_dir, 
                                           maltparser_dir=maltparser_dir,
                                           maltparser_jar=maltparser_jar)
                        # Predict on test
                        output_file = f'{output_prefix}test.conllu'
                        predict_maltparser(model_file, test_file, output_file, output_dir, 
                                           maltparser_dir=maltparser_dir,
                                           maltparser_jar=maltparser_jar)
                    elif parser == 'udpipe1':
                        # Predict on train
                        output_file = f'{output_prefix}train.conllu'
                        predict_udpipe1(model_file, train_file, output_file, output_dir, 
                                        udpipe_dir=udpipe_dir)
                        # Predict on test
                        output_file = f'{output_prefix}test.conllu'
                        predict_udpipe1(model_file, test_file, output_file, output_dir, 
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
                # MaltParser options
                maltparser_dir = config[section].get('maltparser_dir', DEFAULT_MALTPARSER_DIR)
                maltparser_jar = config[section].get('maltparser_jar', DEFAULT_MALTPARSER_JAR)
                # UDPipe-1 options
                udpipe_dir = config[section].get('udpipe_dir', DEFAULT_UDPIPE_DIR)
                # Iterate over input files and predict
                for in_fname in sorted(os.listdir(input_dir)):
                    if in_fname.endswith('.conllu'):
                        m1 = train_file_re.match(in_fname)
                        if m1:
                            # Got the train file!
                            cur_train_file = os.path.join(input_dir, in_fname)
                            cur_subexp = m1.group('exp')
                            if subexp is not None:
                                if cur_subexp != subexp:
                                    continue
                            # Try to find corresponding test file
                            cur_test_file = test_file
                            if test_file_re is not None:
                                cur_test_file = None
                                for in_fname2 in sorted(os.listdir(input_dir)):
                                    if in_fname2.endswith('.conllu'):
                                        m2 = test_file_re.match(in_fname2)
                                        if m2:
                                            test_file_subexp = m2.group('exp')
                                            if cur_subexp == test_file_subexp:
                                                cur_test_file = \
                                                    os.path.join(input_dir, in_fname2)
                                                break
                                if cur_test_file is None:
                                    raise Exception(f'(!) Could not find test file matching pattern {test_file!r} '+\
                                                    f'for experiment {cur_subexp!r} from {input_dir!r}.')
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
                                    # Predict on train
                                    predict_maltparser(model_path, cur_train_file, train_output_file, output_dir, 
                                                       maltparser_dir=maltparser_dir,
                                                       maltparser_jar=maltparser_jar)
                                    # Predict on test
                                    predict_maltparser(model_path, cur_test_file, test_output_file, output_dir, 
                                                       maltparser_dir=maltparser_dir,
                                                       maltparser_jar=maltparser_jar)
                                elif parser == 'udpipe1':
                                    # Predict on train
                                    predict_udpipe1(model_path, cur_train_file, train_output_file, output_dir, 
                                                    udpipe_dir=udpipe_dir)
                                    # Predict on test
                                    predict_udpipe1(model_path, cur_test_file, test_output_file, output_dir, 
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

# ========================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    conf_file = sys.argv[1]
    subexp = None
    if len(sys.argv) > 2:
        subexp = sys.argv[2]
    run_models_main( conf_file, subexp=subexp )
