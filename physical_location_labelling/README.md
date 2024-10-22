## Labelling physical locations - v01

The aim of this work is to develop a tagger for obliques that tags physical locations in syntactically annotated Estonian texts.

**Base_data**: data needed to run the code. 
* *valjendverbid.csv/valjendverbid-txt*: a list of VMWEs (verbal multiword expressions) extracted from the [Ekilex database](https://ekilex.ee/), 
* *ajamaarused_sage.txt/ajamaarused.csv*: obliques that denote time from Heiki-Jaan Kaalep's previous work found in the same branch under the folder *rule_based_semantic_categorisation* 

**Code**: code files for different development tasks. 
* *v01_placewords_by_verb* for finding possible physical placewords by looking for words in cases denoting location for multiple verbs. For better documentation look inside the file.
* *timetest_v01.ipynb* for finding possible timewords using files in base_data

**Results**: results obtained from running the code. 
* *kohasonad_test*: possible physical locations by each verb with their frequency in the corpus and a concreteness rating
* *kohasonad_test_aegadeta*: the same but where possible time denoting words haven't been filtered out
* *kohasonad_hea_vaadata.xlsx*: an excel file with the csv-s for better viewing