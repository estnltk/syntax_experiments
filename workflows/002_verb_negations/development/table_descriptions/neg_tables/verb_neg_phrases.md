## Description of verb_neg_phrases table

The table contains selected attributes of *transaction_row* table rows from transactions database (v32) that match a transaction head from *verb_neg* table.

| Column name | Description | Example
|---|---|---|
|head_id| *head_id* attribute in *transcation_row* table, matches ID in table *transaction_head* | 63
|deprel| *deprel* attribute in *transaction_row* table | xcomp
|form| *form* attribute in *transaction_row* table | elama
|lemma| *lemma* attribute in *transaction_row* table | elama
|feats| *feats* attribute in *transaction_row* table | ill,mod,ps,sup

## Additional information

- Currently, *transaction_row* attributes *id*, *loc*, *loc_rel*, *parent_loc* and *pos* have not been included in this table.