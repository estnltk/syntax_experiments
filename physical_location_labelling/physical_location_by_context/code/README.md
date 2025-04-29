## Code files for different development tasks

**environment_v03.yml**: anaconda environment file with all packages and versions used for coding

**v01_experiment_1**: Trying to find physical locations by finding words in spatial cases that are several verbs' direct dependents.

* *v01_locations_by_verb.ipynb*: for finding possible physical locations by looking for words in cases denoting location for multiple verbs. For better documentation look inside the file.
* *v01_locations_by_verb_timefilter.ipynb*: for finding possible physical locations by looking for words in cases denoting location for multiple verbs where words denoting time are filtered out.
* *timetest_v01.ipynb*: for finding possible timewords using files in base_data

**v02_manual_annotation**: Preparing material for experiment 2 - gpt annotation.

* *v02_examples_for_location.ipynb*: searching for forms and example phrases for an oblique's lemma. Used to ease manual annotation.
* *v02_annotation_analysis.ipynb*: analysing the manual annotation of 1000 obliques found in *kohasonad_margendus.csv*
* *v02_sentence_by_id_katrin.ipynb*: searches for sentences in the Estonian Reference Corpus by sentence_id. Corpus is located in an SQL database. Used to feed them to gpt as word context.

**v03_gpt_annotation**: Annotating physical locations with gpt and calculating its quality.

* *v03_gpt_annotation.ipynb*: annotating 1000 words with GPT as physical locations (LOC) or something else (NONE)
* *v03_gpt_results.ipynb*:  comparing automatic and manual annotation files. Finds quality of automatic annotation.

**v04_rulebased_annotation**: Annotating obliques with various freely available resources

* *heiki_annotation*: experiments to add ner+timex+rulebased tagging results compiled by Heiki-Jaan Kaalep to the data. Currently way too slow. 
* *obliikva_semantika_ekilexist_script.sql*: Sql queries for extracting a word's semantic type info from ekilex
* *v04_semtype_co-occurance.ipynb*: Finds how much each semantic type appears with location, time, state and event tags. Looks through words that have 2 semantic types where 1 is loc, time, state or event. 
* *v04_semtype_to_database.ipynb*: Adds semantic tags (currently from ekilex) to lemmas that appear in spatial cases in the Estonian Reference corpus. 
* *v04_spatial_obliques_from_SQLite.ipynb*: Finds all obliques in spatial cases from the Estonian Reference corpus and writes them into a database table
* *v04_statistics_lemma.ipynb*: Calculates semantic tag coverage and lemma frequency for words in spatial cases in the estonian Reference corpus
* *v04_statistics_verb_case.ipynb*: Seperates case from feats, calculates tag frequency, percentages, proportions and amount of unique dependents per verb and case pair
* *v04_visualization.ipynb*: creates various hoverplots to illustrate data from *v04_semtype_statisctic_verb.ipynb*.
* *v04_wordnet_synsets.ipynb*: counts the amount of synsets each verb has in Estonian Wordnet. Used for data visualization.