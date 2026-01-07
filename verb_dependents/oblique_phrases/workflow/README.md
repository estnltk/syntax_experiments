### Workflow:

**verb filtering:**

 01_... - 07_... are [v04](https://github.com/estnltk/syntax_experiments/tree/semantic_labelling/physical_location_labelling/physical_location_by_context/v04_verb-case_pattern/code) workflow to incorporate timex and ner tags in the data tables 


**example sentence selection:**

08_... - middle step to merge "section" data with spatial_obl table and assign section (n80 etc)

09_... - selects all verbs in the n80 area and takes max 500 (unique) lemmas per verb and one example sentence for each lemma.


**initial gpt testing:**

10_... - 12_... are initial gpt prompt testing files, these might become legacy later on 

10_v04_data_extraction_4_gpt_test580.ipynb: Testing propting with 580 sentences from n80. Uses input file n80_top29_10p_10n_examples.csv.

10_v04_data_extraction_4_gpt_n80_v1.ipynb: Testing prompting with 10K sentences from n80. Uses input file n80_examples_large_v1.csv''. Results are saved in n80_examples_large_v1_gpt_v1_10K_b12_v1.csv. 

10_v04_data_extraction_4_gpt_n80_v1_analysis.ipynb: Analysis for the 10K sentences that gpt classified. Uses input file n80_examples_large_v1_gpt_v1_10K_b12_v1.csv.

12_v04_data_extraction_4_gpt_n80_v2.ipynb: Testing prompting with 10K sentences from n80. Uses input file n80_examples_large_v1_gpt_v1_10K_b12_v1.csv''. Results are saved in n80_examples_large_v1_gpt_v2_10K_b10_v1.csv. 

12_v04_data_extraction_4_gpt_n80_v2_analysis.ipynb: Analysis for the 10K sentences that gpt classified. Uses input file n80_examples_large_v1_gpt_v2_10K_b10_v1.csv.

