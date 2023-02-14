#
#   Gap experiments: delete systematically conllu fields 
#   form, lemma and upos.
#
#   Implemented conllu file modifications:
#
#   '01_no_wordforms'                    -- remove 'form' of every word;
#   '02_no_lemmas'                       -- remove 'lemma' of every word;
#   '02_no_pos'                          -- remove 'upos' and 'xpos' of every word;
#   '03_no_adj_noun_lemmas'              -- remove 'lemma' if a word is noun or adj;
#   '03_no_wordforms_adj_noun_lemmas'    -- remove 'form' of every word, and remove 'lemma' if a word is noun or adj;
#   '04_no_verb_adpos_lemmas'            -- remove 'lemma' if a word is verb or adposition;
#   '04_no_wordforms_verb_adpos_lemmas'  -- remove 'form' of every word, and remove 'lemma' if a word is verb or adposition;
#   '05_only_cg_list_wordforms_lemmas'   -- remove 'form' of every word, and remove 'lemma' if a word is not in CG lemmas list;
#   '06_no_wordform_lemma_pos_keep_conj' -- remove 'form', 'lemma' and 'upos'/'xpos' of word if word is no conjunction;
#   '07_no_wordform_lemma_pos'           -- remove 'form', 'lemma' and 'upos'/'xpos' of every word;
#   '08_only_wordforms'                  -- keep only 'form' and remove 'lemma', 'upos'/'xpos', 'feats';
#   '09_only_pos_feats'                  -- keep only 'upos', 'xpos', and 'feats' and remove 'form' and 'lemma';
#

from datetime import datetime
import os, os.path
import sys, re

import configparser
import warnings

from conllu import parse_incr

gap_experiment_names = [ \
 '01_no_wordforms',
 '02_no_lemmas',
 '02_no_pos',
 '03_no_adj_noun_lemmas', 
 '03_no_wordforms_adj_noun_lemmas', 
 '04_no_verb_adpos_lemmas', 
 '04_no_wordforms_verb_adpos_lemmas', 
 '05_only_cg_list_wordforms_lemmas', 
 '06_no_wordform_lemma_pos_keep_conj', 
 '07_no_wordform_lemma_pos', 
 '08_only_wordforms', 
 '09_only_pos_feats', 
]

def perform_gap_experiment_modifications( conf_file ):
    '''
    Modifies conllu files for gap experiments based on the configuration. 
    Settings/parameters of modifications will be read from the given 
    `conf_file`. 
    Executes sections in the configuration starting with prefix 
    'modify_conllu_'. 
    '''
    # Parse configuration file
    config = configparser.ConfigParser()
    if conf_file is None or not os.path.exists(conf_file):
        raise FileNotFoundError("Config file {} does not exist".format(conf_file))
    if len(config.read(conf_file)) != 1:
        raise ValueError("File {} is not accessible or is not in valid INI format".format(conf_file))
    section_found = False
    for section in config.sections():
        if section.startswith('modify_conllu_'):
            section_found = True
            print(f'Performing {section} ...')
            # Collect conllu modification parameters
            if not config.has_option(section, 'input_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_dir" parameter.')
            input_dir = config[section]['input_dir']
            if not os.path.isdir(input_dir):
                raise FileNotFoundError(f'Error in {conf_file}: invalid "input_dir" value {input_dir!r} in {section!r}.')
            if not config.has_option(section, 'output_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
            output_dir = config[section]['output_dir']
            if not config.has_option(section, 'gap_experiments'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "gap_experiments" parameter.')
            gap_experiments_str = config[section]['gap_experiments']
            collected_gap_experiments = []
            for gap_exp in gap_experiments_str.split(','):
                gap_exp_norm = (gap_exp.strip()).lower()
                if gap_exp_norm not in gap_experiment_names:
                    raise ValueError( f'Error in {conf_file} section {section!r} parameter "gap_experiments": '+\
                                      f'unknown gap experiment name: {gap_exp!r}. \n'+\
                                      f'Legal names are: {gap_experiment_names}' )
                collected_gap_experiments.append( gap_exp_norm )
            if len(collected_gap_experiments) == 0:
                raise ValueError( f'Error in {conf_file} section {section!r} parameter "gap_experiments": '+\
                                  f'no gap experiment names found from the variable. \n'+\
                                  f'Legal names are: {gap_experiment_names}' )
            conll_file_pat=None
            # Customize sub-experiment pattern (if required)
            if config.has_option(section, 'conll_file_pat'):
                conll_file_pat = config[section]['conll_file_pat']
            suppress_checks = config[section].getboolean('suppress_checks', False)
            # Perform file modifications
            modify_directory( input_dir, output_dir, collected_gap_experiments, 
                              conll_file_pat=conll_file_pat,
                              suppress_checks=suppress_checks )
    if not section_found:
        print(f'No section starting with "modify_conllu_" in {conf_file}.')


def modify_directory( in_dir, out_dir, gap_experiments, conll_file_pat=None, skip_files=['train_full.conllu'], suppress_checks=False ):
    '''
    Iteratively processes all train/test/dev conllu files from in_dir, performing all 
    modifications listed in gap_experiments. Saves modified files into out_dir.
    
    If in_dir contains files of multiple sub experiments, conll_file_pat should be a 
    regular expression that matches generalizes file name over all sub experiments, and 
    allows to extract sub experiment name (the regex should have a named group 'exp', 
    capturing the name of the sub experiment).
    
    Note that for each sub experiment, there can be only 1 train, 1 test and 1 dev 
    conllu file. If there are multiple candidate files (and suppress_checks==True), 
    then an exception will be raised. 
    However, you can use suppress_checks=False to disable the exception rising 
    behaviour, or alternatively, provide list of skip_files with the names of 
    files to be skipped from modifications.
    '''
    start_time = datetime.now()
    # If conll_file_pat is given, try to convert it to regular expression
    conll_file_regexp = None
    if conll_file_pat is not None:
        # Convert file pattern to regular experssion
        if not isinstance(conll_file_pat, str):
            raise TypeError(f'conll_file_pat must be a string')
        try:
            conll_file_regexp = re.compile(conll_file_pat)
        except Exception as err:
            raise ValueError(f'Unable to convert {conll_file_pat!r} to regexp') from err
        if 'exp' not in conll_file_regexp.groupindex:
            raise ValueError(f'Regexp {conll_file_pat!r} is missing named group "exp"')
    # Collect conllu files from input dir
    input_files = []
    for fname in sorted(os.listdir( in_dir )):
        if (fname.lower()) in skip_files:
            continue
        if (fname.lower()).endswith('.conllu'):
            # Check conllu file pattern (if required)
            sub_exp = None
            if conll_file_regexp is not None:
                m = conll_file_regexp.match( fname )
                if m:
                    sub_exp = m.group('exp')
                else:
                    # Skip file if it does not match the pattern
                    continue
            # Determine file type: (train_all,) train, dev or test
            cur_ftype = None
            for f_type in ['train_all', 'train', 'dev', 'test']:
                if f_type in fname.lower():
                    cur_ftype = f_type
                    break
            if cur_ftype is None:
                warnings.warn(f'(!) Could not determine if {fname!r} is train, dev or test file. '+
                               'Skipping file')
                continue
            fpath = os.path.join( in_dir, fname )
            input_files.append( (cur_ftype, fpath, sub_exp) )
    if len(input_files) == 0:
        raise FileNotFoundError(f'(!) No suitable conllu files found from directory {in_dir!r}.')
    # Validate that there is an equal number of files in each sub set
    if not suppress_checks:
        dev_files   = [in_file for in_type, in_file, sub_exp in input_files if in_type == 'dev']
        test_files  = [in_file for in_type, in_file, sub_exp in input_files if in_type == 'test']
        train_files = [in_file for in_type, in_file, sub_exp in input_files if in_type == 'train']
        if len(dev_files) != len(train_files):
            raise Exception( f'(!) Number of collected train files does not match with the number of '+\
                             f'dev files. train_files: {train_files!r} vs dev_files: {dev_files!r}. '+\
                              'Please make sure there is equal number of train, dev and test files for '+\
                              'each experiment.' )
        if len(test_files) != len(train_files):
            raise Exception( f'(!) Number of collected train files does not match with the number of '+\
                             f'test files. train_files: {train_files!r} vs test_files: {test_files!r}. '+\
                             'Please make sure there is equal number of train, dev and test files for '+\
                             'each experiment.' )
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    cg_lemmas_set = None
    if '05_only_cg_list_wordforms_lemmas' in gap_experiments:
        cg_lemmas_set = load_cg_list()
        print(f' Loaded {len(cg_lemmas_set)} EstCG lemmas.')
    for exp_name in gap_experiments:
        exp_name = exp_name.lower()
        for in_type, in_file, sub_exp in input_files:
            subset_name = ''
            # Try to fetch subset name, if corresponding pattern is defined
            if conll_file_regexp is not None:
                in_path, fname = os.path.split(in_file)
                m = conll_file_regexp.match(fname)
                if m:
                    subset_name = m.group('exp')
                    if not subset_name.endswith('_'):
                        subset_name = subset_name + '_'
            out_file_temp = os.path.join( out_dir, f'{exp_name}_{subset_name}{in_type}_temp.conllu' )
            out_file_final = os.path.join( out_dir, f'{exp_name}_{subset_name}{in_type}.conllu' )
            if exp_name == '01_no_wordforms':
                # gap_experiments/experiment_x/ -- kustuta kõik sõnavormid
                modify_file(in_file, out_file_final, remove_fields=['form'], token_picker=None, remove_meta=False)
            elif exp_name == '02_no_lemmas':
                # gap_experiments/experiment_2/ -- kustuta kõik lemmad
                modify_file(in_file, out_file_final, remove_fields=['lemma'], token_picker=None, remove_meta=False)
            elif exp_name == '02_no_pos':
                # gap_experiments/experiment_x/ -- kustuta kõik sõnaliigimärgendid
                modify_file(in_file, out_file_final, remove_fields=['upos', 'xpos'], token_picker=None, remove_meta=False)
            elif exp_name == '03_no_adj_noun_lemmas':
                # gap_experiments/experiment_3/ -- nimisõnade ja omadussõnade lemmad kustutatud
                modify_file(in_file, out_file_final, remove_fields=['lemma'], token_picker=lambda x: x['xpos'] in ['S', 'A'])
            elif exp_name == '03_no_wordforms_adj_noun_lemmas':
                # gap_experiments/experiment_3_2/ -- kõik sõnavormid ja nimisõnade, omadussõnade lemmad kustutatud
                modify_file(in_file,        out_file_temp, remove_fields=['form'], token_picker=None)
                modify_file(out_file_temp, out_file_final, remove_fields=['lemma'], token_picker=lambda x: x['xpos'] in ['S', 'A'])
                os.remove(out_file_temp) 
            elif exp_name == '04_no_verb_adpos_lemmas':
                # gap_experiments/experiment_4/ -- verbide ja kaassõnade lemmad kustutatud
                modify_file(in_file, out_file_final, remove_fields=['lemma'], token_picker=lambda x: x['xpos'] in ['V', 'K'])
            elif exp_name == '04_no_wordforms_verb_adpos_lemmas':
                # gap_experiments/experiment_4_2/ -- kõik sõnavormid + verbide ja kaassõnade lemmad kustutatud
                modify_file(in_file,        out_file_temp, remove_fields=['form'], token_picker=None)
                modify_file(out_file_temp, out_file_final, remove_fields=['lemma'], token_picker=lambda x: x['xpos'] in ['V', 'K'])
                os.remove(out_file_temp) 
            elif exp_name == '05_only_cg_list_wordforms_lemmas':
                # gap_experiments/experiment_5/ -- kõik sõnavormid + lemmad kustutatud, kui lemma pole CG listis
                modify_file(in_file,        out_file_temp, remove_fields=['form'], token_picker=None)
                modify_file(out_file_temp, out_file_final, remove_fields=['lemma'], token_picker=lambda x: not cg_lemma_match(x, cg_lemmas_set))
                os.remove(out_file_temp) 
            elif exp_name == '06_no_wordform_lemma_pos_keep_conj':
                # gap_experiments/experiment_conjunction/ -- kustuta sõnavorm & lemma & upos, kui pole tegemist sidesõnaga
                modify_file(in_file, out_file_final, remove_fields=['form', 'lemma', 'upos', 'xpos'], token_picker=lambda x: x['xpos'] not in ['J'])
            elif exp_name == '07_no_wordform_lemma_pos':
                # POS+MORPH experiments -- kustuta igalt poolt sõnavorm & lemma & upos (maksimaalne kustutamine)
                modify_file(in_file, out_file_final, remove_fields=['form', 'lemma', 'upos', 'xpos'], token_picker=None)
            elif exp_name == '08_only_wordforms':
                # Keep only 'form' and remove 'lemma', 'upos'/'xpos', 'feats';
                modify_file(in_file, out_file_final, remove_fields=['lemma', 'upos', 'xpos', 'feats'], token_picker=None)
            elif exp_name == '09_only_pos_feats':
                # Keep only 'upos', 'xpos', and 'feats' and remove 'form' and 'lemma';
                modify_file(in_file, out_file_final, remove_fields=['form', 'lemma'], token_picker=None)
            else:
                warnings.warn(f'(!) Unknown gap experiment {exp_name!r}. Skipping that modification step.')
    print(f'Total time elapsed: {datetime.now()-start_time}')


def load_cg_list( in_file='visl_lemmas.txt', clean_lemmas=True, return_set=True ):
    '''
    Loads list of lemmas that were used in the EstCG syntax from in_file.
    Cleans the list: removes lemmas that are likely regular expression patterns, 
    and if clean_lemmas==True, also deletes '=' and '_' symbols inside lemmas. 
    Returns a list of lemmas or set of lemmas if return_set==True.
    '''
    if not os.path.exists(in_file):
        raise FileNotFoundError(f'(!) Unable to find cg list file {in_file!r}')
    visl_regexes = []
    visl_lemmas_clean = []
    with open('visl_lemmas.txt', 'r', encoding='utf-8') as fin:
        lemmas_raw_all = fin.readlines()
        lemmas_raw = [l.strip() for l in lemmas_raw_all]
        for l in lemmas_raw:
            if re.search('[^-a-züõöäÜÕÖÄšžŽŠA-Z=_]', l):
                visl_regexes.append(l)
            else:
                if clean_lemmas:
                    # Remove _ & =
                    l = (l.replace('_', '')).replace('=', '')
                visl_lemmas_clean.append(l)
    return visl_lemmas_clean if not return_set else set(visl_lemmas_clean)


def cg_lemma_match( candidate_token, cg_lemmas_set ):
    '''
    Determines if lemma of the candidate_token is in cg_lemmas_set.
    If the token is verb and ends with 'ma', then also tries to 
    find lemma with stripped-off 'ma' ending from the cg_lemmas_set 
    (because verb lemmas in cg_lemmas_set may or may not have the 
    'ma' ending -- the listing is not systematic).
    '''
    candidate_lemma = candidate_token['lemma']
    candidate_pos = candidate_token['xpos']
    if candidate_lemma.endswith('ma') and candidate_pos == 'V':
        # If candidate is verb, try to match without 'ma' ending
        candidate_lemma_stripped = re.sub('ma$', '', candidate_lemma)
        return candidate_lemma in cg_lemmas_set or \
                candidate_lemma_stripped in cg_lemmas_set
    else:
        return candidate_lemma in cg_lemmas_set


def modify_file( in_file, output_file, remove_fields=[], token_picker=None, remove_meta=False ):
    '''
    Modifies conllu in_file by removing specified fields. Optionally, if a token_picker (lambda 
    callable that should return a boolean) is defined, then removes fields only from tokens that 
    satisfy the token_picker.
    Saves modified file into output_file.
    '''
    if token_picker is not None:
        if not callable(token_picker):
            raise ValueError('(!) token_picker should be a function (callable) that '+\
                             'can be used for picking tokens for deletion.')
    with open(in_file, 'r', encoding='utf-8') as conllu_file:
        with open(output_file, 'w', encoding='utf-8') as fout:
            for sentence in parse_incr(conllu_file):
                if remove_meta:
                    sentence.metadata.pop('text')
                    sentence.metadata.pop('sent_id')
                    if 'newdoc id' in sentence.metadata:
                        sentence.metadata.pop('newdoc id')
                for i, token in enumerate(sentence):
                    if token_picker is not None:
                        if not token_picker(token):
                            # Skip this token
                            continue
                    for key in token.keys():
                        if key in remove_fields:
                            if key not in ['form', 'upos', 'xpos']:
                                token[key] = '_'
                            else:
                                # TODO: next time, use a token that does 
                                # not appear among punctuation tokens of 
                                # the corpus 
                                token[key] = '---'
                fout.write(sentence.serialize())

# ========================================================================

if __name__ == '__main__':
    #print ( load_cg_list() )
    
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    # Try to execute all input files as configurations
    for conf_file in sys.argv[1:]:
        perform_gap_experiment_modifications( conf_file )
