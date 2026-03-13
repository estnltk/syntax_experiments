## Code files for different development tasks

### Workflow:

Depends on the things done in v04 workflow until v04_visualization.ipynb

1. **v04_calculate_line_info.ipynb** : Calculating quality lines and plotting. Version of the 07_... code.
2. ** ..._line_data_merge.ipynb**: Merging quality line data with scatterplot data. Calculating additional values for filtering data.
3. **v04_data_extraction_4_gpt.ipynb**: First extracting example from table for n80. Example code is for extracting data and initial GPT json but not the code necessary for using GPT.
4. **09_v04_data_extraction_4_gpt_v2_2new_prompt_580.ipynb**: Testing propting with 580 sentences from n80. Uses input file **n80_top29_10p_10n_examples.csv**.
5. **09_v04_data_extraction_4_gpt_v3_n80.ipynb**: Testing prompting with 10K sentences from n80. Uses input file **n80_examples_large_v1.csv''**. Results are saved in **n80_examples_large_v1_gpt_v1_10K_b12_v1.csv**. 
6. **09_v04_data_extraction_4_gpt_v3_n80_analysis.ipynb**: Analysis for the 10K sentences that gpt classified. Uses input file **n80_examples_large_v1_gpt_v1_10K_b12_v1.csv**.
7. 01_... - 07_... are v04 workflow to incorporate timex and ner tags in the data tables 


NB!  The gpt code expects python >=3.10

