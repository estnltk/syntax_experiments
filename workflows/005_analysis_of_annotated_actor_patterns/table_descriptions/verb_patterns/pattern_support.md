# Description of pattern_support table

It includes the frequency of verb patterns in the transaction table.

| Column name | Description | Example
|---|---|---|
|pat_id| pattern ID in table patterns_actors_len1_alati | 167
|verb_word |	main verb | tundma 
|verb_compound| verb compound| kaasa
|phrase_case	| case of the main word that is tied to the verb | all
|adp	| verb conjunction | -
|inf_verb	| infinite verb in the verb phrase | - 
|verb_occurrence_count | verb frequency in transaction table | 1
|absolute_support | pattern frequency in transaction table | 1
|relative_support | pattern frequency in comparison to verb frequency in transaction table| 100.0


## Additional information

Pattern could consist of multiple parts and then it should be decided if the frequency is for the whole pattern.

