Script 1_collection_splitting.py takes 3 arguments:
first and last text index to be processed, also the name of configuration file. 

The indexing of texts starts with 0.
The text with the last index (second argument) will not be processed.

Example: 
python 1_collection_splitting.py 0 2 conf.ini
--> the first 2 texts (0 and 1) from the database will be processed.

To process the next slice of texts:
python 1_collection_splitting.py 2 5 conf.ini

If the second argument is larger than the size of the collection then the
program will automatically process texts until the last one in the collection.

Configuration file should have sections "source_database" and "target_database". Both sections
should have fields host, port, database_name, username, password, work_schema, role and 
collection filled out. Source database is where the texts will be read from and target 
database is where the sentences will be saved.
The configuration file 'configuration.ini' should be given as the third argument.
The file name can be given without path (if conf.ini file is in the same folder as script) or
with full path.
