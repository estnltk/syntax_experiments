## Syntax ablation experiments

### Pre-requisites

* Install [estnltk](https://github.com/estnltk/estnltk) (version 1.7.2+ is required);
* Install [stanza](https://github.com/stanfordnlp/stanza) (we used version 1.4.2);
* For some of the experiments, you'll also need MaltParser, MaltOptimizer, and UDPipe-1; 
* Download and unpack [Estonian UD corpus](https://github.com/UniversalDependencies/UD_Estonian-EDT/tags) (we used version 2.6);

### Configuration files

Most important settings of data pre-processing, training and evaluation are defined in configuration INI files. In order to run a processing step, pass name of an INI file as an input to the script.

### Processing steps (scripts)

* `01_ud_preprocessing.py` -- Converts gold standard UD corpus to EstNLTK's format: overwrites values of `lemma`, `upos`, `xpos` and `feats` with EstNLTK's automatic morphological analyses (from layers `morph_analysis` / `morph_extended` / `ud_morph_analysis`).  Alternatively, you can also skip the conversion altogether and just clean the gold standard files and copy to the experiments folder. Executes all sections starting with `preannotation_` and `copy_` in input configuration file. Example usage:

	* `python  01_ud_preprocessing.py  conf_edt_v26_Stanza_ME_full.ini`

* `02_split_data.py` -- Creates data splits (or joins) for model training and evaluation. Executes all sections starting with `split_` and `join_` in input configuration file. Example usage:

	* `python  02_split_data.py  conf_edt_v26_Stanza_ME_full.ini`

* `02b_make_gaps.py` -- Modifies conllu files for gap experiments: deletes a combination of fields `form`, `lemma`, `upos`, `xpos`, `feats` from files, and writes files with deletions to a new location. For implemented modifications, see the header comment of the script. Executes all sections starting with `modify_conllu_` in input configuration file. Example usage:

	* `python  02b_make_gaps.py  conf_edt_v26_Stanza_ME_gap_experiments.ini`

* `03_train_stanza.py` -- Trains stanza parser models. Executes all sections starting with `train_stanza_` in input configuration file. Example:

	* `python  03_train_stanza.py  conf_edt_v26_Stanza_ME_full.ini`

* `03b_optimize_malt.py` -- Optimizes MaltParser before training: produces feature selection files. Requires Python 2.7. Executes all sections starting with `maltoptimize_` in input configuration file. Example:

	* `python  03b_optimize_malt.py  conf_edt_v26_MaltParser_ME_full.ini`

* `03c_train_malt_udpipe.py` -- Trains MaltParser and/or UDPipe-1 models. Executes all sections starting with `train_malt_` and `train_udpipe1_` in input configuration file. Example:

	* `python  03c_train_malt_udpipe.py  conf_edt_v26_MaltParser_ME_full.ini`

* `04_predict_stanza.py` -- Applies trained stanza parser models on evaluation data to get predictions. Writes predictions to conllu files. Executes all sections starting with `predict_stanza_` in input configuration file. Example:

	* `python  04_predict_stanza.py  conf_edt_v26_stanza_morph_extended_full.ini`

* `04b_predict_malt_udpipe.py` -- Applies trained MaltParser and/or UDPipe-1 models on evaluation data to get predictions. Writes predictions to conllu files. Executes all sections starting with `predict_malt_` and `predict_udpipe1_` in input configuration file. Example:

	* `python  04b_predict_malt_udpipe.py  conf_edt_v26_MaltParser_ME_full.ini`

* `05_evaluate.py` -- Evaluates predictions: compares predicted files to gold standard files and calculates LAS/UAS scores. Executes all sections starting with `eval_` in given configuration files (multiple csv files can be given as an input). Writes results into file `results.csv` in a sub directory closest to the execution directory (for given configurations, the path will be: `edt_2.6/results.csv`). You can also give name of the output csv file as an input argument of the script. Example usage:

	* `python  05_evaluate.py  conf_edt_v26_MaltParser_ME_full.ini  results_maltparser.csv`

Note: configurations also contain overlapping parts, e.g. once you've run UD preprocessing with `conf_edt_v26_Stanza_ME_full.ini`, you do not need to run UD preprocessing again with `conf_edt_v26_stanza_ME_ensemble_full.ini`;

### Results and further studies


* [06_result_tables.ipynb](06_result_tables.ipynb) -- tables with the experiment results read from CSV files;

* [07_smaller_data_exp_and_extrapolation.ipynb](07_smaller_data_exp_and_extrapolation.ipynb) -- draw figures about smaller data experiments (experiments where training set size is gradually increased) and extrapolate the results;
