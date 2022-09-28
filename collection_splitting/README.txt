Script 1_collection_splitting.py takes 3 arguments:
module and remainder for BlockQuery, and the name/path of configuration file. 

The indexing of texts starts with 0.

Example: 
python 1_collection_splitting.py 2 0 conf.ini
--> Texts 0, 2, 4, 6, ... will be processed

To process the remainder of texts:
python 1_collection_splitting.py 2 1 conf.ini

Configuration file should have sections "source_database" and "target_database". Both sections should have fields: host, port, database_name, username, password, work_schema, role and collection filled out. Source database is where the texts will be read from and target database is where the sentences will be saved.
The configuration file name can be given without path (if conf.ini file is in the same folder as script) or with full path.
