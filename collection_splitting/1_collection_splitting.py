from estnltk import Text, logger
from estnltk.storage.postgres import PostgresStorage, create_schema, BlockQuery
from estnltk_core.layer_operations import split_by_sentences
from read_config import read_config
import argparse
import os

# example: python 1_collection_splitting.py 2 0 conf.ini 
# processes texts 0, 2, 4, ...

parser = argparse.ArgumentParser()
parser.add_argument("module", help="Module for BlockQuery. Selecting texts with text_id % module == remainder.", type=int)
parser.add_argument("remainder", help="Remainder for BlockQuery. Selecting texts with text_id % module == remainder.", type=int)
parser.add_argument("file", help="Configuration ini file name.", type=str)
args = vars(parser.parse_args())

module = args["module"]
remainder = args["remainder"]

# read configuration
root = os.getcwd()
file_name = args["file"]
if os.path.isfile(file_name):
    fname = os.path.basename(file_name).split('/')[-1]
    config = read_config(fname, file_name)
else:
    print("Could not find the specified configuration file.")
    raise SystemExit

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
                          schema=config["source_database"]["work_schema"], 
                          role=config["source_database"]["role"],
                          temporary=False)

source_collection = source_storage[config["source_database"]["collection"]]

# database where the sentences will be saved
target_storage = PostgresStorage(host=config["target_database"]["host"],
                          port=config["target_database"]["port"],
                          dbname=config["target_database"]["database_name"],
                          user=config["target_database"]["username"],
                          password=config["target_database"]["password"],
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
    target_storage[config["target_database"]["collection"]].create(description='5000 texts split into sentences (based on v2)', meta={'text_no': 'int', 'sent_start': 'int', 'sent_end': 'int', 'subcorpus':'str', 'file': 'str', 'title': 'str', 'type': 'str'})
except Exception as e: # psycopg2.errors.DuplicateTable
    #print("Exception: ", str(e).strip(), ". Moving on.")
    pass
    
collection = target_storage[config["target_database"]["collection"]]

# split texts and save sentences
try:
    for text_id, text_obj in source_collection.select(BlockQuery(module,remainder)):
        analysed = Text(text_obj.text).tag_layer(['sentences','morph_extended'])
        sentence_starts = [span.start for span in analysed.sentences]
        sentence_ends = [span.end for span in analysed.sentences]

        sentences = split_by_sentences(analysed, layers_to_keep=list(analysed.layers))
        with collection.insert() as collection_insert:
            sent_counter = 0
            for sent in sentences:
                sent.meta['text_no'] = text_id
                sent.meta['sent_start'] = sentence_starts[sent_counter]
                sent.meta['sent_end'] = sentence_ends[sent_counter]
                sent.meta['subcorpus'] = text_obj.meta["subcorpus"]
                sent.meta['file'] = text_obj.meta["file"]
                sent.meta['title'] = text_obj.meta["title"]
                sent.meta['type'] = text_obj.meta["type"]
                collection_insert(sent, meta_data=sent.meta)

                sent_counter += 1

except Exception as e: 
    print("Problem during splitting and saving sentences: ", str(e).strip())
    target_storage.close()
    raise SystemExit

target_storage.close()
source_storage.close()
