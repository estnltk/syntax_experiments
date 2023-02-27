#
#  Splits sentences in CONLLU files into clauses (with EstNLTK's ClauseTagger).
#  Cleans clauses (removes conjunctions and punctuation at the beginning or at 
#  the end of the clause), and exports cleaned clauses as CONLLU files.
#
#  Requires estnltk 1.7.2+
#

import os
import sys
import configparser
from datetime import datetime

from estnltk.converters.conll.conll_importer import conll_to_text

from syntax_sketches.syntax_sketch import clean_clause
from syntax_sketches.clause_export import export_cleaned_clause

def extract_clauses( conf_file ):
    '''
    Splits sentences in CONLLU files into clauses with EstNLTK, 
    cleans clauses and saves as new CONLLU files.
    Inputs/outputs and parameters of the processing will be read 
    from the given `conf_file`. 
    Executes sections in the configuration starting with prefix 
    'extract_clauses_'. 
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
        if section.startswith('extract_clauses_'):
            section_found = True
            print(f'Performing {section} ...')
            # Collect clause tagging parameters
            if not config.has_option(section, 'input_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "input_dir" parameter.')
            input_dir = config[section]['input_dir']
            if not os.path.isdir(input_dir):
                raise FileNotFoundError(f'Error in {conf_file}: invalid "input_dir" value {input_dir!r} in {section!r}.')
            if not config.has_option(section, 'output_dir'):
                raise ValueError(f'Error in {conf_file}: section {section!r} is missing "output_dir" parameter.')
            output_dir = config[section]['output_dir']
            if input_dir == output_dir:
                raise ValueError(f'Error in {conf_file}: section {section!r} "output_dir" cannot be same as "input_dir".')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            remove_empty_nodes = config[section].getboolean('remove_empty_nodes', True)
            skip_list = config[section].get('skip_list', '')
            if len(skip_list) > 0:
                skip_list = skip_list.split(',')
                skip_list = [fname.strip() for fname in skip_list]
            for fname in os.listdir(input_dir):
                if fname in skip_list:
                    continue
                fpath = os.path.join(input_dir, fname)
                if os.path.isfile(fpath) and fname.endswith('.conllu'):
                    text_obj = conll_to_text( fpath, 'ud_syntax', remove_empty_nodes=remove_empty_nodes )
                    print('Tagging clauses in: ', fname)
                    text_obj.tag_layer('clauses')
                    expected_layers = {
                        'clauses', 'compound_tokens', 'morph_analysis',
                        'sentences', 'tokens', 'ud_syntax', 'words'
                    }
                    assert text_obj.layers == expected_layers, 'Unexpected layers'

                    print('Writing out results to: ', output_dir)
                    output_fname = os.path.join(output_dir, fname)
                    valid_clauses = 0
                    invalid_clauses = 0
                    output_file = open(output_fname, 'wt', encoding='utf-8')  
                    for clause in text_obj.clauses:
                        cleaned_clause = clean_clause(clause)
                        
                        if len(cleaned_clause['root_loc']) != 1:
                            invalid_clauses += 1
                            continue
                        
                        if valid_clauses > 0:
                            output_file.write('\n\n')
                        
                        output_file.write(export_cleaned_clause(cleaned_clause))
                        valid_clauses += 1
                    
                    print('Valid clauses:   {}'.format(valid_clauses))
                    print('Invalid clauses: {} (missing root)'.format(invalid_clauses))
                    output_file.close()
    if section_found:
        print(f'Total processing time: {datetime.now()-start}')
    else:
        print(f'No section starting with "extract_clauses_" in {conf_file}.')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    # Try to execute all input files as configurations
    for conf_file in sys.argv[1:]:
        extract_clauses( conf_file )


