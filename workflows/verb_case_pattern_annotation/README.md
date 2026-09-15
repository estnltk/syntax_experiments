
## Verb case pattern annotation scripts

Short description and example command for each python script.

All scripts are run from this folder and the commands reflect that. If you wish to run the sripts from a different folder then the conf file path has to be modified.

If "any conf file can be used" then any conf file from "conf" folder can be used (except azure conf) as long as the general database, table and column names are correct. If multiple conf files have to be used then it will be noted and example commands given.

Note for future: if confidence value table confidence_range=5000 then one verb is left out since it has 6500 unique lemmas. This can be fixed in the future version if the range is set to 7000 or more (should be checked in future version step 06). This time only one verb was left out. 

### Create spatial_obl tabel

This script has to be run once with one conf file (any conf file).

>> python3 01_create_spatial_obl.py --conf ../conf/conf_ex_A.ini


### Statistics tables

Has to be run for every tag conf file.

>> python3 02_spatial_obl_statistics_tables.py --conf ../conf/conf_ex_A.ini

>> python3 02_spatial_obl_statistics_tables.py --conf ../conf/conf_ex_E.ini

>> python3 02_spatial_obl_statistics_tables.py --conf ../conf/conf_ex_EL.ini

>> python3 02_spatial_obl_statistics_tables.py --conf ../conf/conf_ex_ELT.ini

>> python3 02_spatial_obl_statistics_tables.py --conf ../conf/conf_ex_L.ini

>> python3 02_spatial_obl_statistics_tables.py --conf ../conf/conf_ex_S.ini

>> python3 02_spatial_obl_statistics_tables.py --conf ../conf/conf_ex_T.ini


### Calculate confidence values

This table has to be calculated once and doesn't need to be re-calculated even if other tables are updated. This table contains values in a set range for verb scatterplot so that n-lines could be drwan on the plot. Any conf file can be used.

>> python3 03_calculate_confidence_values.py --conf ../conf/conf_ex_A.ini


### Plotting examples

Selectes examples to display on the verb scatterplot. Any conf file can be used.

>> python3 04_create_spatial_obl_plotting_examples.py --conf ../conf/conf_ex_A.ini


### Scatterplot

Creates scatterplots for given labels and saves the result graph to folder specified in the conf file. Has to be run for every conf file.

>> python3 05_spatial_obl_visualization.py --conf ../conf/conf_ex_A.ini

>> python3 05_spatial_obl_visualization.py --conf ../conf/conf_ex_E.ini

>> python3 05_spatial_obl_visualization.py --conf ../conf/conf_ex_EL.ini

>> python3 05_spatial_obl_visualization.py --conf ../conf/conf_ex_ELT.ini

>> python3 05_spatial_obl_visualization.py --conf ../conf/conf_ex_L.ini

>> python3 05_spatial_obl_visualization.py --conf ../conf/conf_ex_S.ini

>> python3 05_spatial_obl_visualization.py --conf ../conf/conf_ex_T.ini


### Creating n-level table

This script adds n-level and annotation counts to every tag table. Has to be run for every conf file.

>> python3 06_spatial_obl_verbcase_merge_confidence_data.py --conf ../conf/conf_ex_A.ini

>> python3 06_spatial_obl_verbcase_merge_confidence_data.py --conf ../conf/conf_ex_E.ini

>> python3 06_spatial_obl_verbcase_merge_confidence_data.py --conf ../conf/conf_ex_EL.ini

>> python3 06_spatial_obl_verbcase_merge_confidence_data.py --conf ../conf/conf_ex_ELT.ini

>> python3 06_spatial_obl_verbcase_merge_confidence_data.py --conf ../conf/conf_ex_L.ini

>> python3 06_spatial_obl_verbcase_merge_confidence_data.py --conf ../conf/conf_ex_S.ini

>> python3 06_spatial_obl_verbcase_merge_confidence_data.py --conf ../conf/conf_ex_T.ini


### Making datasets

07_make_dataset has to be run for all conf files. This script creates datasets based on the lemma_limit (500 or max - this has to be changed manually in the conf file) and class (n80 or n50 - has to be changed manually in the conf file). If some combinations are not needed then they can be skipped.


change lemma_limit=500 and class=n80

>> python3 07_make_dataset.py --conf ../conf/conf_ex_A.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_E.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_EL.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_ELT.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_L.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_S.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_T.ini


change lemma_limit=500 and class=n50

>> python3 07_make_dataset.py --conf ../conf/conf_ex_A.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_E.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_EL.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_ELT.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_L.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_S.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_T.ini


change lemma_limit=max and class=n80

>> python3 07_make_dataset.py --conf ../conf/conf_ex_A.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_E.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_EL.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_ELT.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_L.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_S.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_T.ini


change lemma_limit=max and class=n50

>> python3 07_make_dataset.py --conf ../conf/conf_ex_A.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_E.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_EL.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_ELT.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_L.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_S.ini

>> python3 07_make_dataset.py --conf ../conf/conf_ex_T.ini














