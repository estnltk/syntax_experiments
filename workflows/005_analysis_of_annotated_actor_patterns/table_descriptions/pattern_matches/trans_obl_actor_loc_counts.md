# Description of trans_obl_actor_loc_counts table

The table contains obl transactions distinct root counts for actors and locations.

Derived from trans_obl_loc table.

| Column name | Description | Example
|---|---|---|
|verb |	main verb | aitama 
|verb_compound| verb compound| - 
|loc_case| case of  | 0
|elus_cnt| distinct root count based on verb and loc_case that are marked as elus| 0
|koht_cnt| distinct root count based on verb and loc_case  that are marked as koht | 1
|root_cnt| distinct root count based on verb and loc_case | 2



## Additional information

Elus and koht are not from verb annotation but from phrase_pattern db lists.

