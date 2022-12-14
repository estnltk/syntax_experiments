from estnltk import Text
from estnltk.storage.postgres import PostgresStorage

from read_config import read_config
import argparse
import os
from collection_to_ls import collection_to_labelstudio, conf_gen


# example: python 4_export_2_labelstudio.py advmod conf.ini ls_export_v1.json 20 12345 1
# exports the necessary layers for advmod infto json 


parser = argparse.ArgumentParser(description = "Takes the stanza layer and ignored entities layer of given advmod and creates a json file with data and configuration file for labelstudio. Configuration file will be saved to the same folder as the data json file or where the script was run.")
parser.add_argument("deprel", help="Deprel for removing subtrees of the sentence.", type=str)
parser.add_argument("config_file", help="Configuration ini file name.", type=str)
parser.add_argument("result_file", help="Results json file name.", type=str)
parser.add_argument("percent", help="Percentage of data to take randomly.", type=int)
parser.add_argument("seed", help="Seed for taking the data.", type=int)
parser.add_argument("entity_count", help="For filtering sentences. Only sentences with given number of given deprel will be chosen.", type=int)
args = vars(parser.parse_args())

input_deprel = args["deprel"]
percent = args["percent"]
seed = args["seed"]
entity_count = args["entity_count"]

# read configuration
file_name = args["config_file"]
if os.path.isfile(file_name):
    fname = os.path.basename(file_name).split('/')[-1]
    config = read_config(fname, file_name)
else:
    print("Could not find the specified configuration file.")
    raise SystemExit
    
# get output file
res_path = args["result_file"]
res_fname = os.path.basename(res_path)
fpath = None 
if res_path.split(".")[-1:][0] != "json":
    print("Please provide result file name with .json extension.")
    raise SystemExit
if  len(res_path.split('/')) > 1: # filename contains path, save it for ls conf file 
    fpath = os.path.join(*list(res_path.split('/'))[:-1])

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

        
# database for exporting to labelstudio 
target_storage = PostgresStorage(host=config["target_database"]["host"],
                          port=config["target_database"]["port"],
                          dbname=config["target_database"]["database_name"],
                          user=config["target_database"]["username"],
                          password=config["target_database"]["password"],
                          schema=config["target_database"]["work_schema"], 
                          role=config["target_database"]["role"],
                          temporary=False)        
        
collection = target_storage[config["target_database"]["collection"]]


try:
    ignore_layer = "stanza_syntax_ignore_entity_"+input_deprel 
    collection.selected_layers = ["stanza_syntax", ignore_layer]
    
    # take random 1000 sentences 
    sample = collection.select().sample( percent, amount_type='PERCENTAGE', seed=seed )
    
    txt_ids = []
    for txt in sample:
        if len(collection[txt[0]].ignore_layer) == entity_count:
            txt_ids.append(txt[0])
        if len(txt_ids) == 1000:
            break
            
     collection2 = []

    for txtid in txt_ids:
        collection2.append(collection[txtid])
    
    collection_to_labelstudio(collection2, regular_layers=[ignore_layer],filename=res_path)
    
    if fpath != None:
        # TODO linux path wants "/" at the beginning of full path 
        conf_save = os.path.join("/", fpath, "ls_conf.txt")
        idx_save = os.path.join("/", fpath, "ls_ids.txt")
    else:
        conf_save = "ls_conf.txt"
        idx_save = "ls_ids.txt"
    
    with open(conf_save, "w", encoding="utf-8") as f:
        f.write(conf_gen(classes=[ignore_layer]))
        
    with open(idx_save, "w", encoding="utf-8") as f:
        for listitem in txt_ids:
            f.write(f'{listitem}\n')
    
    
except Exception as e: 
    print("Problem with exporting the layers: ", str(e).strip())
    target_storage.close()
    raise SystemExit
    
target_storage.close()

