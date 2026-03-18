## Workflow:

### Creates necessary tables from pre-existing databases for categorizing verb phrases.

Expected space for the database files is 13-14GB.

**01_workflow_with_nertimex:** - workflow to get base data in the database

**02_add_n80_data:** - middle step to merge "section" data with spatial_obl table and assign section (n80, n20 etc)


### The creates datasets for each category.

**03_make_n20_dataset:** - creating dataset from n20 examples

**03_make_n50_dataset:** - creating dataset from n50 examples. Consists of data from n70 and n30 sections.

**03_make_n80_dataset:** - creating dataset from n80 examples


### Analyses the gpt results, creates benchmarks and summary files. 

**04_gpt_result_analysis:** - additional analysis for prompt improvements etc. The analysis notebooks are mainly to look at examples, detect overlaps and find odd cases in the result files.

**05_make_error_benchmarks:** - creating examples for benchmarks/morph_syntax_error categories

**06_summary:** - analysis and summary of all gpt answers (v01, v02, v03, ...). 

