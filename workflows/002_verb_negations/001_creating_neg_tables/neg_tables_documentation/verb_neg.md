# Description of verb_neg table

The table contains *transaction_head* table rows with selected attributes from transactions database (v32) that contain a negated verb and match a verb pattern from vp_data3 *patterns* table.

| Column name | Description | Example
|---|---|---|
|id| ID of *transaction_head* table row | 676
|verb| *lemma* attribute of *transaction_head* table | valima
|verb_compound| *verb compound* attribute of *transaction_head* table | välja
|form| *form* attribute of *transaction_head* table | valin
|deprel| *deprel* attribute of *transaction_head* table | conj
|feats| *feats* attribute of *transaction_head* table | af,indic,main,pres,ps,ps1,sg


## Additional information

- Currently, *transaction_head* table attributes *sentence_id* and *loc* have not been included in this table.