#
#  Creates frequency table of syntax sketches, and prepares datasets 
#  for sketches knockout experiments: removes clauses corresponding 
#  to sketches systematically from train, dev and test sets.
#

import os
import sys
import configparser
from datetime import datetime
from collections import Counter

from typing import List, Tuple, Dict, Any

import os, os.path
from random import Random

from pandas import DataFrame
from pandas import read_csv

from syntax_sketches.syntax_sketch import safe_sketch_name
from syntax_sketches.syntax_sketch import extract_sketches
from syntax_sketches.syntax_sketch import remove_sketches
from syntax_sketches.syntax_sketch import remove_sketches_group
from syntax_sketches.syntax_sketch import rand_group_sketches
from syntax_sketches.syntax_sketch import compute_sketches
from syntax_sketches.clause_import import import_clauses
from syntax_sketches.clause_export import remove_extracted_from_conllu_and_dicts

def prepare_sketches_main( conf_file ):
    '''
    Creates frequency table of syntax sketches for a corpus, and/or
    prepares datasets for sketches knockout experiments: removes 
    clauses corresponding to sketches systematically from train, 
    dev and test sets.
    Inputs/outputs and parameters of the processing will be read 
    from the given `conf_file`. 
    Executes sections in the configuration starting with prefix 
    'make_sketches_table_' and 'prepare_knockout_'. 
    '''
    # Parse configuration file
    config = configparser.ConfigParser()
    if conf_file is None or not os.path.exists(conf_file):
        raise FileNotFoundError("Config file {} does not exist".format(conf_file))
    if len(config.read(conf_file)) != 1:
        raise ValueError("File {} is not accessible or is not in valid INI format".format(conf_file))
    section_found = False
    start = datetime.now()
    for section in config.sections():
        if section.startswith('make_sketches_table_'):
            section_found = True
            print(f'Performing {section} ...')
            # Collect sketch computing parameters
            if not config.has_option(section, 'input_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_dir" parameter.')
            input_dir = config[section]['input_dir']
            if not os.path.isdir(input_dir):
                raise FileNotFoundError(f'Error in {conf_file}: invalid "input_dir" value {input_dir!r} in {section!r}.')
            if not config.has_option(section, 'output_csv_file'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_csv_file" parameter.')
            output_csv_file = config[section]['output_csv_file']
            top_n = config[section].getint('top_n', 50)
            skip_list = config[section].get('skip_list', [])
            if len(skip_list) > 0:
                skip_list = skip_list.split(',')
                skip_list = [fname.strip() for fname in skip_list]
            # Compute sketches frequency TOP N and save into CSV file
            compute_sketches_freq_table( input_dir, top_n, output_csv_file, skip_files=skip_list, verbose=True )
        elif section.startswith('prepare_knockout_'):
            section_found = True
            print(f'Performing {section} ...')
            # Collect knockout preparation parameters
            # input_dir -- contains train/dev/test conllu files with clauses
            if not config.has_option(section, 'input_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_dir" parameter.')
            input_dir = config[section]['input_dir']
            if not os.path.isdir(input_dir):
                raise FileNotFoundError(f'Error in {conf_file}: invalid "input_dir" value {input_dir!r} in {section!r}.')
            # top_sketches_file -- CSV file containing top_n sketches (created via 'make_sketches_table_')
            if not config.has_option(section, 'top_sketches_file'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "top_sketches_file" parameter.')
            top_sketches_file = config[section]['top_sketches_file']
            if not os.path.isfile(top_sketches_file):
                raise FileNotFoundError(f'Error in {conf_file}: invalid or missing "top_sketches_file" value '+\
                                        f'{top_sketches_file!r} in {section!r}.')
            # min_support -- the minimun number of clauses from top n sketches in test panel. 
            # If test set does not contain at least min_support clauses of a sketch, then missing 
            # number of clauses will be extracted and removed from the train set. 
            min_support = config[section].getint('min_support', 50)
            # random_groups -- distributes top_n_sketches randomly into random_groups bins, 
            # and prepares knockout splits on groups instead of on all sketches. 
            # If None (default), then prepares knockout splits on all top_n_sketches separately.
            random_groups = config[section].getint('random_groups', None)
            grouping_seed = config[section].getint('grouping_seed', 1)
            top_sketches_grouped_file = config[section].get('top_sketches_grouped_file', None)
            # create_control -- instead of preparing knockout data on top_n_sketches or corresponding groups, 
            # pick same amounts of clauses randomly for control experiment.
            create_control = config[section].getboolean('create_control', False)
            create_control_seed = config[section].getint('create_control_seed', 5)
            # initial_output_dir -- for saving test panel and pure train data
            if not config.has_option(section, 'initial_output_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "initial_output_dir" parameter.')
            initial_output_dir = config[section]['initial_output_dir']
            initial_train_fname = config[section].get('initial_train_fname', 'train_pure.conllu')
            initial_test_fname  = config[section].get('initial_test_fname', None)
            # final_output_dir -- for saving knockout splits data
            if not config.has_option(section, 'final_output_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "final_output_dir" parameter.')
            final_output_dir = config[section]['final_output_dir']
            # Load input data
            whole_data_map = load_clauses_datasets(input_dir)
            top_n_sketches = read_csv(top_sketches_file, index_col=0).values.tolist()
            # Create output directories and required file names
            if not os.path.exists(initial_output_dir):
                os.makedirs(initial_output_dir, exist_ok=True)
            if not os.path.exists(final_output_dir):
                os.makedirs(final_output_dir, exist_ok=True)
            if initial_test_fname is None:
                initial_test_fname = f'test_{len(top_n_sketches)}x{min_support}.conllu'
            initial_test_fname  = os.path.join(initial_output_dir, initial_test_fname)
            initial_train_fname = os.path.join(initial_output_dir, initial_train_fname)
            if random_groups is not None:
                # ==================================
                #  Knockout grouped top sketches 
                # ==================================
                if random_groups is not None and top_sketches_grouped_file is None:
                    top_sketches_grouped_file = f'top_{len(top_n_sketches)}_sketches_{random_groups}_groups.csv'
                    # Put top_sketches_grouped_file into same folder as top_sketches_file
                    head, tail = os.path.split( top_sketches_file )
                    if len(head) > 0:
                        top_sketches_grouped_file = os.path.join( head, top_sketches_grouped_file )
                # Group sketches
                grouped_sketches = group_top_sketches_randomly(top_n_sketches, random_groups, top_sketches_grouped_file, 
                                                               seed=grouping_seed)
                # Create test panel and pure train
                test_data, test_data_sketches = \
                    create_test_panel_and_pure_train(top_n_sketches, whole_data_map, initial_test_fname, 
                                                     initial_train_fname, min_support=min_support)
                # Create knockout data 
                control_removed = create_knockout_files_from_grouped_sketches(grouped_sketches, test_data_sketches, 
                                                                              test_data, whole_data_map, final_output_dir,
                                                                              dry_run=create_control)
                if create_control:
                    # Create randomized control data
                    create_random_control_files_from_grouped_sketches(grouped_sketches, test_data_sketches, test_data, 
                                                                      whole_data_map, control_removed, final_output_dir, 
                                                                      seed=create_control_seed)
            else:
                # ==================================
                #  Knockout all top sketches        
                # ==================================
                # Create test panel and pure train
                test_data, test_data_sketches = \
                    create_test_panel_and_pure_train(top_n_sketches, whole_data_map, initial_test_fname, 
                                                     initial_train_fname, min_support=min_support)
                # Create knockout data 
                control_removed = create_knockout_files_from_sketches(test_data_sketches, test_data, whole_data_map, 
                                                                      final_output_dir, dry_run=create_control)
                if create_control:
                    # Create randomized control data
                    create_random_control_files_from_sketches(test_data_sketches, test_data, whole_data_map, 
                                                              control_removed, final_output_dir, 
                                                              seed=create_control_seed)
    if section_found:
        print(f'Total processing time: {datetime.now()-start}')
    else:
        print(f'No section starting with "make_sketches_table_" or "prepare_knockout_" in {conf_file}.')

# =============================================
#  Make sketches frequency table               
# =============================================

def compute_sketches_freq_table(input_dir:str, N:int, output_file:str, skip_files:List[str]=[], verbose:bool=True):
    '''
    Computes syntax sketches for conllu files in the input_dir, extracts top N most frequent sketches 
    and saves into CSV file output_file (must end with '.csv').
    Assumes that all conllu files in the input_dir have been created via script "01b_extract_clauses.py", 
    that is, they contain clauses instead of sentences. 
    Optionally, you can skip some of the conllu input files from computations via parameter skip_files.
    Returns DataFrame with most frequent sketches and their frequencies.
    '''
    assert output_file.endswith('.csv'), f'(!) Unexpected file ending for a csv file {output_file!r}'
    sketches, clauses_count_total = compute_sketches( input_dir, skip_files=skip_files, verbose=verbose )
    sketch_counter = Counter(sketches)
    df = DataFrame({
        'sketch': [sketch for sketch, _ in sketch_counter.most_common(N)],
        'support': [count for _, count in sketch_counter.most_common(N)] 
    })
    if verbose:
        print(f'Writing sketches freq table into {output_file}.')
    df.to_csv( output_file )
    return df

# =============================================
#  Prepare sketches data for knockout exp      
# =============================================

def load_clauses_datasets(input_dir:str, skip_files:List[str]=[], verbose:bool=True):
    '''
    Loads train, dev and test datasets from conllu files in the input_dir.
    The input_dir must contain exactly one file of each type.
    Assumes that all conllu files in the input_dir have been created via 
    script "01b_extract_clauses.py", that is, they contain clauses instead 
    of sentences. 
    Returns dictionary mapping keys {'train', 'dev', 'test'} to lists 
    [file_name, list_of_clause_conllu_strings, list_of_clause_dicts].
    '''
    # Load data from conllu files
    whole_data = []
    for fname in os.listdir(input_dir):
        if fname in skip_files:
            continue
        if fname.endswith('.conllu'):
            # import clauses as conllu strings
            clauses = import_clauses( os.path.join(input_dir, fname), as_dicts=False )
            # import clauses as dicts (required for sketch creation)
            clause_dicts = import_clauses( os.path.join(input_dir, fname), as_dicts=True )
            # sanity check
            assert len(clauses) == len(clause_dicts), f'{len(clauses)} vs {len(clause_dicts)}'
            if verbose:
                print( fname, f'| #clauses: {len(clauses)}' )
            whole_data.append( (fname, clauses, clause_dicts) )
    # Map loaded train, test, dev sets to named shortcuts
    whole_data_map = {}
    for (fname, clauses, clause_dicts) in whole_data:
        if 'train' in fname:
            assert 'train' not in whole_data_map.keys(), \
                f'More than 1 train files: {fname} vs {whole_data_map["train"][0]}'
            whole_data_map['train'] = [fname, clauses, clause_dicts]
        elif 'dev' in fname:
            assert 'dev' not in whole_data_map.keys(), \
                f'More than 1 dev files: {fname} vs {whole_data_map["dev"][0]}'
            whole_data_map['dev'] = [fname, clauses, clause_dicts]
        elif 'test' in fname:
            assert 'test' not in whole_data_map.keys(), \
                f'More than 1 test files: {fname} vs {whole_data_map["test"][0]}'
            whole_data_map['test'] = [fname, clauses, clause_dicts]
    assert whole_data_map.keys() == {'train', 'dev', 'test'}
    return whole_data_map

def write_conllu_file(out_fpath:str, clauses_conllus:List[str]):
    '''
    Saves clause conllu strings (clauses_conllus) into file out_fpath. 
    An existing file will be overwritten. 
    '''
    assert out_fpath.endswith('.conllu'), \
        f'(!) Unexpected output file ending in {out_fpath}. Expected file ending with .conllu'
    with open(out_fpath, 'w', encoding='utf-8') as fout:
        fout.write('\n\n'.join( clauses_conllus ))
        # Add final empty line (to avoid UDError: The CoNLL-U file does not end with empty line)
        fout.write('\n\n')

def create_test_panel_and_pure_train(top_sketches_list:List[Any], whole_data_map:Dict[str,List[Any]], 
                                     test_file:str, train_file:str, min_support:int=50, 
                                     verbose:bool=True) -> Tuple[List[str], List[List[str]]]:
    '''
    Creates a panel test set, extracting all occurrences of top_sketches_list from test set.
    If test set does not contain at least min_support (default: 50) clauses of a sketch, 
    then extracts and removes missing number of clauses from the train set. 
    Saves the panel test set into test_fname, and purified train set (that has no overlap 
    with test panel) into train_file. 
    Returns tuple (list_of_sketch_names, list_of_corresponding_clause_conllus)
    '''
    c = 0
    test_data = []
    test_data_sketches = []
    for sketch, support in sorted(top_sketches_list, key=lambda x:x[1], reverse=True):
        # Extract all sketches from the test set
        test_conllu = whole_data_map['test'][1]
        test_dicts  = whole_data_map['test'][2]
        extracted_conllu, extracted_dicts, extracted_amount = \
            extract_sketches(test_conllu, test_dicts, sketch)
        if verbose:
            print(sketch)
            print( f'    extracted {extracted_amount} clauses from test' )
        test_data.append( extracted_conllu )
        test_data_sketches.append( sketch )
        if extracted_amount < min_support:
            # If the test set does not contain enough instances (at least min_support),
            # we take them form the training set. There are enough clauses in the training 
            # set so this should not effect the overall performance.
            train_conllu = whole_data_map['train'][1]
            train_dicts  = whole_data_map['train'][2]
            extracted_train_conllu, extracted_train_dicts, extracted_train_amount = \
                    extract_sketches(train_conllu, train_dicts, sketch, amount=min_support-extracted_amount)
            if verbose:
                print( f'    extracted {extracted_train_amount} clauses from train' )
            # Extend the last sub list in new test
            test_data[-1].extend( extracted_train_conllu )
            # Remove extracted clauses from train
            new_train_conllu, new_train_dicts, deletion_counts = \
                remove_extracted_from_conllu_and_dicts(train_conllu, train_dicts, extracted_train_conllu)
            assert len(new_train_conllu) == len(train_conllu) - sum(deletion_counts.values())
            assert len(new_train_dicts) == len(train_dicts) - sum(deletion_counts.values())
            # Update train (make it pure from test)
            whole_data_map['train'][1] = new_train_conllu
            whole_data_map['train'][2] = new_train_dicts
        c += 1
    assert len(test_data) == len(test_data_sketches)
    # Write out test panel file
    flat_test_data = [line for conll_list in test_data for line in conll_list]
    write_conllu_file( test_file, flat_test_data )
    if verbose:
        print(f' Saved {len(flat_test_data)} test clauses into {test_file}.')
    # Write out purified train file (all clauses from test panel have been removed)
    write_conllu_file( train_file, whole_data_map['train'][1] )
    if verbose:
        print(f' Saved {len(whole_data_map["train"][1])} train clauses into {train_file}.')
    return test_data, test_data_sketches

# ==================================
#  Knockout grouped top sketches 
# ==================================

def group_top_sketches_randomly(top_sketches_list:List[Any], N:int, output_csv_file:str, seed:int=1, 
                                flatten_groups:bool=True):
    '''
    Distributes items of top_sketches_list randomly into N roughly equal size bins. 
    Assumes top_sketches_list is a list of lists, where each sub list contains two 
    items: sketch name (str) and its frequency (int).
    Returns list of lists of lists, where there are N sub lists and each sub list 
    contains two item lists (sketch name and support).
    If flatten_groups==True (default), then returns list of lists, where there are 
    N sub lists and each sub list contains only sketch names.
    '''
    grouped = rand_group_sketches( top_sketches_list, N, seed=seed )
    DataFrame({
        'grouped_sketches': [';'.join([s[0] for s in gr]) for gr in grouped],
        'support': [sum([s[1] for s in gr]) for gr in grouped]
    }).to_csv( output_csv_file )
    if flatten_groups:
        # Flatten list: remove sketch frequencies, 
        # keep only sketch names
        new_grouped = []
        for group in grouped:
            assert all([isinstance(sketch[0], str) for sketch in group])
            sketches_list = [sketch[0] for sketch in group]
            new_grouped.append(sketches_list)
        grouped = new_grouped
    return grouped

def create_knockout_files_from_grouped_sketches(grouped_sketches:List[Any], test_data_sketches:List[str], 
                                                test_data:List[List[str]], whole_data_map:Dict[str,List[Any]], 
                                                output_dir:str, dry_run:bool=False, verbose:bool=True) -> List[Tuple[int, int, int]]:
    '''
    Creates knockout train, dev and test files based on the grouped_sketches.
    For each sketch group, removes all clauses corresponding to sketches of the 
    group from train and dev, and creates a subset of test set containing only 
    clauses corresponding to sketches of the group. 
    Saves resulting files into output_dir, under names 'test_group{GID}.conllu',
    'train_group{GID}.conllu', 'dev_group{GID}.conllu', where GID is the index 
    of the sketch group.
    If dry_run==True, then only emulates saving sketches into files, but does 
    not write any actual files. Use this option if you want to collect removal 
    statistics for preparation of control experiments.
    Returns tuple: 
    (sketch group index, no of clauses removed from train, no of clauses removed from dev)
    '''
    assert len(test_data_sketches) == len(test_data)
    control_removed = [] # (sketch group, no of clauses removed from train, no of clauses removed from dev)
    for gid, group in enumerate( grouped_sketches ):
        assert isinstance(group, list) and all(isinstance(s, str) for s in group)
        if verbose:
            print(f'group: {gid}')
        #
        # Subset for test
        #
        # Collect all test clauses of given group
        group_clauses = []
        for sketch, test_conll in zip(test_data_sketches, test_data):
            if sketch in group:
                if verbose:
                    print(sketch)
                group_clauses.extend(test_conll)
        out_test_fname = f'test_group{gid}.conllu'
        if not dry_run:
            write_conllu_file( os.path.join(output_dir, out_test_fname), group_clauses )
        if verbose:
             print(f'  Saved {len(group_clauses)} test clauses into {out_test_fname}.')
        #
        # Extract subset of dev
        #
        all_conllu = whole_data_map['dev'][1]
        all_dicts  = whole_data_map['dev'][2]
        # Remove and return remaining clauses
        # Note: the removal is virtual, actual lists are not affected
        preserved_conllu, preserved_dicts, removed_amount_dev = \
            remove_sketches_group(all_conllu, all_dicts, group)
        out_dev_fname = f'dev_group{gid}.conllu'
        if not dry_run:
            write_conllu_file( os.path.join(output_dir, out_dev_fname), preserved_conllu )
        if verbose:
            print(f'  Removed {removed_amount_dev} clauses and saved remaining {len(preserved_conllu)} dev clauses into {out_dev_fname}.')
        #
        # Extract subset of train
        #
        # Assume that instances appearing in test set 
        # have already been removed in previous steps
        # (we have a "pure train set")
        all_conllu = whole_data_map['train'][1]
        all_dicts  = whole_data_map['train'][2]
        # Remove and return remaining clauses
        # Note: the removal is virtual, actual lists are not affected
        preserved_conllu, preserved_dicts, removed_amount_train = \
            remove_sketches_group(all_conllu, all_dicts, group)
        out_train_fname = f'train_group{gid}.conllu'
        if not dry_run:
            write_conllu_file( os.path.join(output_dir, out_train_fname), preserved_conllu )
        if verbose:
            print(f'  Removed {removed_amount_train} clauses and saved remaining {len(preserved_conllu)} train clauses into {out_train_fname}.')
        # Remember how much we removed (for control experiments)
        control_removed.append( (gid, removed_amount_train, removed_amount_dev) )
    return control_removed


def create_random_control_files_from_grouped_sketches(grouped_sketches:List[Any], test_data_sketches:List[str], 
                                                      test_data:List[List[str]], whole_data_map:Dict[str,List[Any]], 
                                                      control_removed:List[Tuple[int, int, int]], output_dir:str, 
                                                      seed:int=5, verbose:bool=True) -> List[Tuple[int, int, int]]:
    '''
    Creates random control train, dev and test files for grouped knockout experiments. 
    For each sketch group, removes randomly the same amount of clauses that were removed 
    in knockout dataset preparation (create_knockout_files_from_grouped_sketches) from 
    train and dev files. Group's test set will be the same as in knockout dataset 
    preparation.
    Saves resulting files into output_dir, under names 'test_group{GID}.conllu',
    'train_group{GID}.conllu', 'dev_group{GID}.conllu', where GID is the index 
    of the sketch group.
    '''
    assert len(test_data_sketches) == len(test_data)
    rnd = Random()
    rnd.seed(seed)
    for (gid, removed_from_train, removed_from_dev) in control_removed:
        group = grouped_sketches[gid]
        assert isinstance(group, list) and all(isinstance(s, str) for s in group)
        if verbose:
            print(f'group: {gid}')
        #
        # Subset for test
        #
        # Collect all test clauses of given group
        group_clauses = []
        for sketch, test_conll in zip(test_data_sketches, test_data):
            if sketch in group:
                if verbose:
                    print(sketch)
                group_clauses.extend(test_conll)
        out_test_fname = f'test_group{gid}.conllu'
        write_conllu_file( os.path.join(output_dir, out_test_fname), group_clauses )
        if verbose:
             print(f'  Saved {len(group_clauses)} test clauses into {out_test_fname}.')
        # 
        # Pick randomly same amount of clauses from train & dev
        #
        train_pure = whole_data_map['train'][1]
        dev_full   = whole_data_map['dev'][1]
        train_sample = rnd.sample(range(0, len(train_pure)+1), removed_from_train)
        dev_sample   = rnd.sample(range(0, len(dev_full)+1), removed_from_dev)
        #
        # Remove randomly picked clause instances
        #
        ablation_train = []
        ablation_dev = []
        for i, conllu in enumerate(train_pure):
            if i in train_sample:
                continue
            ablation_train.append(conllu)
        for i, conllu in enumerate(dev_full):
            if i in dev_sample:
                continue
            ablation_dev.append(conllu)
        #
        # Save results
        #
        out_dev_fname = f'dev_group{gid}.conllu'
        write_conllu_file( os.path.join(output_dir, out_dev_fname), ablation_dev )
        if verbose:
            print(f'  Removed {removed_from_dev} clauses randomly and saved remaining {len(ablation_dev)} dev clauses into {out_dev_fname}.')
        out_train_fname = f'train_group{gid}.conllu'
        write_conllu_file( os.path.join(output_dir, out_train_fname), ablation_train )
        if verbose:
            print(f'  Removed {removed_from_train} clauses randomly and saved remaining {len(ablation_train)} train clauses into {out_train_fname}.')


# ==================================
#  Knockout all top sketches        
# ==================================

def create_knockout_files_from_sketches(test_data_sketches:List[str], test_data:List[List[str]], 
                                        whole_data_map:Dict[str,List[Any]], output_dir:str, 
                                        dry_run:bool=False, verbose:bool=True) -> List[Tuple[int, int, int]]:
    '''
    Creates knockout train, dev and test files based for all test_data_sketches. 
    For sketch in test_data_sketches, removes its clauses from train and dev, and 
    creates a subset of test set containing only clauses of this sketch. 
    Saves resulting files into output_dir, under names 'test_{SKETCH}.conllu',
    'train_{SKETCH}.conllu', 'dev_{SKETCH}.conllu', where SKETCH is the name 
    of the sketch (made safe via safe_sketch_name(...)).
    If dry_run==True, then only emulates saving sketches into files, but does 
    not write any actual files. Use this option if you want to collect removal 
    statistics for preparation of control experiments.
    Returns tuple: 
    (sketch name, no of clauses removed from train, no of clauses removed from dev)
    '''
    assert len(test_data_sketches) == len(test_data)
    control_removed = [] # (sketch name, no of clauses removed from train, no of clauses removed from dev)
    for sketch, test_conll in zip(test_data_sketches, test_data):
        sketch_id = safe_sketch_name(sketch)
        if verbose:
            print(sketch)
        #
        # Subset for test
        #
        out_test_fname = f'test_{sketch_id}.conllu'
        if not dry_run:
            write_conllu_file( os.path.join(output_dir, out_test_fname), test_conll )
        if verbose:
             print(f'  Saved {len(test_conll)} test clauses into {out_test_fname}.')
        #
        # Extract subset of dev
        #
        all_conllu = whole_data_map['dev'][1]
        all_dicts  = whole_data_map['dev'][2]
        # Remove sketch and return remaining clauses
        # Note: the removal is virtual, actual lists are not affected
        preserved_conllu, preserved_dicts, removed_amount_dev = \
            remove_sketches(all_conllu, all_dicts, sketch)
        out_dev_fname = f'dev_{sketch_id}.conllu'
        if not dry_run:
            write_conllu_file( os.path.join(output_dir, out_dev_fname), preserved_conllu )
        if verbose:
            print(f'  Removed {removed_amount_dev} clauses and saved remaining {len(preserved_conllu)} dev clauses into {out_dev_fname}.')
        #
        # Extract subset of train
        #
        # Assume that instances appearing in test set 
        # have already been removed in previous steps
        # (we have a "pure train set")
        all_conllu = whole_data_map['train'][1]
        all_dicts  = whole_data_map['train'][2]
        # Remove sketch and return remaining clauses
        # Note: the removal is virtual, actual lists are not affected
        preserved_conllu, preserved_dicts, removed_amount_train = \
            remove_sketches(all_conllu, all_dicts, sketch)
        out_train_fname = f'train_{sketch_id}.conllu'
        if not dry_run:
            write_conllu_file( os.path.join(output_dir, out_train_fname), preserved_conllu )
        if verbose:
            print(f'  Removed {removed_amount_train} clauses and saved remaining {len(preserved_conllu)} train clauses into {out_train_fname}.')
        # Remember how much we removed (for control experiments)
        control_removed.append( (sketch, removed_amount_train, removed_amount_dev) )
    return control_removed


def create_random_control_files_from_sketches(test_data_sketches:List[str], test_data:List[List[str]], 
                                              whole_data_map:Dict[str,List[Any]], control_removed:List[Tuple[int, int, int]], 
                                              output_dir:str, seed:int=5, verbose:bool=True) -> List[Tuple[int, int, int]]:
    '''
    Creates random control train, dev and test files for single sketch knockout experiments. 
    For sketch in test_data_sketches, removes randomly the same amount of clauses that were 
    removed in knockout dataset preparation (create_knockout_files_from_sketches) from 
    train and dev files. Group's test set will be the same as in knockout dataset 
    preparation.
    Saves resulting files into output_dir, under names 'test_{SKETCH}.conllu',
    'train_{SKETCH}.conllu', 'dev_{SKETCH}.conllu', where SKETCH is the name 
    of the sketch (made safe via safe_sketch_name(...)).
    '''
    assert len(test_data_sketches) == len(test_data)
    rnd = Random()
    rnd.seed(seed)
    for (sketch, removed_from_train, removed_from_dev) in control_removed:
        sketch_id = safe_sketch_name(sketch)
        if verbose:
            print(sketch)
        #
        # Subset for test
        #
        # Collect all test clauses of the sketch
        sketch_clauses = []
        for sketch2, test_conll in zip(test_data_sketches, test_data):
            if sketch2 == sketch:
                sketch_clauses.extend(test_conll)
                break
        out_test_fname = f'test_{sketch_id}.conllu'
        write_conllu_file( os.path.join(output_dir, out_test_fname), sketch_clauses )
        if verbose:
             print(f'  Saved {len(sketch_clauses)} test clauses into {out_test_fname}.')
        # 
        # Pick randomly same amount of clauses from train & dev
        #
        train_pure = whole_data_map['train'][1]
        dev_full   = whole_data_map['dev'][1]
        train_sample = rnd.sample(range(0, len(train_pure)+1), removed_from_train)
        dev_sample   = rnd.sample(range(0, len(dev_full)+1), removed_from_dev)
        #
        # Remove randomly picked clause instances
        #
        ablation_train = []
        ablation_dev = []
        for i, conllu in enumerate(train_pure):
            if i in train_sample:
                continue
            ablation_train.append(conllu)
        for i, conllu in enumerate(dev_full):
            if i in dev_sample:
                continue
            ablation_dev.append(conllu)
        #
        # Save results
        #
        out_dev_fname = f'dev_{sketch_id}.conllu'
        write_conllu_file( os.path.join(output_dir, out_dev_fname), ablation_dev )
        if verbose:
            print(f'  Removed {removed_from_dev} clauses randomly and saved remaining {len(ablation_dev)} dev clauses into {out_dev_fname}.')
        out_train_fname = f'train_{sketch_id}.conllu'
        write_conllu_file( os.path.join(output_dir, out_train_fname), ablation_train )
        if verbose:
            print(f'  Removed {removed_from_train} clauses randomly and saved remaining {len(ablation_train)} train clauses into {out_train_fname}.')

# =============================================
# =============================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    # Try to execute all input files as configurations
    for conf_file in sys.argv[1:]:
        prepare_sketches_main( conf_file )
