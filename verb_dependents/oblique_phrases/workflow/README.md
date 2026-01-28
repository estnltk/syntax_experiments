### Workflow:

**01_workflow_with_nertimex:**

 01_... - 06_... are [v04](https://github.com/estnltk/syntax_experiments/tree/semantic_labelling/physical_location_labelling/physical_location_by_context/v04_verb-case_pattern/code) workflow to incorporate timex and ner tags in the data tables 


**02_add_n80_data:**

07_... - visualization and adding line data

08_... - middle step to merge "section" data with spatial_obl table and assign section (n80 etc)


**03_make_n80_dataset:**

09_... - selects all verbs in the n80 area and takes max 500 (unique) lemmas per verb and one example sentence for each lemma.


**04_gpt_result_analysis:**

gpt_run01_analysis - gpt v01 answer analysis

vabamorf_analysis

verbimallid_analysis  - locative case pairs analysis 

**05_make_error_benchmarks:**

creating examples for benchmarks/morph_syntax_error categories

**06_summary:**

analysis and summary of all gpt answers (v01, v02, v03, ...)

