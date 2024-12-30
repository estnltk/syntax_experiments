# Description of pattern_support table

The table contains information about patterns and their support in transactions database (v32). Each row contains one pattern, its main verb and verb compound part frequency in transactions database, the number of pattern matches in transactions database and the support of pattern matches among main verb and verb compound part matches.

| Column name | Description | Example
|---|---|---|
|pat_id| Pattern ID in table *patterns* | 2526
|verb_word| (main) verb | laimama
|verb_compound| Other verb compound parts | kokku
|phrase_case| Grammatical case of the phrase root (after verb) | ill
|adp| Phrase adposition |  poolt
|inf_verb| Phrase infinitive | tegema
|verb_occurrence_count| Total number of pattern verb and its compound part matches in transactions database | 10267
|absolute_support| Total number of pattern matches in transactions database | 4707
|relative_support| Proportion of pattern matches (absolute support) in pattern verb and its compound part matches (verb occurrence count) | 45.84591409369826


## Additional information

Columns *verb_word*, *verb_compound*, *phrase_case*, *adp* and *inf_verb* can be accessed by pattern ID from table *patterns* and have only been added to this table in order to increase readability. The columns may be removed in future.