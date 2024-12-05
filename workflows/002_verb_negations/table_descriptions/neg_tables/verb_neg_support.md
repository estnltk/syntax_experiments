# Description of verb_neg_support table

The table contains information about negation support among verbs that match verbs in *patterns* table from vp_data3 and occur in *verb_neg* table.

| Column name | Description | Example
|---|---|---|
|verb| verb lemma | jõudma
|verb_compound| verb compound part(s) | järgi
|all_matches| total number of verb+verb compound occurrences in transactions database (v32) | 32
|neg_matches| total number of negated form occurrences of a given verb+verb compound in transactions database (v32) | 14
|relative_support| Percentage of negated form occurrences of total number of occurrences | 43.75


## Additional information

-