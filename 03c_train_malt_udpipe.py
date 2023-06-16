#
#    Trains MaltParser/UDPipe1 models according to experiment settings.
#    Supported settings:
#       * full_data
#       * multi_experiment (general)
#       * crossvalidation
#       * half_data
#       * smaller_data
#
import subprocess
import os, os.path
import sys, re
import pkgutil
import configparser

from conllu import parse_incr

# Change to local paths & files, if required
DEFAULT_MALTPARSER_DIR = 'MaltOptimizer-1.0.3'
DEFAULT_MALTPARSER_JAR = 'maltparser-1.9.2.jar'
#DEFAULT_UDPIPE_DIR = 'udpipe-1.2.0-bin\\bin-win64'
DEFAULT_UDPIPE_DIR = 'udpipe-1.2.0-bin/bin-linux64'

def train_malt_udpipe_main( conf_file, subexp=None, dry_run=False ):
    '''
    Trains MaltParser/UDPipe-1 models based on the configuration. 
    Settings/parameters of the training will be read from the given 
    `conf_file`. 
    Executes sections in the configuration starting with prefix 
    'train_malt_' and 'train_udpipe1_'. 
    
    Optinally, if `subexp` is defined, then trains only that 
    sub-experiment and skips all other sub-experiments (in 
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
        if section.startswith('train_malt_') or section.startswith('train_udpipe1_'):
            parser = 'maltparser' if section.startswith('train_malt_') else 'udpipe1'
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
                # output_dir
                if not config.has_option(section, 'output_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
                output_model_dir = config[section]['output_dir']
                # other parameters
                dry_run = config[section].getboolean('dry_run', dry_run)
                default_model = 'model.mco' if parser == 'maltparser' else 'model.udpipe'
                output_model_file  = config[section].get('model_file', default_model)
                # MaltParser options
                final_options_file = config[section].get('final_options_file', None)
                feature_model_file = config[section].get('feature_model_file', None)
                maltparser_dir = config[section].get('maltparser_dir', DEFAULT_MALTPARSER_DIR)
                maltparser_jar = config[section].get('maltparser_jar', DEFAULT_MALTPARSER_JAR)
                # UDPipe-1 options
                create_embeddings_file = config[section].get('create_embeddings_file', None)
                parser_options = config[section].get('parser_options', None)
                udpipe_dir = config[section].get('udpipe_dir', DEFAULT_UDPIPE_DIR)
                if not dry_run:
                    if parser == 'maltparser':
                        train_maltparser(output_model_file, train_file, output_dir=output_model_dir, 
                                         final_options_file=final_options_file, 
                                         feature_model_file=feature_model_file,
                                         maltparser_dir=maltparser_dir,
                                         maltparser_jar=maltparser_jar)
                    elif parser == 'udpipe1':
                        train_udpipe1(output_model_file, train_file, output_model_dir, 
                                      parser_options=parser_options, 
                                      create_embeddings_file=create_embeddings_file,
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
                output_model_dir = config[section]['output_dir']
                # Common options
                dry_run = config[section].getboolean('dry_run', dry_run)
                train_file_pat = r'(?P<exp>\d+)_train.conllu'
                train_file_re = None
                if config.has_option(section, 'train_file_pat'):
                    train_file_pat = config[section]['train_file_pat']
                train_file_re = _create_regexp_pattern(train_file_pat, 'train_file_pat')
                # MaltParser options
                maltparser_dir = config[section].get('maltparser_dir', DEFAULT_MALTPARSER_DIR)
                maltparser_jar = config[section].get('maltparser_jar', DEFAULT_MALTPARSER_JAR)
                feature_files_dir = config[section].get('feature_files_dir', None)
                final_options_file_pat = r'finalOptionsFile(?P<exp>\S+)\.xml'
                feature_model_file_pat = r'featureFile(?P<exp>\S+)\.xml'
                final_options_file_re = None
                feature_model_file_re = None
                if config.has_option(section, 'final_options_file_pat'):
                    final_options_file_pat = config[section]['final_options_file_pat']
                if config.has_option(section, 'feature_model_file_pat'):
                    feature_model_file_pat = config[section]['feature_model_file_pat']
                final_options_file_re = _create_regexp_pattern( final_options_file_pat, 
                                                                'final_options_file_pat')
                feature_model_file_re  = _create_regexp_pattern( feature_model_file_pat, 
                                                                 'feature_model_file_pat')
                all_feature_files = []
                if feature_files_dir is not None and os.path.isdir(feature_files_dir):
                    all_feature_files = [fname for fname in os.listdir(feature_files_dir)]
                # UDPipe-1 options
                create_embeddings_file = config[section].get('create_embeddings_file', None)
                parser_options = config[section].get('parser_options', None)
                udpipe_dir = config[section].get('udpipe_dir', DEFAULT_UDPIPE_DIR)
                # Iterate over input files and train
                for in_fname in os.listdir(input_dir):
                    if in_fname.endswith('.conllu'):
                        m = train_file_re.match(in_fname)
                        if m:
                            # Candidate for a training file
                            train_file = os.path.join(input_dir, in_fname)
                            cur_subexp = m.group('exp')
                            if subexp is not None:
                                if cur_subexp != subexp:
                                    continue
                            if parser == 'maltparser':
                                output_model_file = f'model_{cur_subexp}.mco'
                            else:
                                output_model_file = f'model_{cur_subexp}.udpipe'
                            # Fetch Maltparser feature files
                            final_options_file = None
                            feature_model_file = None
                            # Try to find feature selection files (if any provided)
                            if len(all_feature_files) > 0:
                                cur_subexp_lstrip = cur_subexp.lstrip('0')
                                for feats_file in all_feature_files:
                                    f1 = final_options_file_re.match(feats_file)
                                    f2 = feature_model_file_re.match(feats_file)
                                    if f1 and (f1.group('exp') == cur_subexp or \
                                               f1.group('exp') == cur_subexp_lstrip):
                                        final_options_file = os.path.join(feature_files_dir, 
                                                                          feats_file)
                                    if f2 and (f2.group('exp') == cur_subexp or \
                                               f2.group('exp') == cur_subexp_lstrip):
                                        feature_model_file = os.path.join(feature_files_dir, 
                                                                          feats_file)
                                if final_options_file is None:
                                    raise Exception(f'Unable to find final_options_file for experiment {cur_subexp!r}')
                                if feature_model_file is None:
                                    raise Exception(f'Unable to find feature_model_file for experiment {cur_subexp!r}')
                            # Launch training
                            if not dry_run:
                                if parser == 'maltparser':
                                    print(f' Training Maltparser on {train_file} (exp: {cur_subexp}) ...')
                                    train_maltparser(output_model_file, train_file, 
                                                     output_dir=output_model_dir, 
                                                     final_options_file=final_options_file, 
                                                     feature_model_file=feature_model_file,
                                                     maltparser_dir=maltparser_dir,
                                                     maltparser_jar=maltparser_jar)
                                elif parser == 'udpipe1':
                                    cur_embeddings_file = create_embeddings_file
                                    if cur_embeddings_file is not None:
                                        cur_embeddings_file = f'{cur_subexp}_{cur_embeddings_file}'
                                    train_udpipe1(output_model_file, train_file, output_model_dir, 
                                                  parser_options=parser_options, 
                                                  create_embeddings_file=cur_embeddings_file,
                                                  udpipe_dir=udpipe_dir)
                                else:
                                    raise Exception(f'Unexpected parser name: {parser!r}')
    if not section_found:
        print(f'No section starting with "train_malt_" or "train_udpipe1_" in {conf_file}.')

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
#  Train MaltParser
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

def train_maltparser(output_model, train_corpus, output_dir=None, final_options_file=None, feature_model_file=None,
                     maltparser_dir=DEFAULT_MALTPARSER_DIR, maltparser_jar=DEFAULT_MALTPARSER_JAR):
    '''
    Trains MaltParser on train_corpus, creates output_model and saves into output_dir.
    Optionally, uses final_options_file and feature_model_file for feature selection.
    '''
    check_maltparser_requirements(maltparser_dir=maltparser_dir, maltparser_jar=maltparser_jar)
    # Make input file paths absolute
    if train_corpus != os.path.abspath(train_corpus):
        train_corpus = os.path.abspath(train_corpus)
    if final_options_file is not None and final_options_file != os.path.abspath(final_options_file):
        final_options_file = os.path.abspath(final_options_file)
    if feature_model_file is not None and feature_model_file != os.path.abspath(feature_model_file):
        feature_model_file = os.path.abspath(feature_model_file)
    # Construct command
    if final_options_file is not None and feature_model_file is not None:
        train_command = \
            ('java -Xmx6g  -jar {jar} -i {train_corpus} -c {output_model} -m learn -f {final_options_file} -F {feature_model_file}').\
                format(jar=maltparser_jar, output_model=output_model, train_corpus=train_corpus, 
                       final_options_file=final_options_file, feature_model_file=feature_model_file)
    else:
        train_command = \
            ('java -Xmx6g  -jar {jar} -i {train_corpus} -c {output_model} -m learn').\
                format(jar=maltparser_jar, train_corpus=train_corpus, output_model=output_model)
    # Execute training
    subprocess.call(train_command, shell=True, cwd=maltparser_dir)
    if output_dir is not None:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        # Remove old file
        if os.path.exists(os.path.join(output_dir, output_model)):
            os.remove(os.path.join(output_dir, output_model))
        # Move model file to output dir
        os.rename(os.path.join(maltparser_dir, output_model), 
                  os.path.join(output_dir, output_model))


# ===============================================================
#  Train UDPipe-1 (preprocessing)
# ===============================================================

def is_gensim_available():
    """
    Checks if the package gensim is available. 
    This is required for creating word2vec embeddings for gensim. 
    """
    return pkgutil.find_loader('gensim') is not None

def load_conllu_tokens_sentences(input_conllu):
    '''
    Loads conllu file's textual content.
    Returns a list of lists: sentences of tokens.
    '''
    sentences = []
    with open(input_conllu, 'r', encoding='utf-8') as conllu_file:
        for sentence in parse_incr(conllu_file):
            sentences.append([])
            for i, token in enumerate(sentence):
                sentences[-1].append(token['form'])
    return sentences

def create_word2vec_model(input_conllu, output_path):
    '''
    Trains word2vec embeddings file for UDPipe-1.
    Saves text format model to output_path.
    '''
    if not is_gensim_available():
        raise Exception('(!) Package gensim is required for pre-training embeddings for udpipe. '+\
                        'Get the package from here: https://radimrehurek.com/gensim/ ')
    import gensim.models
    sentences = load_conllu_tokens_sentences(input_conllu)
    # Following pre-training settings mentioned here:
    # https://ufal.mff.cuni.cz/udpipe/1/users-manual#udpipe_training_parser_embeddings
    model = gensim.models.Word2Vec( 
        sentences=sentences,
        min_count=2,
        vector_size=50,
        window=10,
        hs=0,
        sg=1, # skip-gram
        sample=1e-3,
        epochs=15,
        negative=5
    )
    model.wv.save_word2vec_format(output_path, binary=False)

# ===============================================================
#  Train UDPipe-1
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

def train_udpipe1(output_model, train_corpus, output_dir, parser_options=None, create_embeddings_file=None, verbose=True,
                  udpipe_dir=DEFAULT_UDPIPE_DIR):
    '''
    Trains UDPipe-1 on train_corpus, creates output_model and saves into output_dir. 
    List of parser options can be provided via string parser_options.
    If create_embeddings_file is not None, then creates word2vec form embeddings from train_corpus 
    and saves into file named create_embeddings_file.
    
    Note: if parser_options is not provided, then UDPipe's default training options are:
    Parser transition options: system=projective, oracle=dynamic, structured_interval=8, single_root=1
    Parser uses lemmas/upos/xpos/feats: from gold data
    Parser embeddings options: upostag=20, feats=20, xpostag=0, form=50, lemma=0, deprel=20
      form mincount=2, precomputed form embeddings=none
      lemma mincount=2, precomputed lemma embeddings=none
    Parser network options: iterations=10, hidden_layer=200, batch_size=10,
      learning_rate=0.0200, learning_rate_final=0.0010, l2=0.5000, early_stopping=0
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
    embeddings_path = None
    if create_embeddings_file is not None:
        embeddings_path = os.path.join(output_dir, create_embeddings_file)
        if verbose:
            print(f'Creating word2vec embeddings file {create_embeddings_file} ...')
        create_word2vec_model(train_corpus, embeddings_path)
    output_model_path = os.path.join(output_dir, output_model)
    if parser_options is None:
        parser_options = 'use_gold_tags=1'
    else:
        if 'use_gold_tags=1' not in parser_options:
            parser_options += ';use_gold_tags=1'
    if embeddings_path is not None:
        if 'embedding_form_file=' not in parser_options:
            parser_options += f';embedding_form_file={embeddings_path}'
        else:
            # Updated from embeddings file path
            parser_options = re.sub(r';embedding_form_file=([^; ])+',
                                    f';embedding_form_file={embeddings_path}', 
                                    parser_options)
    if verbose:
        print(f' Training UDPipe-1 on {train_corpus!r} with settings {parser_options!r} ...')
    udpipe_cmd = 'udpipe'
    if udpipe_dir_exists:
        udpipe_cmd = os.path.join(udpipe_dir, udpipe_cmd)
    # Linux shell note: parser_options must be surrounded by ' and ', otherwise udpipe is unable 
    # to parse them and hangs while waiting for training input.
    train_command = \
        ('{udpipe_cmd} --train {output_model_path} --tokenizer=none --tagger=none --parser={parser_options!r} {train_corpus}').\
            format(udpipe_cmd=udpipe_cmd, output_model_path=output_model_path, parser_options=parser_options, 
                   train_corpus=train_corpus)
    # Execute training
    subprocess.call(train_command, shell=True)



if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    subexp=None
    if len(sys.argv) > 2:
        subexp = sys.argv[2]
    # Try to execute input file as configuration
    train_malt_udpipe_main( sys.argv[1], subexp=subexp, dry_run=False )