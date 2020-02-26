## Creating collections

create_collections.py reads data from original_data folder, creates 2 collections: edt and est_ud, saves collected 
texts to the PostgreStorage collections. Postgre database connection parameters are specified in pgpass file: db_conn.pgpass<br>

Every text object has 4 layers in this stage: <br>
1) words <br>
2) compound tokens <br>
3) sentences <br>
4) syntax_gold <br> 



