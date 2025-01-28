# Description of trans_obl_loc table

The table contains obl transactions that are in one of 7 locative cases. 

| Column name | Description | Example
|---|---|---|
|head_id |  id in the transaction_head table| 8
|verb |	main verb | saama 
|verb_compound| verb compound| pihta 
|transaction_id| id in the transaction table| 1
|root_word| lemma of root word | keel
|word_deprel| deprel of root word | obl
|pos| part of speech | S
|tr_feats | deprel of the word related to the verb | all,com,pl
|koht | indication if word is location | UNK
|elus | indication if word is actor | UNK
|loc_case	| case of the main word that is tied to the verb | all


## Additional information

-

