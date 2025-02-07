## Results from running code or doing manual annotation.

**v01_experiment_1**
* *kohasonad_hea_vaadata.xlsx*: possible physical locations by each verb with their frequency in the corpus and a concreteness rating. An excel file for better viewing
* *kohasonad_test.csv*: possible physical locations by each verb with their frequency in the corpus and a concreteness rating.
* *kohasonad_test_aegadeta-csv*: possible physical locations by each verb with their frequency in the corpus and a concreteness rating but where possible time denoting words haven't been filtered out.

**v02_manual_annotation**
* *kohasonad_naited_lause_idga.csv*: random 1000 lemmas from kohasonad_test with added wordforms and example phrases for annotation. Includes sentence id-s for easier searching. Made with *v01_examples_by_location.ipynb*
* *kohasonad_margendus.xlsx*: Excel annotation file for 1000 obliques in spatial cases with their forms and example phrases. Annotation guidelines found in documentation folder in file *annotation_guidelines_location.md*
* *kohasonad_margendus.csv*: CSV annotation file for 1000 obliques in cases denoting location with their forms and example phrases. For use in code

**v03_gpt_annotation**
* *gpt_test_valjund.csv*: gpt annotation for 10 words with sentence context to test gpt
* *kohad_1000_gpt_valjund_excel.xlsx*: gpt annotation for 1000 words with sentence context. Excel file for easier viewing.
* *kohad_1000_gpt_valjund_pipe.csv* : gpt annotation for 1000 words with sentence context. Delimiter is a pipe (|). Pipe is used as the default delimiter because sentences can contain semicolons.
* *kohad_1000_gpt_valjund_pipe.csv* : gpt annotation for 1000 words with sentence context. Delimiter is a semicolon (;). NB! GPT also outputs the sentence it was given as context for easier annotation, but sentences can contain semicolons, so a semicolon isn't the best delimiter.