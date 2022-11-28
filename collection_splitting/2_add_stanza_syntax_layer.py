from estnltk import Text
from estnltk.storage.postgres import PostgresStorage

from estnltk_neural.taggers.syntax.stanza_tagger.stanza_tagger import StanzaSyntaxTagger
from taggers.entity_tagger import EntityTagger
from taggers.stanza_syntax_tagger import StanzaSyntaxTagger2
from taggers.stanza_syntax_retagger import StanzaSyntaxRetagger

from estnltk.storage.postgres import table_exists
from estnltk.storage.postgres import layer_table_name
from read_config import read_config
import argparse
import os

# example: python 2_add_stanza_syntax_layer.py advmod 2 0 conf.ini 
# processes texts 0, 2, 4, ...

parser = argparse.ArgumentParser(description = "Tags layer block with stanza tagger and creates layers 'stanza_syntax_ignore_entity' where the subtrees of given deprel are stored and layer 'stanza_syntax_without_entity' for the shortened sentence.")
parser.add_argument("deprel", help="Deprel for removing subtrees of the sentence.", type=str)
parser.add_argument("module", help="Module for layer block. Selecting texts with text_id % module == remainder.", type=int)
parser.add_argument("remainder", help="Remainder for layer block. Selecting texts with text_id % module == remainder.", type=int)
parser.add_argument("file", help="Configuration ini file name.", type=str)
args = vars(parser.parse_args())

module = args["module"]
remainder = args["remainder"]
input_deprel = args["deprel"]

# read configuration
root = os.getcwd()
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
else:
    try:
        model_path = config["stanza_syntax"]["model_path"]
        input_type="morph_extended"
        stanza_tagger = StanzaSyntaxTagger(input_type=input_type, input_morph_layer=input_type, add_parent_and_children=True, resources_path=model_path)
        entity_tagger = EntityTagger(deprel =input_deprel, input_type="stanza_syntax", morph_layer="morph_extended")
        ignore_tagger = StanzaSyntaxTagger2( ignore_layer = "stanza_syntax_ignore_entity"+"_"+input_deprel, 
                                            input_type="morph_extended", 
                                                    input_morph_layer="morph_extended", 
                                                      add_parent_and_children=True, resources_path=model_path)
        retagger = StanzaSyntaxRetagger(stanza_syntax_layer="stanza_syntax", 
                                without_entity_layer="stanza_syntax_without_entity"+"_"+input_deprel, 
                                ignore_layer="stanza_syntax_ignore_entity"+"_"+input_deprel)
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
    
table_name = layer_table_name(config["target_database"]["collection"],entity_tagger.get_layer_template().name)
if "stanza_syntax_ignore_entity" in collection.layers or table_exists(target_storage,table_name ):
    print("Ignore Entity (stanza_syntax_ignore_entity) kiht või tabel on juba olemas.")
else:
    collection.add_layer( layer_template=entity_tagger.get_layer_template() ) 
    
table_name = layer_table_name(config["target_database"]["collection"],ignore_tagger.get_layer_template().name)
if "stanza_syntax_without_entity" in collection.layers or table_exists(target_storage,table_name ):
    print("Without Entity (stanza_syntax_without_entity) kiht või tabel on juba olemas.")
else:
    collection.add_layer( layer_template=ignore_tagger.get_layer_template() ) 
    
table_name = layer_table_name(config["target_database"]["collection"],retagger.get_layer_template().name)
if "stanza_syntax_with_entity" in collection.layers or table_exists(target_storage,table_name ):
    print("With Entity (stanza_syntax_with_entity) kiht või tabel on juba olemas.")
else:
    collection.add_layer( layer_template=retagger.get_layer_template() ) 
     

try:
    # tag a block
    collection.create_layer_block( stanza_tagger, (module, remainder), mode='append' )
    collection.create_layer_block( entity_tagger, (module, remainder), mode='append' )
    #collection.create_layer_block( ignore_tagger, (module, remainder), mode='append' )
    #collection.create_layer_block( retagger, (module, remainder), mode='append' )
except Exception as e: 
    print("Problem during tagging: ", str(e).strip())
    target_storage.close()
    raise SystemExit
    
target_storage.close()

