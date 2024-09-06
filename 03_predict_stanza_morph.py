#
#    Executes stanza's morphology models for prediction based on 
#    the given configuration.
#    
#    Supported models:
#       * stanza's tagger (POS/morphological features tagger);
#       * stanza's lemmatizer;
#    Implemented settings:
#       * full_data
#
import os
import os.path
import sys
import re
import argparse
from datetime import datetime

from conllu import parse_incr
from conllu.serializer import serialize_field

from stanza import Pipeline
from stanza.models.common.doc import Document
from stanza.utils.conll import CoNLL

import configparser

# ===============================================================
#  Train Stanza for tagging morphological features (MAIN)
# ===============================================================

def predict_stanza_morph_main( conf_file, dry_run=False ):
    '''
    Executes stanza's morphological tagging models for predictions 
    based on the given configuration. 
    Settings/parameters of the training/prediction will be read from 
    the given `conf_file`. 
    Executes sections in the configuration starting with prefix 
    'predict_morph_feats_stanza_'.
    '''
    # Parse configuration file
    config = configparser.ConfigParser()
    if conf_file is None or not os.path.exists(conf_file):
        raise FileNotFoundError("Config file {} does not exist".format(conf_file))
    if len(config.read(conf_file)) != 1:
        raise ValueError("File {} is not accessible or is not in valid INI format".format(conf_file))
    section_found = False
    for section in config.sections():
        # -----------------------------------------------------
        #  precit  stanza  lemmatizer & morphological  tagger
        # -----------------------------------------------------
        if section.startswith('predict_morph_feats_stanza_'):
            section_found = True
            print(f'Running {section} ...')
            # ------------------------------------------
            # 'full_data'
            # ------------------------------------------
            # skip_train: do not predict on train files
            skip_train = config[section].getboolean('skip_train', False)
            # train_file with path
            train_file = None
            if not skip_train:
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
            dry_run = config[section].getboolean('dry_run', dry_run)
            use_gpu = config[section].getboolean('use_gpu', False)
            output_prefix = config[section].get('output_file_prefix', 'morph_predicted_')
            lang = config[section].get('lang', 'et')
            # predict with a single model: get models file with paths
            lemmatizer_model_file = config[section].get('lemmatizer_model_file', None)
            morph_tagger_model_file = config[section].get('morph_tagger_model_file', None)
            # or, alternatively, download stanza's models
            download_models = config[section].getboolean('download_models', False)
            if lemmatizer_model_file is None and morph_tagger_model_file is None and not download_models:
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing parameters '+\
                                 '"lemmatizer_model_file" and "morph_tagger_model_file". At least one '+\
                                 'of these parameters must be defined.')
            if lemmatizer_model_file is not None and not os.path.isfile( lemmatizer_model_file ):
                raise FileNotFoundError(f'Error in {conf_file}: invalid "lemmatizer_model_file" value '+\
                                        f'{lemmatizer_model_file!r} in {section!r}. ')
            if morph_tagger_model_file is not None and not os.path.isfile( morph_tagger_model_file ):
                raise FileNotFoundError(f'Error in {conf_file}: invalid "morph_tagger_model_file" value '+\
                                        f'{morph_tagger_model_file!r} in {section!r}. ')
            if not dry_run:
                start_time = datetime.now()
                # Predict on train
                if not skip_train:
                    train_path, train_file_name = os.path.split(train_file) 
                    train_output = os.path.join(output_dir, f'{output_prefix}{train_file_name}')
                    predict_with_stanza_pipeline(train_file, lemmatizer_model_file, morph_tagger_model_file, 
                                                 train_output, download_models=download_models, lang=lang, 
                                                 use_gpu=use_gpu)
                # Predict on test
                test_path, test_file_name = os.path.split(test_file) 
                test_output = os.path.join(output_dir, f'{output_prefix}{test_file_name}')
                predict_with_stanza_pipeline(test_file, lemmatizer_model_file, morph_tagger_model_file, 
                                             test_output, download_models=download_models, lang=lang, 
                                             use_gpu=use_gpu)
                print()
                print(f'Total time elapsed: {datetime.now()-start_time}')

    if not section_found:
        print(f'No section starting with "predict_morph_feats_stanza_" in {conf_file}.')


# ========================================================================
#  Stanza predictions: use pipeline to predict both lemmas & morph feats  
# ========================================================================

def create_stanza_document(input_path, mask_morph_feats=True):
    """
    Loads sentences from given CONLLU file and creates stanza's Document. 
    Document will be pretagged: it contains id, text, lemma, upos, xpos, 
    feats values loaded from the CONLLU file, and empty values in place 
    of other conllu fields. 
    Returns loaded Document.
    
    :param input_path: path to conllu file to be loaded
    :param mask_morph_feats: if set (default), then masks all 
           morphological features in the document with '---'. 
    :return: stanza Document
    """
    with open(input_path, 'r', encoding='utf-8') as conllu_file:
        data = []
        for tokenlist in parse_incr(conllu_file):
            pretagged_sent = []
            for word in tokenlist:
                if not isinstance(word['id'], int):
                    # Because stanza cannot handle ellipsis (considers it 
                    # a multi-word), we leave ellipsis word out
                    continue
                word_feats = {
                    'id': word['id'],
                    'text': word['form'],
                    'lemma': word['lemma'],
                    'upos': word['upos'],
                    'xpos': word['xpos'],
                    'feats': serialize_field( word['feats'] ),
                    # Carry over gold standard head & deprel
                    'head': word['head'],
                    'deprel': word['deprel']
                }
                if mask_morph_feats:
                    word_feats['lemma'] = '_'
                    word_feats['upos'] = '---'
                    word_feats['xpos'] = '---'
                    word_feats['feats'] = serialize_field( '_' )
                pretagged_sent.append(word_feats)
            data.append(pretagged_sent)
    # create Document-obj from sentences of the pretagged file
    return Document(data)

def predict_with_stanza_pipeline(input_path, lemmatizer_model_path, morph_tagger_model_path, 
                                 output_path, download_models=False, lang='et', use_gpu=False):
    '''
    Applies stanza's lemmatizer_model/morph_tagger_model on given input CONLLU file to 
    get depparse predictions. Alternatively, uses lemmatizer/morph_tagger_model downloaded 
    from stanza's resources for predictions. 
    Saves predictions to output CONLLU file.
    
    :param input_path:  path to conllu file to be annotated
    :param lemmatizer_model_path:  path to lemmatizer model to be used for predictions
    :param morph_tagger_model_path:  path to tagger model to be used for predictions
    :param output_path: path to output conllu file
    :param download_models: whether models should be downloaded instead of using existing ones
    '''
    if morph_tagger_model_path is None and lemmatizer_model_path is None and not download_models:
        raise ValueError('(!) At least one of the model paths lemmatizer_model_path and '+\
                         'morph_tagger_model_path must be provided.')
    elif (morph_tagger_model_path is not None or lemmatizer_model_path is not None) and download_models:
        raise ValueError('(!) Conflicting parameters: cannot use morph_tagger_model_path or '+\
                         'lemmatizer_model_path if download_models is switched on. ')
    processors = []
    if morph_tagger_model_path is not None:
        processors.append('pos')
    if lemmatizer_model_path is not None:
        processors.append('lemma')
    if download_models:
        processors = ['pos', 'lemma']
    config = {
        'processors': 'tokenize,'+(','.join(processors)),  # Comma-separated list of processors to use
        'lang': lang,  # Language code for the language to build the Pipeline in
        'use_gpu': use_gpu
    }
    if not download_models:
        # Use existing models, do not download anything
        config['download_method'] = 0  # NONE won't download anything
        if morph_tagger_model_path is not None:
            config['pos_model_path'] = morph_tagger_model_path
        if lemmatizer_model_path is not None:
            config['lemma_model_path'] = lemmatizer_model_path
    # Note: "tokenize" is listed in 'processors' because its is 
    # mandatory for lemma/pos. However, we don't want to use it. 
    # Use pretokenized text as input and disable tokenization 
    config['tokenize_pretokenized'] = True
    nlp = Pipeline(**config)
    doc = create_stanza_document(input_path, mask_morph_feats=True)
    nlp(doc)
    output_dir, output_fname = os.path.split(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    write_stanza_doc_to_conll(doc, output_path)

def write_stanza_doc_to_conll(doc, output_path):
    '''Writes given stanza Document to CoNLLU format output file.'''
    conll = CoNLL.convert_dict(doc.to_dict())
    with open(output_path, 'w', encoding='utf-8') as fout:
        for sentence in conll:
            for word in sentence:
                fout.write('\t'.join(word) + '\n')
            fout.write('\n')
        fout.write('\n' * 2)

# ========================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    conf_file = sys.argv[1]
    predict_stanza_morph_main( conf_file )