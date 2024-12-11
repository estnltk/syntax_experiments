# Description of matched_phrases table

The table contains verb patterns and root words with semantic role and elus/koht annotation. 

 It is a join between patterns_tr_head and enriched transaction table.

| Column name | Description | Example
|---|---|---|
|pat_id| pattern ID in table patterns_actors_len1_alati | 179
|head_id| ID in transaction_head table  | 2
|transaction_id| ID in transaction table  | 258
|phrase_nr| phrase number | 1
|verb_word |	main verb | nõudma 
|verb_compound| verb compound| - 
|root_word | lemma of word in transaction table | mina
|deprel | deprel of the word related to the verb in pattern table | obl
|phrase_case	| case of the main word that is tied to the verb | abl
|semantic_role	|  semantic role along with frequenct | isik_mitte kunagi
|koht	|  indication if root_word is location | UNK
|elus	|  indication if root_word is alive | YES


## Additional information

Can be used for further filtering base on semantic role.
For example:
To get patterns that were annotated as sometimes location, you need to set condition semantic_role = 'koht_vahel'.




