## Description of verb_neg_phrases table

The table contains *transaction_row* table rows with selected attributes from transactions database (v32) that match a transation head from *verb_neg* table.

| Column name | Description | Example
|---|---|---|
|head_id| *head_id* attribute in *transcation_row* table, matches ID in table *transaction_head* | 63
|loc| *loc* attribute in *transaction_row* table | 12
|loc_rel| *loc_rel* attribute in *transaction_row* table | 1
|deprel| *deprel* attribute in *transaction_row* table | xcomp
|form| *form* attribute in *transaction_row* table | elama
|lemma| *lemma* attribute in *transaction_row* table | elama
|feats| *feats* attribute in *transaction_row* table | ill,mod,ps,sup
|parent_loc| *parent_loc* attribute in *transaction_row* table | NULL
|pos| *pos* attribute in *transaction_row* table | V

## Additional information

- Currently, *transaction_row* attribute *id* has not been included in this table.