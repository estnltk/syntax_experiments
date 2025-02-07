## Base data used in experiments

**ekilexist**: base data extracted from the Institute of Estonian Language's lexicographic database [Ekilex] (https://github.com/keeleinstituut/ekilex) 
* *ADV_kohad_ekilexist.txt* list of spatial adverbs (ADV_koht)
* *sona_sem_tyyp_ekilexist* words with their semantic types. One word can have more than one semantic type
* *valjendverbid.csv/valjendverbid-txt*: a list of phrasal verbs

**gpt**: data for annotating physical locations with GPT
* *fyysiliste_kohtade_prompt.txt*: prompt used for preliminary testing of GPT's annotation. More detailed than the prompt used for large scale annotation.
* *gptle_test_10.csv*: csv file containing 10 sentences and words to test GPT annotation
* *kohad_gptle.csv*:  csv file containing 1000 sentences and words in those sentences to be annotated by GPT

**time**: word lists used to filter out temporal obliques. Data from Heiki-Jaan Kaalep's previous work found in the same branch under the folder *rule_based_semantic_categorisation* 
* *ajamaarused.csv*: possible temporal obliques found by using NerTagger and TimexTagger 
* *ajamaarused_sage.txt*: temporal obliques with frequencies above 175 extracted from *ajamaarused.csv*.

