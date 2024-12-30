# Description of temp_patterns table

The table is a helper table that contains information about two-member verb rection patterns in a format which allows them to be later saved into the same table as one-member patterns.

| Column name | Description | Example
|---|---|---|
|pat_id| Pattern ID | 2536
|pattern| Full pattern as a string | keelama kellel + mida teha
|verb_word| (main) verb | keelama
|verb_compound| Other verb compound parts | ''
|phrase_nr| Phrase number. If pattern consists on a singular phrase, the number will be 1. If pattern consists of two phrases, the number of the first phrase will be 1 and the number of the second one will be 2 | 2
|phrase_case| Grammatical case of the phrase root (after verb) | part
|adp| Phrase adposition | ''
|inf_verb| Phrase infinitive | teha


## Additional information

Two halves of the same pattern share the same *pat_id*, *pattern*, *verb_word* and *verb_compound* values. Other values are different.