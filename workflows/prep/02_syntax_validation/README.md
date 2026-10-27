
## Syntax validation script

>> python3 syntax_validation_rules.py --conf ../../conf/conf_ex_A.ini


Configuration file can be any file from 'conf' folder (except azure conf) as long as the database, conflict_column name and transaction table names are correct.

This script might become deprecated later. If morphosyntax conflicts are marked on the layers in original database then in newer transaction table the conflicts are already marked.


