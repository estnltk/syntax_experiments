import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from estnltk import Text
from estnltk.storage.postgres import PostgresStorage

from taggers.super_tagger import SuperTagger
from estnltk_patches.phrase_extractor import PhraseExtractor
from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_name
from read_config import read_config
import argparse
import os
import datetime

from estnltk_core.converters.serialisation_registry import SERIALISATION_REGISTRY
from estnltk.converters.serialisation_modules import syntax_v1
from estnltk.converters.serialisation_modules import legacy_v0

if 'syntax_v1' not in SERIALISATION_REGISTRY:
    SERIALISATION_REGISTRY['syntax_v1'] = syntax_v1
if 'legacy_v0' not in SERIALISATION_REGISTRY:
    SERIALISATION_REGISTRY['legacy_v0'] = legacy_v0


# example: python 3_add_ignore_entity_layer.py obl 2 0 conf.ini obl_phrases
# processes texts 0, 2, 4, ...

parser = argparse.ArgumentParser(description = "Tags layer block with super tagger and creates layer 'syntax_ignore_entity' where the subtrees of given deprel are stored. (expects that stanza syntax layer already exists)")
parser.add_argument("deprel", help="Deprel for removing subtrees of the sentence.", type=str)
parser.add_argument("module", help="Module for layer block. Selecting texts with text_id % module == remainder.", type=int)
parser.add_argument("remainder", help="Remainder for layer block. Selecting texts with text_id % module == remainder.", type=int)
parser.add_argument("config file", help="Configuration ini file name.", type=str)
parser.add_argument("ignore layer name", help="Name of the ignore layer (obl_phrases etc).", type=str)
args = vars(parser.parse_args())

module = args["module"]
remainder = args["remainder"]
input_deprel = args["deprel"]
ignore_layer_name  = args["ignore layer name"]

# read configuration
file_name = args["config file"]
if os.path.isfile(file_name):
    fname = os.path.basename(file_name).split('/')[-1]
    config = read_config(fname, file_name)
else:
    print("Could not find the specified configuration file.")
    raise SystemExit


try:
    phrase_tagger = PhraseExtractor(deprel=input_deprel, input_type="stanza_syntax", 
                            syntax_layer="stanza_syntax", output_layer=ignore_layer_name)
    
except Exception as e: 
    print("Problem with creating the tagger: ", str(e).strip())
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
table_name = layer_table_name(config["target_database"]["collection"],phrase_tagger.get_layer_template().name)
if ignore_layer_name in collection.layers or table_exists(target_storage,table_name ):
    print(f"{ignore_layer_name} kiht või tabel on juba olemas.")
else:
    collection.add_layer( layer_template=phrase_tagger.get_layer_template() , sparse=True) 

try:
    print(f"Started tagging: {datetime.datetime.now()}")
    # tag a block
    collection.create_layer_block( phrase_tagger, (module, remainder), mode='append' ) 

except Exception as e: 
    print("Problem during tagging: ", str(e).strip())
    print(f"Program exits with error: {datetime.datetime.now()}")
    target_storage.close()
    raise SystemExit
    
print(f"Finished tagging: {datetime.datetime.now()}")
target_storage.close()

