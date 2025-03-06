## Base data used in experiments

**ekilexist**: base data extracted from the Institute of Estonian Language's lexicographic database [Ekilex] (https://github.com/keeleinstituut/ekilex) 

* *wordlists*: contains word lists as txt files for locations, time, state, event, phrasal verbs and words that have only one semantic type and it's not location, time, state or event (other)
* *obliikva_1_semtyyp.csv*: words that have one semantic type (location, time, event, state)
* *obliikva_2_semtyyp.csv*: words that have 2 semantic types where at least one is location, time, event, state.
* *obliikva_semtyybiga_koik.csv*: words with all their semantic types. 
* *sem_type_ekilex.xlsx*: an excel file of the previous 3 files for ease of viewing
* *valjendverbid.csv*: a list of phrasal verbs

**gpt**: data for annotating physical locations with GPT
* *fyysiliste_kohtade_prompt.txt*: prompt used for preliminary testing of GPT's annotation. More detailed than the prompt used for large scale annotation.
* *gptle_test_10.csv*: csv file containing 10 sentences and words to test GPT annotation
* *kohad_gptle.csv*:  csv file containing 1000 sentences and words in those sentences to be annotated by GPT

**time**: word lists used to filter out temporal obliques. Data from Heiki-Jaan Kaalep's previous work found in the same branch under the folder *rule_based_semantic_categorisation* 
* *ajamaarused.csv*: possible temporal obliques found by using NerTagger and TimexTagger 
* *ajamaarused_sage.txt*: temporal obliques with frequencies above 175 extracted from *ajamaarused.csv*.

