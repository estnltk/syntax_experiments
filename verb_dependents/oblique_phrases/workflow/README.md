## Workflow:

In this context "category" refers to verb phrases that are semantically in one group (almost always and almost never locations). 
Refer to this [explanation](https://github.com/estnltk/syntax_experiments/blob/semantic_labelling/verb_dependents/oblique_phrases/data/README.md).


### Labeling verbs and phrases

Creates necessary tables from [Katrin Tsepelina's](https://github.com/estnltk/syntax_experiments/tree/verb_templates/workflows/001_verb_transactions/v33) pre-existing [databases](https://drive.google.com/drive/folders/1MhvQYevlJnowiWqu2NF5QFT_4noLeBTz) for categorizing verb phrases.

Expected space for the database files is 13-14GB.

**01_workflow_with_nertimex** - workflow to get base data in the database

**02_add_n80_data** -  to assign category (n80, n20 etc)


### Datasets

Creates dataset files for each category.

**03_make_n20_dataset** 

**03_make_n50_dataset**

**03_make_n80_dataset** 



### Analyse semantic label data 

**04_gpt_result_analysis** - additional analysis for prompt improvements etc. The analysis notebooks are mainly to look at examples, detect overlaps and find odd cases in the result files.

**05_make_error_benchmarks** - creating examples for benchmarks/morph_syntax_error categories

**06_summary** - analysis and summary of gpt answers (v01, v02, v03, ...). 

