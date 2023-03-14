## Syntax ablation experiments

### Pre-requisites

* Install [estnltk](https://github.com/estnltk/estnltk) (version 1.7.2+ is required);
* Install [stanza](https://github.com/stanfordnlp/stanza) (we used version 1.4.2);
* Install [scikit-learn](https://scikit-learn.org/) (we used version 1.2.1);
* For some of the experiments, you'll also need [MaltParser](https://maltparser.org), [MaltOptimizer](http://nil.fdi.ucm.es/maltoptimizer), [UDPipe-1](https://ufal.mff.cuni.cz/udpipe/1) and [gensim](https://radimrehurek.com/gensim);
* For visualization of the results, you'll need [matplotlib](https://matplotlib.org/stable/), [seaborn](https://seaborn.pydata.org/), [plotnine](https://plotnine.readthedocs.io/en/stable/); 
* Download and unpack [Estonian UD corpus](https://github.com/UniversalDependencies/UD_Estonian-EDT/tags) (most experiments were conducted with the corpus version 2.6, the version 2.11 was used for one experiment);

### Configuration files

Most important settings of data pre-processing, training and evaluation are defined in configuration INI files. You can find these files in [confs](confs/) folder. In order to run a processing step, pass name of an INI file as an argument to the script.

### Processing steps (scripts)

* `01_ud_preprocessing.py` -- Converts gold standard UD corpus to EstNLTK's format: overwrites values of `lemma`, `upos`, `xpos` and `feats` with EstNLTK's automatic morphological analyses (from layers `morph_analysis` / `morph_extended` / `ud_morph_analysis`).  Alternatively, you can also skip the conversion altogether and just clean the gold standard files and copy to the experiments folder. Executes all sections starting with `preannotation_` and `copy_` in input configuration file. Example usage:

	* `python  01_ud_preprocessing.py  confs/conf_edt_v26_Stanza_ME_full.ini`

* `01b_extract_clauses.py` -- Splits sentences in CONLLU files into clauses (with EstNLTK's ClauseTagger). Cleans clauses (removes conjunctions and punctuation at the beginning and/or at the end of a clause), and exports cleaned clauses as CONLLU files. Executes all sections starting with `extract_clauses_` in input configuration file. This is a preprocessing step required by _syntax sketches knockout experiments_. Example usage:

	* `python  01b_extract_clauses.py  confs/conf_edt_v26_Stanza_ME_sketches_knockout_5_groups.ini`

* `01c_analyse_sketches.ipynb` -- computes sketches from the whole corpus and provides (descriptive) data analysis of sketches. Optional step in _syntax sketches knockout experiments_.

* `01d_prepare_sketches.py` -- Creates frequency table of syntax sketches, and prepares datasets for sketches knockout experiments: removes clauses corresponding to sketches systematically from train, dev and test sets. Executes sections in the configuration starting with prefix `make_sketches_table_` and `prepare_knockout_`. This is a preprocessing step required by _syntax sketches knockout experiments_. Example usage: 

	* `python  01d_prepare_sketches.py  confs/conf_edt_v26_Stanza_ME_sketches_knockout_5_groups.ini`

* `02_split_data.py` -- Creates data splits (or joins) for model training and evaluation. Executes all sections starting with `split_` and `join_` in input configuration file. Example usage:

	* `python  02_split_data.py  confs/conf_edt_v26_Stanza_ME_full.ini`

* `02b_make_gaps.py` -- Modifies conllu files for gap experiments: deletes a combination of fields `form`, `lemma`, `upos`, `xpos`, `feats` from files, and writes files with deletions to a new location. For implemented modifications, see the header comment of the script. Executes all sections starting with `modify_conllu_` in input configuration file. Example usage:

	* `python  02b_make_gaps.py  confs/conf_edt_v26_Stanza_ME_gap_experiments.ini`

* `03_train_stanza.py` -- Trains stanza parser models. Executes all sections starting with `train_stanza_` in input configuration file. Example:

	* `python  03_train_stanza.py  confs/conf_edt_v26_Stanza_ME_full.ini`

* `03b_optimize_malt.py` -- Optimizes MaltParser before training: produces feature selection files. Requires Python 2.7. Executes all sections starting with `maltoptimize_` in input configuration file. Example:

	* `python  03b_optimize_malt.py  confs/conf_edt_v26_MaltParser_ME_full.ini`

* `03c_train_malt_udpipe.py` -- Trains MaltParser and/or UDPipe-1 models. Executes all sections starting with `train_malt_` and `train_udpipe1_` in input configuration file. Example:

	* `python  03c_train_malt_udpipe.py  confs/conf_edt_v26_MaltParser_ME_full.ini`

* `04_predict_stanza.py` -- Applies trained stanza parser models on evaluation data to get predictions. Writes predictions to conllu files. Executes all sections starting with `predict_stanza_` in input configuration file. Example:

	* `python  04_predict_stanza.py  confs/conf_edt_v26_Stanza_ME_full.ini`

* `04b_predict_malt_udpipe.py` -- Applies trained MaltParser and/or UDPipe-1 models on evaluation data to get predictions. Writes predictions to conllu files. Executes all sections starting with `predict_malt_` and `predict_udpipe1_` in input configuration file. Example:

	* `python  04b_predict_malt_udpipe.py  confs/conf_edt_v26_MaltParser_ME_full.ini`

* `05_evaluate.py` -- Evaluates predictions: compares predicted files to gold standard files and calculates LAS/UAS scores. Executes all sections starting with `eval_` in given configuration files (multiple INI files can be given as an input). Writes results into file `results.csv` in a sub directory closest to the execution directory (for given configurations, the path will be: `edt_2.6/results.csv`). You can also give name of the output csv file as an input argument of the script. Example usage:

	* `python  05_evaluate.py  confs/conf_edt_v26_MaltParser_ME_full.ini  results_maltparser.csv`

Note: configurations also contain overlapping parts, e.g. once you've run UD preprocessing with `confs/conf_edt_v26_Stanza_ME_full.ini`, you do not need to run UD preprocessing again with `confs/conf_edt_v26_stanza_ME_ensemble_full.ini`;

### Results and further studies


* [06_result_tables.ipynb](06_result_tables.ipynb) -- tables with the experiment results read from CSV files;

* [07_smaller_data_exp_and_extrapolation.ipynb](07_smaller_data_exp_and_extrapolation.ipynb) -- draw figures about smaller data experiments (experiments where training set size is gradually increased) and extrapolate the results;

* [08_results_sketches_knockout_5groups.ipynb](08_results_sketches_knockout_5groups.ipynb) -- results of the _syntax sketches knockout experiments_;