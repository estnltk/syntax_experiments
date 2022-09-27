from estnltk import Text, logger
from estnltk.storage.postgres import PostgresStorage, create_schema, delete_schema
from estnltk.layer_operations import split_by
from read_config import read_config
import argparse
import os

# example: python 1_collection_splitting.py 0 5 conf.ini 
# processes textx 0, 1, 2, 3, 4

parser = argparse.ArgumentParser() # description="Number of texts (start and end) to be processed"
parser.add_argument("start", help="First text to be processed.", type=int)
parser.add_argument("end", help="Last text to be processed. The text with that index is not included in the processing.", type=int)
parser.add_argument("file", help="ini file name.", type=str)
args = vars(parser.parse_args())

start = args["start"]
end = args["end"]

if start > end:
    print("PROGRAM ERROR: Program stopped. Starting index should be smaller than end index!")
    raise SystemExit

# read configuration
root = os.getcwd()
file_name = args["file"]
if os.path.isfile(file_name):
    fname = os.path.basename(file_name).split('/')[-1]
    config = read_config(fname, file_name)

# check necessary fields
for option in ["host", "port", "database_name", "username", "password", "work_schema", "role", "collection"]:
    if option not in list(config["source_database"]) or option not in list(config["target_database"]):
        msg = "Error in file {}. Missing field \"{}\".\n".format(file_name, option)
        print(msg)
        raise SystemExit
    if config["source_database"][option] == "" or config["target_database"][option] == "":
        msg = "Error in file {}. Empty value for \"{}\".\n".format(file_name, option)
        print(msg)
        raise SystemExit
        
    
# postgres storage where the texts are
source_storage = PostgresStorage(host=config["source_database"]["host"],
                          port=config["source_database"]["port"],
                          dbname=config["source_database"]["database_name"],
                          user=config["source_database"]["username"],
                          password=config["source_database"]["password"],
                          pgpass_file='~/.pgpass',
                          schema=config["source_database"]["work_schema"], 
                          role=config["source_database"]["role"],
                          temporary=False)

source_collection = source_storage[config["source_database"]["collection"]]

collection_size = len(source_collection)
if end > collection_size:
    end = collection_size
    #print(f'PROGRAM INFO: given last text index is out of range. Collection has {collection_size} texts. Texts up to the last index will be processed.')

# database where the sentences will be saved
target_storage = PostgresStorage(host=config["target_database"]["host"],
                          port=config["target_database"]["port"],
                          dbname=config["target_database"]["database_name"],
                          user=config["target_database"]["username"],
                          password=config["target_database"]["password"],
                          pgpass_file='~/.pgpass',
                          schema=config["target_database"]["work_schema"], 
                          role=config["target_database"]["role"],
                          temporary=False)

try:
    create_schema(target_storage)
except Exception as e: #psycopg2.errors.DuplicateSchema
    #print("Exception: ", str(e).strip(), ". Moving on to creating collection.")
    pass

# create collection
try:
    target_storage[config["target_database"]["collection"]].create(description='5000 texts split into sentences (based on v2)', meta={'text_no': 'int', 'sent_start': 'int', 'sent_end': 'int'})
except Exception as e: # psycopg2.errors.DuplicateTable
    #print("Exception: ", str(e).strip(), ". Moving on.")
    pass
    
collection = target_storage[config["target_database"]["collection"]]

# split texts and save sentences
try:
    txt_id = start # counter of text id-s
    for txt in source_collection[start:end]:
        analysed = Text(txt.text).analyse("all")
        # get starts and ends of sentences
        sentence_starts = analysed.sentences['start']
        sentence_ends = analysed.sentences['end']

        sentences = split_by(analysed, "sentences")

        with collection.insert() as collection_insert:
            # sent_counter is for accessing the correct starts and ends
            sent_counter = 0
            for sent in sentences:
                sent.meta['text_no'] = txt_id
                sent.meta['sent_start'] = sentence_starts[sent_counter]
                sent.meta['sent_end'] = sentence_ends[sent_counter]
                collection_insert(sent, meta_data=sent.meta)

                sent_counter += 1
        txt_id += 1
except Exception as e: 
    print("Problem during splitting and saving sentences: ", str(e).strip())
    target_storage.close()
    source_storage.close()
    raise SystemExit

target_storage.close()
source_storage.close()
