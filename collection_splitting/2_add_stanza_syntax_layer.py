from estnltk import Text
from estnltk.storage.postgres import PostgresStorage

from estnltk_neural.taggers.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger

from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_name
from read_config import read_config
import argparse
import os
import datetime

# example: python 2_add_stanza_syntax_layer.py 2 0 conf.ini 
# processes texts 0, 2, 4, ...

parser = argparse.ArgumentParser(description = "Tags layer block with stanza tagger.")
parser.add_argument("module", help="Module for layer block. Selecting texts with text_id % module == remainder.", type=int)
parser.add_argument("remainder", help="Remainder for layer block. Selecting texts with text_id % module == remainder.", type=int)
parser.add_argument("file", help="Configuration ini file name.", type=str)
args = vars(parser.parse_args())

module = args["module"]
remainder = args["remainder"]

# read configuration
file_name = args["file"]
if os.path.isfile(file_name):
    fname = os.path.basename(file_name).split('/')[-1]
    config = read_config(fname, file_name)
else:
    print("Could not find the specified configuration file.")
    raise SystemExit

# check needed fields for tagger
if "model_path" not in list(config["stanza_syntax"]):
    print("Stanza model path is not defined!")
    raise SystemExit
if  "input_type" not in list(config["tagger_parameters"]):
	print("Missing input_type parameter!")
    raise SystemExit
else:
    try:
        model_path = config["stanza_syntax"]["model_path"]
        input_type = config["tagger_parameters"]["input_type"]
        stanza_tagger = StanzaSyntaxTagger(input_type=input_type, input_morph_layer=input_type, add_parent_and_children=True, resources_path=model_path)
    except Exception as e: 
        print("Problem with model path or creating the tagger: ", str(e).strip())
        raise SystemExit

# check necessary fields for db connection
for option in ["host", "port", "database_name", "username", "password", "work_schema", "role", "collection"]:
    if option not in list(config["target_database"]):
        msg = "Error in file {}. Missing field \"{}\".\n".format(file_name, option)
        print(msg)
        raise SystemExit
    if config["target_database"][option] == "":
        msg = "Error in file {}. Empty value for \"{}\".\n".format(file_name, option)
        print(msg)
        raise SystemExit

        
# database for tagging
target_storage = PostgresStorage(host=config["target_database"]["host"],
                          port=config["target_database"]["port"],
                          dbname=config["target_database"]["database_name"],
                          user=config["target_database"]["username"],
                          password=config["target_database"]["password"],
                          schema=config["target_database"]["work_schema"], 
                          role=config["target_database"]["role"],
                          temporary=False)        
        
collection = target_storage[config["target_database"]["collection"]]

# check if table exists
table_name = layer_table_name(config["target_database"]["collection"],stanza_tagger.get_layer_template().name)
if "stanza_syntax" in collection.layers or table_exists(target_storage,table_name ):
    print("Stanza Syntax kiht või tabel on juba olemas.")
else:
    collection.add_layer( layer_template=stanza_tagger.get_layer_template() )   

try:
    #print(f"Started tagging: {datetime.datetime.now()}")
    # tag a block
    collection.create_layer_block( stanza_tagger, (module, remainder), mode='append' )

except Exception as e: 
    print("Problem during tagging: ", str(e).strip())
    #print(f"Program exits with error: {datetime.datetime.now()}")
    target_storage.close()
    raise SystemExit
    
#print(f"Finished tagging: {datetime.datetime.now()}")
target_storage.close()

