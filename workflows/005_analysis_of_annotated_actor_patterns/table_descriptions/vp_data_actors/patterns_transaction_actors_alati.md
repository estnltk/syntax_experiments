# Description of patterns_transaction_actors_alati table

The table contains verb patterns that were annotated as isikumäärus = 'alati'. 

 It is a join between pat_tr_head_ and transaction table.

| Column name | Description | Example
|---|---|---|
|pat_id| pattern ID in table patterns_actors_len1_alati | 179
|head_id| ID in transaction_head table  | 2
|transaction_id| ID in transaction table  | 258
|phrase_nr| phrase number | 1
|verb_word |	main verb | nõudma 
|verb_compound| verb compound| - 
|root_word | lemma of word in transaction table | mina
|pat_deprel | deprel of the word related to the verb in pattern table | obl
|word_deprel | deprel of the word related to the verb in transaction table | obl
|pos	|  part of speech | P
|phrase_case	| case of the main word that is tied to the verb | abl
|tr_feats	|  feats attribute value from transaction table | abl,sg
|koht	|  indication if root_word is location | UNK
|elus	|  indication if root_word is alive | YES


## Additional information

-

