#
#  Convert gold standard UD corpus to training/experiments format:
#  1) EstNLTK's format: add EstNLTK's automatic morphological 
#     annotations to CONLL files;
#  2) UD format: clean annotations by removing null nodes,
#     deps and misc values (optional), and copy gold standard 
#     CONLL files to new location;
#

import re
import os
import os.path
import sys

from datetime import datetime
from random import Random
import configparser

import conllu

from estnltk import Text
from estnltk.taggers import Tagger
from estnltk.taggers import VabamorfTagger
from estnltk.taggers import MorphExtendedTagger
from estnltk.taggers import WhiteSpaceTokensTagger
from estnltk.taggers import PretokenizedTextCompoundTokensTagger

from estnltk.converters.conll.conll_importer import conll_to_text

# ===============================================================
#  Convert UD corpora to training/experiments format: 
#  1) EstNLTK's format: add EstNLTK's morphological annotations;
#  2) UD format: clean annotations by removing null nodes,
#     deps and misc values;
#   (MAIN)
# ===============================================================

def convert_to_estnltk_conllu_main( conf_file, verbose=True ):
    '''
    Converts gold standard CONLL-U files to training/experiments format. 
    Settings/parameters of the conversion will be read from the given 
    `conf_file`. 
    Executes sections in the configuration starting with prefix 'preannotation_' 
    (add EstNLTK's morphological annotations) and 'copy_' (clean and copy files 
    with UD annotations). 
    See functions `convert_ud_conllu_to_estnltk_conllu(...)` and 
    `copy_and_clean_ud_conllu(...)` for details about the conversion 
    and possible parameters. 
    '''
    # Parse configuration file
    config = configparser.ConfigParser()
    if conf_file is None or not os.path.exists(conf_file):
        raise FileNotFoundError("Config file {} does not exist".format(conf_file))
    if len(config.read(conf_file)) != 1:
        raise ValueError("File {} is not accessible or is not in valid INI format".format(conf_file))
    morph_pipeline = [ WhiteSpaceTokensTagger(), 
                       PretokenizedTextCompoundTokensTagger(), 
                       VabamorfTagger(use_reorderer=True), 
                       MorphExtendedTagger() ]
    start = datetime.now()
    section_found = False
    for section in config.sections():
        if section.startswith('preannotation_'):
            # Load preannotation configuration from the section
            if not config.has_option(section, 'input_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_dir" parameter.')
            input_dir = config[section]['input_dir']
            if not os.path.isdir(input_dir):
                raise FileNotFoundError(f'Error in {conf_file}: invalid "input_dir" value {input_dir!r} in {section!r}.')
            if not config.has_option(section, 'morph_layer'):
                raise ValueError(f'Error in {conf_file}: section {section} is missing "morph_layer" parameter.')
            morph_layer = config[section]['morph_layer']
            if morph_layer == 'ud_morph_analysis':
                # Add UDMorphConverter() to disambiguated morph
                from estnltk.taggers import UDMorphConverter  # requires estnltk 1.7.2+
                morph_pipeline.append( UDMorphConverter() )
            if not config.has_option(section, 'output_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
            output_dir = config[section]['output_dir']
            seed = config[section].getint('seed', 43)
            dictionarize = config[section].getboolean('dictionarize', True)
            remove_empty_nodes = config[section].getboolean('remove_empty_nodes', True)
            remove_deps = config[section].getboolean('remove_deps', True)
            remove_misc = config[section].getboolean('remove_misc', True)
            replace_lemma_by_root = config[section].getboolean('replace_lemma_by_root', False)
            remove_metadata = config[section].getboolean('remove_metadata', False)
            # Collect input files. Make possible output files and dir
            input_files = []
            output_files = []
            for fname in os.listdir(input_dir):
                if fname.endswith('.conllu'):
                    input_files.append(os.path.join(input_dir, fname))
                    out_fname = fname.replace('.conllu', f'-{morph_layer}.conllu')
                    output_files.append(os.path.join(output_dir, out_fname))
            if not input_files:
                raise Exception(f'(!) No conllu files found from "input_dir" {input_dir!r}.')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            # Convert files
            for in_file, out_file in zip(input_files, output_files):
                if verbose:
                    print(f'Reannotating {in_file} with layer {morph_layer} ...')
                convert_ud_conllu_to_estnltk_conllu( in_file, morph_pipeline, morph_layer, out_file,
                                                     dictionarize=dictionarize, 
                                                     replace_lemma_by_root=replace_lemma_by_root, 
                                                     remove_empty_nodes=remove_empty_nodes, 
                                                     remove_metadata=remove_metadata, 
                                                     remove_deps=remove_deps, 
                                                     remove_misc=remove_misc, 
                                                     seed=seed )
            section_found = True
        if section.startswith('copy_'):
            # Load copying configuration from the section
            if not config.has_option(section, 'input_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_dir" parameter.')
            input_dir = config[section]['input_dir']
            if not os.path.isdir(input_dir):
                raise FileNotFoundError(f'Error in {conf_file}: invalid "input_dir" value {input_dir!r} in {section!r}.')
            if not config.has_option(section, 'output_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
            output_dir = config[section]['output_dir']
            remove_empty_nodes = config[section].getboolean('remove_empty_nodes', True)
            remove_deps = config[section].getboolean('remove_deps', True)
            remove_misc = config[section].getboolean('remove_misc', True)
            remove_metadata = config[section].getboolean('remove_metadata', False)
            # Collect input files. Make possible output files and dir
            input_files = []
            output_files = []
            for fname in os.listdir(input_dir):
                if fname.endswith('.conllu'):
                    input_files.append(os.path.join(input_dir, fname))
                    output_files.append(os.path.join(output_dir, fname))
            if not input_files:
                raise Exception(f'(!) No conllu files found from "input_dir" {input_dir!r}.')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            # Copy & clean files
            for in_file, out_file in zip(input_files, output_files):
                if verbose:
                    print(f'Copying & cleaning {in_file} ...')
                copy_and_clean_ud_conllu( in_file, out_file,
                                          remove_empty_nodes=remove_empty_nodes, 
                                          remove_deps=remove_deps, 
                                          remove_metadata=remove_metadata, 
                                          remove_misc=remove_misc )
            section_found = True
    if section_found:
        print(f'Total processing time: {datetime.now()-start}')
    else:
        print(f'No section starting with "preannotation_" or "copy_" in {conf_file}.')


def convert_ud_conllu_to_estnltk_conllu( in_file, morph_pipeline, morph_layer, out_file, 
                                         dictionarize=True, replace_lemma_by_root=False, 
                                         remove_empty_nodes=True, remove_metadata=False, 
                                         remove_deps=True, remove_misc=True, seed=43 ):
    '''
    Reannotates `in_file` with given `morph_pipeline` and saves results into `out_file`. 
    During reannotation, values of `lemma`, `upos`, `xpos` and `feats` will be replaced 
    with corresponding automatically tagged values from `morph_layer` (either morph_analysis 
    or morph_extended type of layer). In case of ambiguity, annotation is chosen randomly. 
    Use `seed` to provide seed value for random choices. 
    `morph_pipeline` must be a list of taggers that can be applied on the `Text` object 
    loaded from `in_file`. Both `in_file` and `out_file` are CONLL-U format files. 
    
    Requires EstNLTK version 1.7.2+.

    Parameters
    -----------
    in_file
        name/path of the CONLL-U format input file.
    morph_pipeline
        list of `Tagger`-s (in the order of layer dependencies) that can be applied 
        on the `Text` object loaded from `in_file`.
        this pipeline should produce `morph_layer`, which is used to reannotate 
        the input file.
    morph_layer
        morphological annotations layer (either morph_analysis or morph_extended 
        type of layer) produced by `morph_pipeline`. 
        Values from this layer are used to reannotate values of `upos`, `xpos` 
        and `feats` in the input file.
    out_file
        name/path of the CONLL-U format output file.
    dictionarize
        If True (default), then values of `feats` will be converted to a dictionary of 
        features. 
    replace_lemma_by_root
        If True, then lemmas will be replaced by root values from morph_analysis layer. 
        Default: False.
    remove_metadata:
        If True, then sentence metadata will be removed from the output conllu file. 
        This might be necessary if you want to create data for legacy parsers such as 
        MaltParser.
        Default: False.
    remove_empty_nodes
        If True (default), then null / empty nodes (of the enhanced representation) will 
        be removed from the output.
    remove_deps
        If True (default), then values of `deps` field will be replaced with `_`.
    remove_misc
        If True (default), then values of `misc` field will be replaced with `_`.
    '''
    # Validate input pipeline
    assert isinstance(morph_pipeline, list)
    assert isinstance(morph_layer, str)
    has_morph_layer = False
    for tagger in morph_pipeline:
        assert isinstance(tagger, Tagger)
        if morph_layer == tagger.output_layer:
            has_morph_layer = True
    if not has_morph_layer:
        raise Exception(('(!) No tagger in the input pipeline {!r} creates '+\
                         'required layer {!r}.'.format(morph_pipeline, morph_layer)))
    # Import text from conllu
    with open(in_file, 'r', encoding='utf-8') as input_file:
        conll_sentences = conllu.parse(input_file.read())
    text_obj = conll_to_text(in_file, remove_empty_nodes=remove_empty_nodes)
    assert len(text_obj['sentences']) == len(conll_sentences), \
        ('(!) Mismatching sentence numbers in estnltk import ({})'+\
         ' and conllu import ({}).').format( len(text_obj['sentences']), \
                                             len(conll_sentences) )
    # Annotate text
    for tagger in morph_pipeline:
        tagger.tag( text_obj )
    # If required, remove orphans / null nodes
    if remove_empty_nodes:
        token_count = 0
        for sid, sentence in enumerate(conll_sentences):
            removables = []
            for tid, token in enumerate(sentence):
                token_id = token['id']
                if isinstance(token_id, tuple) and len(token_id) == 3 and token_id[1] == '.':
                    removables.append(token)
            if removables:
                for token in removables:
                    sentence.remove(token)
            token_count += len(sentence)
        assert token_count == len(text_obj[morph_layer]), \
            f'(!) Token count mismatch: tokens from CONLL file: {token_count} '+\
            f'vs tokens from EstNLTK annotated text: {len(text_obj[morph_layer])}.'
    # Carry annotations over to TokenList-s
    word_id = 0
    # In case of an ambiguity, pick random analysis.
    # Fix seed for repeatability
    rand = Random()
    rand.seed( seed )
    for sid, sentence in enumerate(conll_sentences):
        for tid, token in enumerate(sentence):
            word_span = text_obj[morph_layer][word_id]
            assert word_span.text == token["form"]
            annotation = rand.choice(word_span.annotations)
            if morph_layer in ['morph_analysis', 'morph_extended']:
                token['upos']  = annotation['partofspeech']
                token['xpos']  = annotation['partofspeech']
                token['feats'] = annotation['form']
                token['lemma'] = annotation['lemma']
                if replace_lemma_by_root:
                    if 'root' in annotation:
                        token['lemma'] = annotation['root']
                    else:
                        # Find the same analysis from morph_analysis layer
                        # Get lemma from there
                        word_span2 = text_obj['morph_analysis'][word_id]
                        for annotation2 in word_span2.annotations:
                            if annotation2['lemma'] == annotation['lemma'] and \
                               annotation2['partofspeech'] == annotation['partofspeech']:
                                token['lemma'] = annotation2['root']
                                break
                # ? Override random pos with first pos (seems to be more accurate ?)
                #token['upos'] = word_span.annotations[0]['partofspeech']
                #token['xpos'] = word_span.annotations[0]['partofspeech']
                if dictionarize:
                    # Format form as a dictionary
                    form_parts = annotation['form'].split()
                    token['feats'] = {f:f for f in form_parts}
            elif morph_layer == 'ud_morph_analysis':
                token['upos']  = annotation['upostag']
                token['xpos']  = annotation['xpostag']
                token['feats'] = annotation['feats']
                token['lemma'] = annotation['lemma']
            else:
                raise Exception(f'(!) Unexpected morph_layer: {morph_layer!r}')
            if len(token['feats']) == 0:
                token['feats'] = None
            if remove_misc and token['misc'] is not None:
                token['misc'] = None
            if remove_deps and token['deps'] is not None:
                token['deps'] = None
            word_id += 1
        #print(sentence.serialize())
        #print()
    # Export annotated file
    with open(out_file, 'w', encoding='utf-8') as out_file:
        for sentence in conll_sentences:
            if remove_metadata:
                sentence.metadata = None
            out_file.write( sentence.serialize() )


def copy_and_clean_ud_conllu( in_file, out_file, remove_empty_nodes=True, 
                              remove_metadata=False, remove_deps=True, remove_misc=True ):
    '''
    Cleans `in_file` by removing empty nodes, deps and misc attributes, and 
    saves result as `out_file`. 
    Both `in_file` and `out_file` are CONLL-U format files. 
    Use this function to prepare data for experiments that use gold standard 
    UD morphological annotations.
    
    Parameters
    -----------
    in_file
        name/path of the CONLL-U format input file.
    out_file
        name/path of the CONLL-U format output file.
    remove_empty_nodes
        If True (default), then null / empty nodes (of the enhanced representation) will 
        be removed from the output.
    remove_metadata:
        If True, then sentence metadata will be removed from the output conllu file. 
        This might be necessary if you want to create data for legacy parsers such as 
        MaltParser.
        Default: False.
    remove_deps
        If True (default), then values of `deps` field will be replaced with `_`.
    remove_misc
        If True (default), then values of `misc` field will be replaced with `_`.
    '''
    # Import text from conllu
    with open(in_file, 'r', encoding='utf-8') as input_file:
        conll_sentences = conllu.parse(input_file.read())
    # If required, remove orphans / null nodes
    if remove_empty_nodes:
        for sid, sentence in enumerate(conll_sentences):
            removables = []
            for tid, token in enumerate(sentence):
                token_id = token['id']
                if isinstance(token_id, tuple) and len(token_id) == 3 and token_id[1] == '.':
                    removables.append(token)
            if removables:
                for token in removables:
                    sentence.remove(token)
    # Clean annotations
    for sid, sentence in enumerate(conll_sentences):
        for tid, token in enumerate(sentence):
            if remove_misc and token['misc'] is not None:
                token['misc'] = None
            if remove_deps and token['deps'] is not None:
                token['deps'] = None
    # Export annotated file
    with open(out_file, 'w', encoding='utf-8') as out_file:
        for sentence in conll_sentences:
            if remove_metadata:
                sentence.metadata = None
            out_file.write( sentence.serialize() )


# ===============================================================
#  DEBUGGING:
#  Convert UD corpora to EstNLTK format and 
#  compare against reference converted corpus
# ===============================================================

def convert_and_compare_against_reference( in_file, morph_pipeline, morph_layer, ref_file, 
                                           dictionarize=True, remove_empty_nodes=False, 
                                           remove_misc=True, remove_deps=True, seed=43 ):
    '''
    Reannotates `in_file` with given `morph_pipeline` and compares results against `ref_file`. 
    Outputs numers/percentages of matching `upos`, `lemma` and `feats` values.
    For description of parameters, see `convert_ud_conllu_to_estnltk_conllu(...)`.
    '''
    # Validate input pipeline
    assert isinstance(morph_pipeline, list)
    assert isinstance(morph_layer, str)
    has_morph_layer = False
    for tagger in morph_pipeline:
        assert isinstance(tagger, Tagger)
        if morph_layer == tagger.output_layer:
            has_morph_layer = True
    if not has_morph_layer:
        raise Exception(('(!) No tagger in the input pipeline {!r} creates '+\
                         'required layer {!r}.'.format(morph_pipeline, morph_layer)))
    # Import text from conllu
    with open(in_file, 'r', encoding='utf-8') as input_file:
        conll_sentences = conllu.parse(input_file.read())
    # Import reference conllu
    with open(ref_file, 'r', encoding='utf-8') as input_file:
        ref_conll_sentences = conllu.parse(input_file.read())
    text_obj = conll_to_text(in_file, remove_empty_nodes=remove_empty_nodes)
    assert len(text_obj['sentences']) == len(conll_sentences), \
        ('(!) Mismatching sentence numbers in estnltk import ({})'+\
         ' and conllu import ({}).').format( len(text_obj['sentences']), \
                                             len(conll_sentences) )
    # Annotate text
    for tagger in morph_pipeline:
        tagger.tag( text_obj )
    # If required, remove orphans / null nodes
    if remove_empty_nodes:
        token_count = 0
        for sid, sentence in enumerate(conll_sentences):
            removables = []
            for tid, token in enumerate(sentence):
                token_id = token['id']
                if isinstance(token_id, tuple) and len(token_id) == 3 and token_id[1] == '.':
                    removables.append(token)
            if removables:
                for token in removables:
                    sentence.remove(token)
            token_count += len(sentence)
        assert token_count == len(text_obj[morph_layer]), \
            f'(!) Token count mismatch: tokens from CONLL file: {token_count} '+\
            f'vs tokens from EstNLTK annotated text: {len(text_obj[morph_layer])}.'
        token_count = 0
        for sid, sentence in enumerate(ref_conll_sentences):
            removables = []
            for tid, token in enumerate(sentence):
                token_id = token['id']
                if isinstance(token_id, tuple) and len(token_id) == 3 and token_id[1] == '.':
                    removables.append(token)
            if removables:
                for token in removables:
                    sentence.remove(token)
            token_count += len(sentence)
        assert token_count == len(text_obj[morph_layer]), \
            f'(!) Token count mismatch: tokens from CONLL file: {token_count} '+\
            f'vs tokens from EstNLTK annotated text: {len(text_obj[morph_layer])}.'
    # Carry annotations over to TokenList-s
    # In case of an ambiguity, pick random analysis.
    # Fix seed for repeatability
    rand = Random()
    rand.seed(seed)
    word_id = 0
    matches_with_ref_pos = 0
    matches_with_ref_feats = 0
    matches_with_ref_lemma = 0
    matches_complete = 0
    for sid, sentence in enumerate(conll_sentences):
        ref_sentence = ref_conll_sentences[sid]
        for tid, token in enumerate(sentence):
            word_span = text_obj[morph_layer][word_id]
            assert word_span.text == token["form"], f'{word_span.text!r} vs {token["form"]!r}'
            #if isinstance(token['id'], tuple):
            #    print('orphan:', token['id'], token['upos'], token['feats'])
            annotation = rand.choice(word_span.annotations)
            ref_token = ref_sentence[tid]
            token['upos']  = annotation['partofspeech']
            token['xpos']  = annotation['partofspeech']
            token['feats'] = annotation['form']
            # ? Override random pos with first pos (seems to be more accurate ?)
            #token['upos']  = word_span.annotations[0]['partofspeech']
            #token['xpos']  = word_span.annotations[0]['partofspeech']
            if dictionarize:
                # Format form as a dictionary
                form_parts = annotation['form'].split()
                token['feats'] = {f:f for f in form_parts}
            if len(token['feats']) == 0:
                token['feats'] = None
            if remove_misc and token['misc'] is not None:
                token['misc'] = None
            if remove_deps and token['deps'] is not None:
                token['deps'] = None
            word_id += 1
            if token['upos'] == ref_token['upos']:
                matches_with_ref_pos += 1
            if token['feats'] == ref_token['feats']:
                matches_with_ref_feats += 1
            if token['lemma'] == ref_token['lemma']:
                matches_with_ref_lemma += 1
            if token['upos'] == ref_token['upos'] and \
               token['feats'] == ref_token['feats'] and \
               token['lemma'] == ref_token['lemma']:
                matches_complete += 1

    per_pos = matches_with_ref_pos*100.0/word_id
    per_feats = matches_with_ref_feats*100.0/word_id 
    per_lemma = matches_with_ref_lemma*100.0/word_id 
    per_comp = matches_complete*100.0/word_id 
    print('seed:', seed, f'| upos matches: {matches_with_ref_pos}/{word_id} ({per_pos:.2f}%) |'+\
                          f' feats matches: {matches_with_ref_feats}/{word_id} ({per_feats:.2f}%) |'+\
                          f' lemma matches: {matches_with_ref_lemma}/{word_id} ({per_lemma:.2f}%) |'+\
                          f' complete matches: {matches_complete}/{word_id} ({per_comp:.2f}%) |')


def convert_and_compare_against_all_references( in_dir, morph_pipeline, ref_dirs, ref_skip_list=[], seed=43 ):
    '''
    Reannotates CONLL files in `in_dir` with given `morph_pipeline` and 
    compares results against CONLL files in `ref_dirs`. Outputs results of comparison.
    
    Outputs from the last runs:
    
    1) Results if upos is taken from randomly chosen annotation (default setting):
    Conversion target: 'et_edt-ud-dev-morph_extended.conllu', morph layer: 'morph_extended' ...
    seed: 43 | upos matches: 42801/44686 (95.78%) | feats matches: 44686/44686 (100.00%) | lemma matches: 44686/44686 (100.00%) | complete matches: 42801/44686 (95.78%) |
    Conversion target: 'et_edt-ud-test-morph_extended.conllu', morph layer: 'morph_extended' ...
    seed: 43 | upos matches: 46742/48532 (96.31%) | feats matches: 48530/48532 (100.00%) | lemma matches: 48532/48532 (100.00%) | complete matches: 46740/48532 (96.31%) |
    Conversion target: 'et_edt-ud-train-morph_extended.conllu', morph layer: 'morph_extended' ...
    seed: 43 | upos matches: 331461/344953 (96.09%) | feats matches: 343263/344953 (99.51%) | lemma matches: 344953/344953 (100.00%) | complete matches: 330010/344953 (95.67%) |
    
    Conversion target: 'et_edt-ud-dev-morph_analysis.conllu', morph layer: 'morph_analysis' ...
    seed: 43 | upos matches: 39868/44686 (89.22%) | feats matches: 44686/44686 (100.00%) | lemma matches: 44686/44686 (100.00%) | complete matches: 39868/44686 (89.22%) |
    Conversion target: 'et_edt-ud-test-morph_analysis.conllu', morph layer: 'morph_analysis' ...
    seed: 43 | upos matches: 43338/48532 (89.30%) | feats matches: 48530/48532 (100.00%) | lemma matches: 48532/48532 (100.00%) | complete matches: 43338/48532 (89.30%) |
    Conversion target: 'et_edt-ud-train-morph_analysis.conllu', morph layer: 'morph_analysis' ...
    seed: 43 | upos matches: 308432/344953 (89.41%) | feats matches: 344920/344953 (99.99%) | lemma matches: 344953/344953 (100.00%) | complete matches: 308425/344953 (89.41%) |
    
    2) Results if upos/xpos is always taken from the first annotation:
    Conversion target: 'et_edt-ud-dev-morph_extended.conllu', morph layer: 'morph_extended' ...
    seed: 43 | upos matches: 43259/44686 (96.81%) | feats matches: 44686/44686 (100.00%) | lemma matches: 44686/44686 (100.00%) | complete matches: 43259/44686 (96.81%) |
    Conversion target: 'et_edt-ud-test-morph_extended.conllu', morph layer: 'morph_extended' ...
    seed: 43 | upos matches: 47169/48532 (97.19%) | feats matches: 48530/48532 (100.00%) | lemma matches: 48532/48532 (100.00%) | complete matches: 47167/48532 (97.19%) |
    Conversion target: 'et_edt-ud-train-morph_extended.conllu', morph layer: 'morph_extended' ...
    seed: 43 | upos matches: 335582/344953 (97.28%) | feats matches: 343263/344953 (99.51%) | lemma matches: 344953/344953 (100.00%) | complete matches: 334002/344953 (96.83%) |
    
    Conversion target: 'et_edt-ud-dev-morph_analysis.conllu', morph layer: 'morph_analysis' ...
    seed: 43 | upos matches: 40390/44686 (90.39%) | feats matches: 44686/44686 (100.00%) | lemma matches: 44686/44686 (100.00%) | complete matches: 40390/44686 (90.39%) |
    Conversion target: 'et_edt-ud-test-morph_analysis.conllu', morph layer: 'morph_analysis' ...
    seed: 43 | upos matches: 43902/48532 (90.46%) | feats matches: 48530/48532 (100.00%) | lemma matches: 48532/48532 (100.00%) | complete matches: 43902/48532 (90.46%) |
    Conversion target: 'et_edt-ud-train-morph_analysis.conllu', morph layer: 'morph_analysis' ...
    seed: 43 | upos matches: 313489/344953 (90.88%) | feats matches: 344920/344953 (99.99%) | lemma matches: 344953/344953 (100.00%) | complete matches: 313482/344953 (90.88%) |
    '''
    start = datetime.now()
    ref_conllu_file_name_pat = re.compile('^(\S+)-([^\-]+)\.conllu$')
    assert os.path.isdir( in_dir )
    for ref_dir in ref_dirs:
        assert os.path.isdir( ref_dir )
        conllu_files_found = 0
        for ref_fname in os.listdir( ref_dir ):
            if ref_fname in ref_skip_list:
                continue
            m = ref_conllu_file_name_pat.match(ref_fname)
            if m:
                ref_fpath = os.path.join(ref_dir, ref_fname)
                input_file_prefix = m.group(1)
                morph_layer_name = m.group(2)
                # Detect input file
                in_fpath = None
                for in_fname in os.listdir( in_dir ):
                    if in_fname.startswith(input_file_prefix) and in_fname.endswith('.conllu'):
                        in_fpath = os.path.join(in_dir, in_fname)
                if in_fpath is None:
                    raise FileNotFoundError( ('(!) Unable to find file with '+\
                                              'prefix {!r} from dir {!r}.').format(input_file_prefix,
                                                                                   in_dir))
                print(f'Conversion target: {ref_fname!r}, morph layer: {morph_layer_name!r} ...')
                convert_and_compare_against_reference( in_fpath, morph_pipeline, 
                                                       morph_layer_name, ref_fpath,
                                                       seed=seed)
    print(f'Total processing time: {datetime.now()-start}')



if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    # Try to execute all input files as configurations
    for conf_file in sys.argv[1:]:
        convert_to_estnltk_conllu_main( conf_file )
