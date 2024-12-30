# Description of patterns table

The table contains information about verbs and their patterns. Each row contains a unique pattern.

| Column name | Description | Example
|---|---|---|
|pat_id| Pattern ID in *verb_patterns_new.db* | 349
|pattern| Full pattern as a string | aasima kelle kallal
|verb_word| (main) verb | abielluma
|verb_compound| Other verb compound parts | andeks
|phrase_nr| Phrase number. If pattern consists on a singular phrase, the number will be 1. If pattern consists of two phrases, the number of the first phrase will be 1 and the number of the second one will be 2 | 1
|phrase_case| Grammatical case of the phrase root (after verb) | gen
|adp| Phrase adposition | eest
|inf_verb| Phrase infinitive | teha


## Additional information

Only patterns that consist of a singular phrase are recorded in this table currently. Patterns consisting of two phrases will be added later.
Patterns having a part that is not a phrase root with case, adposition nor infinitive have been omitted from this table, but may be added later.
Patterns having more than one additional compound part have been omitted from this table, but may be added later.