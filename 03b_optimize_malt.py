#
#  Runs MaltOptimizer according to given configuration.
#  This is an optimization step before training MaltParser.
#
#  Requirements:
#     Perl and Linux command line
#     Python 2.7 (because optimizer uses some legacy scripts)
#     Maltparser from https://maltparser.org/index.html
#     MaltOptimizer from http://nil.fdi.ucm.es/maltoptimizer/
#     input conllu files without ANY sentence metadata (otherwise phase 1 will hang)
#

from datetime import datetime
import subprocess
import os, os.path
import sys, re

if not (sys.version_info[0] == 2 and sys.version_info[1] == 7):
    raise Exception('(!) Unexpected Python version. MaltOptimizer script is only runnable with Python 2.7.')

import ConfigParser  # specific to Python 2.7

# Change to local paths & files, if required
maltoptimizer_dir = 'MaltOptimizer-1.0.3'
maltparser_jar    = 'maltparser-1.9.2.jar'
maltoptimizer_jar = 'MaltOptimizer.jar'

def run_maltoptimizer_main( conf_file, verbose=True ):
    '''
    Runs maltoptimizer which provides feature selection before MaltParser training. 
    Settings/parameters will be read from the given `conf_file`. 
    Executes sections in the configuration starting with 'maltoptimize_'. 
    '''
    # Parse configuration file
    config = ConfigParser.ConfigParser()
    if conf_file is None or not os.path.exists(conf_file):
        raise Exception("Config file {} does not exist".format(conf_file))
    if len(config.read(conf_file)) != 1:
        raise ValueError("File {} is not accessible or is not in valid INI format".format(conf_file))
    start = datetime.now()
    section_found = False
    for section in config.sections():
        if section.startswith('maltoptimize_'):
            # input_files -- one file or a list of files (with full paths) separated by ;
            if not config.has_option(section, 'input_files'):
                raise ValueError('Error in %s: section %s is missing "input_files" parameter.' % (conf_file, section) )
            input_files = config.get(section, 'input_files')
            if ',' in input_files:
                input_files = [fname.strip() for fname in input_files.split(',')]
            elif ';' in input_files:
                input_files = [fname.strip() for fname in input_files.split(';')]
            else:
                input_files = [input_files]
            # output_dir -- dir where to but finalOptionsFile.xml & [featureFile.xml]
            if not config.has_option(section, 'output_dir'):
                raise ValueError('Error in %s: section %s is missing "output_dir" parameter.' % (conf_file, section) )
            output_dir = config.get(section, 'output_dir')
            conll_file_pat = None
            conll_file_regexp = None
            # Customize sub-experiment pattern (if required)
            if config.has_option(section, 'conll_file_pat'):
                conll_file_pat = config.get(section, 'conll_file_pat')
                # Convert file pattern to regular experssion
                if not isinstance(conll_file_pat, basestring):
                    raise TypeError('conll_file_pat must be a string')
                try:
                    conll_file_regexp = re.compile(conll_file_pat)
                except Exception as err:
                    raise ValueError('Unable to convert {!r} to regexp'.format(conll_file_pat))
                if 'exp' not in conll_file_regexp.groupindex:
                    raise ValueError('Regexp {!r} is missing named group "exp"'.format(conll_file_pat))
            # Run optimizer on all input files
            for input_file in input_files:
                sub_exp=''
                if conll_file_regexp is not None:
                    m = conll_file_regexp.match( input_file )
                    if m:
                        sub_exp = m.group('exp')
                    else:
                        raise ValueError('Input file {!r} does not match pattern {!r}').format(input_file, conll_file_pat)
                optimize_maltparser(input_file, output_dir=output_dir, sub_exp=sub_exp)
            section_found = True
    if section_found:
        print('Total processing time: %s' % (datetime.now()-start))
    else:
        print('No section starting with "maltoptimize_" in %s.' % (conf_file))

def optimize_maltparser(input_conll_file, output_dir=None, sub_exp=''):
    '''
    Runs MaltOptimizer.jar on given input_conll_file (dev dataset).
    
    See also: 
      https://github.com/estnltk/maltparser_training
      https://github.com/estnltk/syntax_experiments/blob/devel/03_create_training_testing_data/MaltOptimizer-1.0.3/optimize_maltparser.py
    '''
    global maltoptimizer_dir, maltparser_jar, maltoptimizer_jar
    
    # Make input file path absolute
    # (otherwise maltparser fails to load the file)
    if input_conll_file != os.path.abspath(input_conll_file):
        input_conll_file = os.path.abspath(input_conll_file)
    
    phase1 = 'java -jar %s -p 1 -m %s -c %s' % (maltoptimizer_jar, maltparser_jar, input_conll_file)
    subprocess.call(phase1, shell=True, cwd=maltoptimizer_dir)

    phase2 = 'java -jar %s -p 2 -m %s -c %s' % (maltoptimizer_jar, maltparser_jar, input_conll_file)
    subprocess.call(phase2, shell=True, cwd=maltoptimizer_dir)

    phase3 = 'java -jar %s -p 3 -m %s -c %s' % (maltoptimizer_jar, maltparser_jar, input_conll_file)
    subprocess.call(phase3, shell=True, cwd=maltoptimizer_dir)

    phase3_optFile = os.path.join(maltoptimizer_dir, 'phase3_optFile.txt')
    with open(phase3_optFile, 'r' ) as f:
        lines = [l for l in f.read().split('\n') if len(l) > 0]
    feature_model = lines[-1].split(':')[-1]

    if output_dir is not None:
        # move the files to correct place:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        os.rename(os.path.join(maltoptimizer_dir, 'finalOptionsFile.xml'), 
                  os.path.join(output_dir, 'finalOptionsFile%s.xml' % sub_exp))
        if os.path.isfile(os.path.join(maltoptimizer_dir, feature_model)):
            os.rename(os.path.join(maltoptimizer_dir, feature_model), 
                      os.path.join(output_dir, 'featureFile%s.xml' % sub_exp))


if __name__ == '__main__':
    # First, check that required folders and jar files are present
    if not os.path.isdir(maltoptimizer_dir):
        raise Exception( ('Missing directory: \%s. Please get MaltOptimizer from: http://nil.fdi.ucm.es/maltoptimizer/') % (maltoptimizer_dir) )
    malt_dir_files = list(os.listdir(maltoptimizer_dir))
    if maltparser_jar not in malt_dir_files:
        jar_path = os.path.join(maltoptimizer_dir, maltparser_jar)
        raise Exception( ('Missing jar file: \%s. Please get MaltParser from: https://maltparser.org/index.html') % (jar_path) )
    if maltoptimizer_jar not in malt_dir_files:
        jar_path = os.path.join(maltoptimizer_dir, maltoptimizer_jar)
        raise Exception( ('Missing jar file: \%s. Please get MaltOptimizer from: http://nil.fdi.ucm.es/maltoptimizer/') % (jar_path) )
    # Get parameters from command line
    if len(sys.argv) < 2:
        raise Exception('(!) Missing input argument: name of the configuration INI file.')
    conf_file = sys.argv[1]
    run_maltoptimizer_main( conf_file, verbose=True )
