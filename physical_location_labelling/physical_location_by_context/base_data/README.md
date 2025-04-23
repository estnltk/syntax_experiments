## Base data used in experiments

**ekilexist**: base data extracted from the Institute of Estonian Language's lexicographic database [Ekilex] (https://github.com/keeleinstituut/ekilex) 

* *adverbs*: contains lists of words with adverb tags in ekilex. For Kadri Muischnek.
* *wordlists*: contains word lists as txt files for location, time, state, event and not_location
* *obl_2_semtyyp.xlsx*/*obl_2_semtyyp.csv*: words that have 2 semantic types where at least one is location, time, event, state. Used to find what semantic types can be combined
* *semtype_loc_or_not.xlsx*: is a semantic type a location or not.
* *valjendverbid.csv/valjendverbid.txt*: a list of phrasal verbs

**gpt**: data for annotating physical locations with GPT
* *fyysiliste_kohtade_prompt.txt*: prompt used for preliminary testing of GPT's annotation. More detailed than the prompt used for large scale annotation.
* *gptle_test_10.csv*: csv file containing 10 sentences and words to test GPT annotation
* *kohad_gptle.csv*:  csv file containing 1000 sentences and words in those sentences to be annotated by GPT

**time**: word lists used to filter out temporal obliques. Data from Heiki-Jaan Kaalep's previous work found in the same branch under the folder *rule_based_semantic_categorisation* 
* *ajamaarused.csv*: possible temporal obliques found by using NerTagger and TimexTagger 
* *ajamaarused_sage.txt*: temporal obliques with frequencies above 175 extracted from *ajamaarused.csv*.

