# Method of making datasets

## Graph and n-groups

A general confidence value table was calculated to so that every integer x from 1 to 5000 had a positive (min value), negative (x-positive) and log2(x) values for n-groups n90, n80, n30; and positive (max value), negative (x-positive) and log2(x) for n-groups n70, n20, n10. The values are calculated in 03_calculate_confidence_values.py file using binom. These confidence valuew were used to draw the n-group line on the graph.

Previously a verb table of all verbs with their unique_lemmas count (how many unique lemmas had a classification based on ekilex/ner/timex) was made. This table was merged with confidence value table so that x = unique_lemmas and each verbcase then had a log2(pos) value for each n-group.
The log2(pos) values were used to assign an n-group or "level" (n90, n80 etc) to each verb based on the log2_tag value (from verb table) and if it was higher or lower than the log2(pos) value (aka above or below a certain line on the graph).


## Selecting data for datasets 

Each verb had a level assigned to it if it was in the range of an n-group line or "-" if it had a low lemma count. The verbs were filtered beforehand to only include verbs that occured in the data at least 4 times and had at least 1 annotated lemma. The same list of verbs was duplicated for multiple tags (A, ELT, S) so that the number of lemma counts matched the count for that specific tag and correct level. For example a verb in ELT table had level n80 but the same verb in A table had level n20.


### n80 and n50 datasets 

Based on the level, all verbs with the certain tag and level were taken for the dataset. Then for each verb, maximum of 500 unique lemmas were taken and one sentence for each lemma. The limit 500 was applied to control the number of examples in a dataset. Some verbs could have had more than 500 lemmas while others had very few.

ELT_n80 dataset was created using ELT tag table and verbs with level "n80".

ELT_n50 dataset used again ELT table but verbs with level "n50".

This method was used for ELT, A, S tags and for n80 and n50 levels.

### n-random

n-random dataset was created by selecting random 100000 unique lemmas and picking one sentence for each unique lemma. No level or tag was used for filtering.


### n-rare 

For n-rare dataset only verbs that had an unique_lemmas count under a certain value were chosen (also their level had to be "-").

For most cases the maximun unique_lemmas count was 8, for some other cases 11, 12 or 15 unique_lemmas was allowed. This was done so that each case had at least 10000 examples and the whole dataset had at least 100000 sentences. Additionally, a limit of 15 sentences was applied to make the distribution of examples more even. This means that in the dataset, for each verb the maximum number of example sentences can be 15 (similarly how for n80 and n50 datasets the limit of sentences was 500).

The dataset can be filtered to only contain verbs that had up to 4 unique_lemmas and that results in 9444 verbs. This subset contains a small set of examples from the total number of examples for that limit.




