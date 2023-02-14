#
#  Creates data splits/joins of the following experiments:
#
#  * crossvalidation -- split data into N groups; use each 
#                       unique group only once as a test set;
#  * smaller_data -- split data into N groups with increasing 
#                    training set sizes;
#  * half_data -- split data into N groups; each group has 
#                 training size half of the available training 
#                 size;
#  * single_file -- split single file into train, dev and test.
#                   (mainly used for debbuging pipeline)
#  * full_data -- train and dev sets are joined into one set
#                 (for final evaluation);
#

import csv
import os
import os.path
import sys
import random
import warnings
import json

import conllu
import configparser

# ===============================================================
#  Create data splits/joins required by experiments (MAIN)
# ===============================================================

def create_train_splits_joins_main( conf_file ):
    '''
    Creates data splits (or joins) based on the configuration. 
    Settings/parameters of the conversion will be read from the given 
    `conf_file`. 
    Executes sections in the configuration starting with prefixes 
    'split_' and 'join_'.
    
    For details about the conversion and possible parameters, 
    see the functions:
    * `create_crossvalidation_splits(...)` 
    * `create_smaller_data_splits(...)` 
    * `create_half_data_splits(...)` 
    * `create_single_file_split(...)` 
    '''
    # Parse configuration file
    config = configparser.ConfigParser()
    if conf_file is None or not os.path.exists(conf_file):
        raise FileNotFoundError("Config file {} does not exist".format(conf_file))
    if len(config.read(conf_file)) != 1:
        raise ValueError("File {} is not accessible or is not in valid INI format".format(conf_file))
    section_found = False
    for section in config.sections():
        if section.startswith('join_'):
            #
            # Load joining configuration from the section
            # Check validity of the parameters
            #
            section_found = True
            print(f'Performing {section} ...')
            if not config.has_option(section, 'input_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_dir" parameter.')
            input_dir = config[section]['input_dir']
            if not os.path.isdir(input_dir):
                raise FileNotFoundError(f'Error in {conf_file}: invalid "input_dir" value {input_dir!r} in {section!r}.')
            concatenate = config[section].get('concatenate', 'train, dev')
            target_subsets = concatenate.split(',')
            if len(target_subsets) != 2:
                raise ValueError(f'Error in {conf_file}: {section}.concatenate must have 2 values, '+\
                                 f'not {len(target_subsets)}.' )
            train_full_name = config[section].get('train_full', 'train_full.conllu')
            # Collect input files
            concatenate_files = []
            for subset in target_subsets:
                subset = subset.strip()
                if subset not in ['train', 'dev', 'test']:
                    raise ValueError(f'Error in {conf_file}: {section}.concatenate has invalid value {subset}.')
                # Find corresponding file from the input dir
                for fname in os.listdir(input_dir):
                    if fname == train_full_name:
                        continue
                    if fname.endswith('.conllu') and subset in fname:
                        concatenate_files.append(os.path.join(input_dir, fname))
            if len(concatenate_files) != 2:
                raise ValueError(f'Unable to get 2 concatenateable conllu files from dir {input_dir!r}. '+
                                  'Is the directory correct?')
            if not config.has_option(section, 'output_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
            output_dir = config[section]['output_dir']
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            #
            #  Concatenate two files (typically train and dev) into one file
            #
            train_full_file = os.path.join(output_dir, train_full_name)
            join_train_dev( train_path=concatenate_files[0], dev_path=concatenate_files[1], 
                            output_path=train_full_file )
        elif section.startswith('split_'):
            #
            # Load spltting configuration from the section
            # Check validity of the parameters
            #
            section_found = True
            print(f'Performing {section} ...')
            split_type = config[section].get('split_type',  'crossvalidation')
            split_type_clean = (split_type.strip()).lower()
            if split_type_clean not in ['crossvalidation', 'smaller_data', 'half_data', 'single_file']:
                raise ValueError('(!) Unexpected split type value: {!r}'.format(split_type))
            if split_type_clean == 'single_file':
                # -----------------------------------
                # 'single_file_split'
                # -----------------------------------
                if not config.has_option(section, 'input_file'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_file" parameter.')
                input_file = config[section]['input_file']
                split_ratio = config[section].get('split_ratio', '80, 10, 10')
                split_subset_ratios = []
                for subset in split_ratio.split(','):
                    subset = subset.strip()
                    if not subset.isnumeric():
                         raise ValueError(f'Error in {conf_file}: {section}.split_ratio has invalid value {subset}.')
                    split_subset_ratios.append( int(subset) )
                if len(split_subset_ratios) != 3:
                    raise ValueError(f'Error in {conf_file}: {section}.split_ratio has invalid value {subset}: must have 3 ratios.')
                seed = config[section].getint('seed', 9)
                shuffle = config[section].getboolean('shuffle', False)
                subset_size = config[section].getint('subset_size', None)
                if not config.has_option(section, 'output_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
                output_dir = config[section]['output_dir']
                create_single_file_split(input_file, output_dir, 
                                         train=split_subset_ratios[0], 
                                         dev=split_subset_ratios[1], 
                                         test=split_subset_ratios[2], 
                                         subset_size=subset_size, 
                                         shuffle=shuffle, 
                                         seed=seed)
            else:
                # -----------------------------------
                # 'crossvalidation', 
                # 'smaller_data',
                # 'half_data'
                # -----------------------------------
                if not config.has_option(section, 'input_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_dir" parameter.')
                input_dir = config[section]['input_dir']
                if not os.path.isdir(input_dir):
                    raise FileNotFoundError(f'Error in {conf_file}: invalid "input_dir" value {input_dir!r} in {section!r}.')
                concatenate = config[section].get('concatenate', 'train, dev')
                target_subsets = concatenate.split(',')
                if len(target_subsets) != 2:
                    raise ValueError(f'Error in {conf_file}: {section}.concatenate must have 2 values, '+\
                                     f'not {len(target_subsets)}.' )
                # Collect input files
                concatenate_files = []
                for subset in target_subsets:
                    subset = subset.strip()
                    if subset not in ['train', 'dev', 'test']:
                        raise ValueError(f'Error in {conf_file}: {section}.concatenate has invalid value {subset}.')
                    # Find corresponding file from the input dir
                    for fname in os.listdir(input_dir):
                        if fname == 'train_full.conllu':
                            continue
                        if fname.endswith('.conllu') and subset in fname:
                            concatenate_files.append(os.path.join(input_dir, fname))
                if len(concatenate_files) != 2:
                    raise ValueError(f'Unable to get 2 concatenateable conllu files from dir {input_dir!r}. '+
                                      'Is the directory correct?')
                split_file  = config[section].get('split_file', 'splits.csv')
                block_count = config[section].getint('block_count', 195)
                split_count = config[section].getint('split_count', 10)
                seed = config[section].getint('seed', 9)
                if not config.has_option(section, 'first_output_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "first_output_dir" parameter.')
                first_output_dir = config[section]['first_output_dir']
                if not config.has_option(section, 'final_output_dir'):
                    raise ValueError(f'Error in {conf_file}: section {section!r} is missing "final_output_dir" parameter.')
                final_output_dir = config[section]['final_output_dir']
                #
                # Perform splitting according to the split type
                #
                if split_type_clean == 'crossvalidation':
                    create_crossvalidation_splits(concatenate_files[0], concatenate_files[1], first_output_dir, 
                                                  final_output_dir, split_csv_file=split_file, block_count=block_count, 
                                                  split_count=split_count, seed=seed)
                if split_type_clean == 'smaller_data':
                    create_smaller_data_splits(concatenate_files[0], concatenate_files[1], first_output_dir, 
                                               final_output_dir, split_csv_file=split_file, block_count=block_count, 
                                               split_count=split_count, seed=seed)
                if split_type_clean == 'half_data':
                    # Warn about parameters not changable (not implemented)
                    for param in ['block_count', 'split_count']:
                        if config.has_option(section, param):
                            msg = f'In {conf_file}, section {section!r}: parameter {param!r} not changable in half_data experiments.'
                            warnings.warn( msg )
                    create_half_data_splits(concatenate_files[0], concatenate_files[1],  first_output_dir, final_output_dir,
                                                split_csv_file=split_file, seed=seed)
    if not section_found:
        print(f'No section starting with "split_" or "join_" in {conf_file}.')


def create_crossvalidation_splits(train_file, dev_file, first_splits_path, crossval_split_path,
                                  split_csv_file='splits.csv', block_count=195, split_count=10, seed=9):
    '''
    Creates crossvalidation splits based on given input CONLLU files (`train_file` and `dev_file`). 
    First, concatenates train_file and dev_file into one file and saves under first_splits_path.
    Then splits the concatenated conllu file randomly into `split_count` sub sets. 
    
    The splitting process: 1) the input is first split at the word-level into roughly 
    equal-sized blocks (`block_count` blocks), 2) the order of blocks is shuffled, and 
    3) the shuffling result is split into `split_count` sub sets. 
    
    Saves sub sets into folder `first_splits_path`.
    
    Finally, rotates over subsets in a way that each sub set belongs to test and dev at once,
    and the remaining subsets belong to train. Saves results (crossvalidation subsets) into
    folder `crossval_split_path`. 
    '''
    # Validate inputs
    if not os.path.exists(train_file) or not os.path.isfile(train_file):
        raise FileNotFoundError(f'(!) Missing or invalid input file {train_file}')
    if not os.path.exists(dev_file) or not os.path.isfile(dev_file):
        raise FileNotFoundError(f'(!) Missing or invalid input file {dev_file}')
    if not os.path.exists(first_splits_path):
        os.makedirs(first_splits_path, exist_ok=True)
    
    # Concatenate train and dev into one file
    train_full_file = os.path.join(first_splits_path, 'train_full.conllu')
    join_train_dev(train_path=train_file, dev_path=dev_file, output_path=train_full_file)
    # Split train_full_file randomly into `split_count` sub sets (roughly equal size blocks)
    splitting(input_file=train_full_file, output_dir=first_splits_path, split_file=split_csv_file, 
              block_count=block_count, split_count=split_count, seed=seed)

    # Divide files to dev - test - train, save into crossvalidation folder
    if not os.path.exists(crossval_split_path):
        os.makedirs(crossval_split_path, exist_ok=True)
    split_conllu_files = [fname for fname in os.listdir(first_splits_path) if fname.endswith('.conllu')]
    split_conllu_files.remove('train_full.conllu')
    
    # CSV file with logging/debugging info
    splits_csv = open(os.path.join(crossval_split_path, split_csv_file), 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(splits_csv)
    csv_writer.writerow(['split', 'dev', 'test', 'train'])
    
    # Rotating splits
    for i in range(len(split_conllu_files)):
        split_key = '{:02d}'.format(i+1)
        print(split_key)

        dev = split_conllu_files[i]
        if i == len(split_conllu_files) - 1:
            test = split_conllu_files[0]
            train = split_conllu_files[1:len(split_conllu_files) - 1]
        else:
            test = split_conllu_files[i+1]
            train = split_conllu_files[i + 2:] + split_conllu_files[:i]

        csv_writer.writerow([i+1, dev, test, train])
        
        # Create new splits into crossvalidation data folder
        with open(os.path.join(crossval_split_path, '{}_dev.conllu'.format(split_key)), 'w', encoding='utf-8') as fout:
            fout.write(join_file_contents(first_splits_path, [dev]))

        with open(os.path.join(crossval_split_path, '{}_test.conllu'.format(split_key)), 'w', encoding='utf-8') as fout:
            fout.write(join_file_contents(first_splits_path, [test]))

        with open(os.path.join(crossval_split_path, '{}_train.conllu'.format(split_key)), 'w', encoding='utf-8') as fout:
            fout.write(join_file_contents(first_splits_path, train))

        with open(os.path.join(crossval_split_path, '{}_train_all.conllu'.format(split_key)), 'w', encoding='utf-8') as fout:
            train_all = train + [dev]
            fout.write(join_file_contents(first_splits_path, train_all))

    splits_csv.close()


def create_smaller_data_splits(train_file, dev_file, first_splits_path, smaller_data_split_path,
                               split_csv_file='splits.csv', block_count=195, split_count=10, seed=9):
    '''
    Creates dataset size increasing crossvalidation splits based on given input CONLLU files 
    (`train_file` and `dev_file`). 
    First, concatenates train_file and dev_file into one file and saves under first_splits_path.
    Then splits the concatenated conllu file randomly into `split_count` sub sets. 
    
    The splitting process: 1) the input is first split at the word-level into roughly 
    equal-sized blocks (`block_count` blocks), 2) the order of blocks is shuffled, and 
    3) the shuffling result is split into `split_count` sub sets. 
    
    Saves initial sub sets into folder `first_splits_path`. 
    
    Creates `split_count` training sets with gradually increasing size: first set contains 
    only 1 sub set from `first_splits_path`, second set contains 2 sub sets from `first_splits_path`, 
    and so on. 
    In the process, these training sets ("train_all" sets) will be further split into train and 
    dev subsets, with increasing dev set sizes / proportions: 10% if training consist of 1-3 sub sets, 
    15% if training consists of 4-6 sub sets, and 20% if training is larger than 6 sub sets.
    Finally, saves results (sub sets with increasing sizes) into folder `smaller_data_split_path`. 
    '''
    if not os.path.exists(train_file) or not os.path.isfile(train_file):
        raise FileNotFoundError(f'(!) Missing or invalid input file {train_file}')
    if not os.path.exists(dev_file) or not os.path.isfile(dev_file):
        raise FileNotFoundError(f'(!) Missing or invalid input file {dev_file}')
    if not os.path.exists(first_splits_path):
        os.makedirs(first_splits_path, exist_ok=True)
    
    # Concatenate train and dev into one file
    train_full_file = os.path.join(first_splits_path, 'train_full.conllu')
    join_train_dev(train_path=train_file, dev_path=dev_file, output_path=train_full_file)
    # Split train_full_file randomly into `split_count` sub sets (roughly equal size blocks)
    splitting(input_file=train_full_file, output_dir=first_splits_path, split_file=split_csv_file, 
              block_count=block_count, split_count=split_count, seed=seed)

    if not os.path.exists(smaller_data_split_path):
        os.makedirs(smaller_data_split_path, exist_ok=True)

    # read all splits to list:
    undivided_splits = [fname for fname in os.listdir(first_splits_path) if fname.endswith('.conllu')]
    undivided_splits.remove('train_full.conllu')

    # CSV file with logging/debugging info
    splits_csv = open(os.path.join(smaller_data_split_path, split_csv_file), 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(splits_csv)
    csv_writer.writerow(['split', 'train'])

    def create_train_dev(training_whole, development_percentage):
        divider = len(training_whole) // 100 * (100 - development_percentage)  # point between train and dev
        training_train = training_whole[:divider]
        training_dev = training_whole[divider:]
        return training_train, training_dev

    for j in range(len(undivided_splits), 0, -1):
        split_key = '{:03d}'.format(j*10)
        print(split_key)
    
        # save splits by sentence-ids
        csv_writer.writerow([split_key, undivided_splits])

        # % of sentences to be divided for development
        dev_percentage = 20
        if j in [6, 5, 4]:
            dev_percentage = 15
        elif j in [3, 2, 1]:
            dev_percentage = 10

        # Get conllu TokenLists from IDs
        data = ''
        for filename in undivided_splits:
            with open(os.path.join(first_splits_path, filename), "r", encoding="utf-8") as split:
                data += split.read()

        training_whole = conllu.parse(data)

        training_train, training_dev = create_train_dev(training_whole, dev_percentage)

        assert len(training_dev) + len(training_train) == len(training_whole)
        
        with open(os.path.join(smaller_data_split_path, f'{split_key}_train_all.conllu'), 'w', encoding='utf-8') as tr:
            tr.write(create_conllu(training_whole))
        with open(os.path.join(smaller_data_split_path, f'{split_key}_train.conllu'), 'w', encoding='utf-8') as tr:
            tr.write(create_conllu(training_train))
        with open(os.path.join(smaller_data_split_path, f'{split_key}_dev.conllu'), 'w', encoding='utf-8') as dev:
            dev.write(create_conllu(training_dev))
        undivided_splits.pop( random.Random(4).randrange(len(undivided_splits)) )
        random.Random(4).shuffle( undivided_splits )
    
    splits_csv.close()


def create_half_data_splits(train_file, dev_file, first_splits_path, half_data_split_path,
                            split_csv_file='splits.csv', seed=9):
    '''
    Creates half training set size crossvalidation splits based on given input CONLLU files 
    (`train_file` and `dev_file`). 
    First, concatenates `train_file` and `dev_file` into one file and saves under 
    `first_splits_path`.

    The splitting process: 1) the concatenated conllu file is first split into 194 blocks of 
    sentences, each block roughly same size in words. 
    2) blocks are shuffled and two different train-dev-test splits are formed, with sizes: 
    78 blocks for train, 19 for dev and 97 test (one selects first half for train-dev, other
    selects the second half for train-dev).
    3) step 2 gets repeated 5 times, resulting in 10 splits at total.

    Finally, saves results (sub sets with halved train sizes) into folder `half_data_split_path`. 
    '''
    # Validate inputs
    if not os.path.exists(train_file) or not os.path.isfile(train_file):
        raise FileNotFoundError(f'(!) Missing or invalid input file {train_file}')
    if not os.path.exists(dev_file) or not os.path.isfile(dev_file):
        raise FileNotFoundError(f'(!) Missing or invalid input file {dev_file}')
    if not os.path.exists(first_splits_path):
        os.makedirs(first_splits_path, exist_ok=True)
    
    # Concatenate train and dev into one file
    train_full_file = os.path.join(first_splits_path, 'train_full.conllu')
    join_train_dev(train_path=train_file, dev_path=dev_file, output_path=train_full_file)
    
    # Extract all tokens and label them with sentence id-s
    all_sentences = []
    with open(train_full_file, 'r', encoding='utf-8') as in_f:
        all_sentences = conllu.parse( in_f.read() )
    assert len(all_sentences) > 0
    full_tokenlist = list()
    for i, sentence in enumerate(all_sentences):
        full_tokenlist.extend([i] * len(sentence))
    
    # Splitting given number of sentence blocks, organizing by sentence id-s 
    # (block_count=194 results in splits of about ~~2000 words)
    sentence_blocks = correct_splits(split(full_tokenlist, 194))
    
    def extract_sentences(tokenlists, train, dev, test):
        train_sents = [tokenlists[no] for block in train for no in block]
        test_sents = [tokenlists[no] for block in test for no in block]
        dev_sents = [tokenlists[no] for block in dev for no in block]
        return train_sents, dev_sents, test_sents

    def save_split_files(train, dev, test, output_path, split_no):
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        with open(os.path.join(output_path, '{}_dev.conllu'.format(split_no)), 'w', encoding='utf-8') as fout:
            fout.write(create_conllu(dev))

        with open(os.path.join(output_path, '{}_test.conllu'.format(split_no)), 'w', encoding='utf-8') as fout:
            fout.write(create_conllu(test))

        with open(os.path.join(output_path, '{}_train.conllu'.format(split_no)), 'w', encoding='utf-8') as fout:
            fout.write(create_conllu(train))
        
        join_train_dev(train_path=os.path.join(output_path, '{}_train.conllu'.format(split_no)), 
                       dev_path=os.path.join(output_path, '{}_dev.conllu'.format(split_no)), 
                       output_path=os.path.join(output_path, '{}_train_all.conllu'.format(split_no)))
    
    # CSV file with logging/debugging info
    splits_csv = open(os.path.join(half_data_split_path, split_csv_file), 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(splits_csv)
    csv_writer.writerow(['split', 'dev', 'test', 'train'])

    # Split corresponding sentence sequence numbers of full train data
    rnd = random.Random(seed)
    split_counter = 0
    saved_splits = dict()  
    for i in range(1, 6, 1):
        rnd.shuffle(sentence_blocks)

        # 19 blocks for dev
        train_1 = sentence_blocks[:78]
        dev_1 = sentence_blocks[78:97]
        test_1 = sentence_blocks[97:]

        train_2 = sentence_blocks[97:175]
        dev_2 = sentence_blocks[175:]
        test_2 = sentence_blocks[:97]

        split_key = '{:03d}'.format(split_counter+1)
        print(f'{split_key} -- train: #{len(train_1)} sents, dev: #{len(dev_1)} sents, test: #{len(test_1)} sents')
        split_counter += 1
        csv_writer.writerow(['split_{}'.format(split_key), dev_1, test_1, train_1])
        train, dev, test = extract_sentences(all_sentences, train_1, dev_1, test_1)
        save_split_files(train, dev, test, half_data_split_path, split_key)

        split_key = '{:03d}'.format(split_counter+1)
        print(f'{split_key} -- train: #{len(train_2)} sents, dev: #{len(dev_2)} sents, test: #{len(test_2)} sents')
        split_counter += 1
        csv_writer.writerow(['split_{}'.format(split_key), dev_2, test_2, train_2])
        train, dev, test = extract_sentences(all_sentences, train_2, dev_2, test_2)
        save_split_files(train, dev, test, half_data_split_path, split_key)

    splits_csv.close()


def create_single_file_split(input_file, output_dir, train=80, dev=10, test=10, subset_size=None, shuffle=False, seed=9):
    '''
    Splits single conllu file (sentence-wise) into train, dev and test sub sets. 
    Writes sub sets into separate files. 
    Parameters train, dev, and test correspond to relative sizes of 
    corresponding sub sets and must add up to 100. 
    
    If shuffle=True, then sentences in the file will be shuffled before
    making the split.
    
    If subset_size is specified, then only the given amount of sentences 
    will be taken for splitting (applied after shuffling, if shuffling is 
    enabled).
    
    This function is used for testing and debugging model training.
    '''
    if train+dev+test != 100:
        raise ValueError( f'(!) Parameter values train + dev + test ({train} + {dev} + {test}) '+\
                          f'do not add up to 100.' )
    all_sentences = []
    with open(input_file, 'r', encoding='utf-8') as in_f:
        all_sentences = conllu.parse( in_f.read() )
    if shuffle:
        random.Random(seed).shuffle(all_sentences)
    if subset_size is not None:
        assert isinstance(subset_size, int)
        if subset_size > len(all_sentences):
            raise ValueError( f'(!) subset_size={subset_size} exceeds the number '+\
                              f'of sentences in {input_file!r} ({len(all_sentences)}).' )
        all_sentences = all_sentences[:subset_size]
    # Split sentences into train, dev, test
    collected_train = []
    collected_dev   = []
    collected_test  = []
    for i in range(len(all_sentences)):
        percentage = int(i*100.0/len(all_sentences))
        if percentage < train:
            collected_train.append( all_sentences[i] )
        elif percentage >= train and percentage < train+dev:
            collected_dev.append( all_sentences[i] )
        else:
            collected_test.append( all_sentences[i] )
    # Sanity check
    assert len(collected_train) + len(collected_dev) + len(collected_test) == len(all_sentences)
    # Write outputs
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f'train.conllu'), 'w', encoding='utf-8') as tr:
        tr.write(create_conllu(collected_train))
        print( f'{len(collected_train)} sentences for training.')
    with open(os.path.join(output_dir, f'dev.conllu'), 'w', encoding='utf-8') as dv:
        dv.write(create_conllu(collected_dev))
        print( f'{len(collected_dev)} sentences for development.')
    with open(os.path.join(output_dir, f'test.conllu'), 'w', encoding='utf-8') as tst:
        tst.write(create_conllu(collected_test))
        print( f'{len(collected_test)} sentences for test.')


# ===============================================================
#  Utilities required by splitting functions
# ===============================================================

def join_train_dev(train_path, dev_path, output_path):
    """
    Concatenates two conllu files into one file. 
    It is used to concatenate train and dev files. 
    """
    with open(output_path, 'w', encoding='utf-8') as fout:
        train_file = open(train_path, 'r', encoding='utf-8')
        dev_file = open(dev_path, 'r', encoding='utf-8')
        fout.write(train_file.read())
        fout.write(dev_file.read())
    train_file.close()
    dev_file.close()


def join_file_contents(input_path: str, filenames: list):
    '''
    Reads contents of given (conllu) files from input_path and returns their concatenation.
    TODO: merge `join_train_dev` and `join_file_contents` into one function
    '''
    data = ''
    for filename in filenames:
        with open(os.path.join(input_path, filename), 'r', encoding='utf-8') as fin:
            data += fin.read()
    return data


def split(a, n):
    """
    Splits list `a` into `n` roughly equal-sized subsets.
    If `a` is not exactly divisible by `n`, then finds the
    reminder `r` of the division and enlarges sizes of first 
    `r` subsets by 1. 
    Returns a generator of the split. 
    
    Examples:
    
    >>> sp1 = split([1,1,2,2,3,3], 3)
    >>> list(sp1)
    [[1, 1], [2, 2], [3, 3]]
    >>> sp2 = split([1,2,2,3,3,3,4,4,4,4,5,5,5,5,5], 6)
    >>> list(sp2)
    [[1, 2, 2], [3, 3, 3], [4, 4, 4], [4, 5], [5, 5], [5, 5]]
    >> sp3 = split([[1], [2,2], [3,3,3], [4,4,4,4]], 3)
    >> list(sp3)
    [[[1], [2, 2]], [[3, 3, 3]], [[4, 4, 4, 4]]]
    """
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def correct_splits(splits):
    """
    Corrects given splits (lists of lists of sentence id-s) in a way that 
    each sentence id can only be in one sub list. Motivation: each sentence 
    should belong to exactly one cross-validation subset.
    
    The input is a list of lists, where each sub list element is the number 
    of sentence the word belongs to, e.g [1, 1, 1, 2, 2, 3, 3, 3]. 
    Assumingly, the division of corpus words into sub lists has been done with 
    function `split(a, n)`. 
    Returns list of lists, where each sublist contains unique id-s of sentences 
    and one sentence id can be in one list only.
    
    When run with the default settings (Estonian UD train+dev split into 195 
    sub sets), then each sub list will have the size of (approx) 2000 words.
    """
    splits = list(splits)  # convert generator to list
    last_sentences_set = set()  # for sanity checking
    sentence_splits = []
    
    for i, subsplit in enumerate(splits):
        current_sentences_set = set(subsplit)

        if i == 0:  # Has no previous sentence
            sentence_splits.append(sorted(list(current_sentences_set)))
            last_sentences_set = current_sentences_set
            continue

        # If first sentence of is not complete (is in previous list, too), remove it from current list.
        last_id = splits[i - 1][-1]
        if last_id in current_sentences_set:
            current_sentences_set.remove(last_id)

        assert len(current_sentences_set.intersection(last_sentences_set)) == 0

        sentence_splits.append(sorted(list(current_sentences_set)))  # sort to keep correct order
        
        last_sentences_set = current_sentences_set

    return sentence_splits


def create_conllu(tokenlists):
    """Serializes given TokenLists into conllu string that can be written to file."""
    conllu_list = []
    for sentence in tokenlists:
        conllu_list.append(sentence.serialize())
    return ''.join(conllu_list)


def splitting(input_file, output_dir, split_file, block_count=195, split_count=10, seed=0):
    """
    Splits `input_file` (a large conllu file) randomly into `split_count` sub sets.
    The splitting process: 1) the input is first split at the word-level into roughly 
    equal-sized blocks (`block_count` blocks), 2) the order of blocks is shuffled, and 
    3) the shuffling result is split into `split_count` sub sets.

    The split data will be written into `output_dir`, and each sub set of the split will 
    be written into separate file named 'split_{split_nr}.conllu'. 
    Ordered blocks of sentence id-s of each split will be written into `split_file`.

    When run with the default settings (input is Estonian UD TreeBank train+dev, 
    block_count=195, split=10, and seed=9), then each block will have a size of approx 
    2000 words, and each final split contains roughly 2500-3000 sentences.

    :param input_file: input conllu file
    :param output_dir: directory for generated splits
    :param split_file: name for csv where to save data about splits (ordered sentence IDs)
    :param block_count: number of blocks of sentences to split data into
    :param split_count: number of final splits
    :param seed: seed value to be used for reproducibility
    :return: none
    """

    split_file = open(os.path.join(output_dir, split_file), 'w', newline='', encoding='utf-8')
    input_file = open(input_file, 'r', encoding='utf-8')
    writer = csv.writer(split_file)

    all_sentences = conllu.parse(input_file.read())
    full_tokenlist = list()
    for i, sentence in enumerate(all_sentences):
        full_tokenlist.extend([i] * len(sentence))
    input_file.close()

    # Splitting given number of sentence blocks, organizing by sentence id-s 
    # (block_count=195 results in splits of about 2000 words)
    sentence_blocks = correct_splits(split(full_tokenlist, block_count))
    random.Random(seed).shuffle(sentence_blocks)

    training_splits = list(split(sentence_blocks, split_count))  # List of sentence blocks divided to 10

    #training_split_map = dict()
    for j, training_split in enumerate(training_splits, 1):
        # Get conllu TokenLists corresponding to sentence IDs
        training_whole = []
        for block in training_split:
            training_whole.extend([all_sentences[id] for id in block])
        with open(os.path.join(output_dir, 'split_{}.conllu'.format(str(j))), 'w', encoding='utf-8') as tr:
            tr.write(create_conllu(training_whole))
        writer.writerow([str(j), training_split])
        #training_split_map[j] = training_split

    split_file.close()
    #return training_split_map


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    # Try to execute all input files as configurations
    for conf_file in sys.argv[1:]:
        create_train_splits_joins_main( conf_file )

