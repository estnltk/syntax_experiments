# Workflow for studing syntax conservation

## General overview

* We first create a corpus where each sentence is a separate `Text` object
* Next we use `StanzaSyntaxTagger` to add a detached syntax layer to the new collection
* After that we tag specific syntactical phrases to the sentences to be ignored:

  * Each phrase corresponds to a subtree of a syntax tree.
  * The deprel of the root must be of specific type (e.g. `adv_mod` for adverbials)
  * All nodes with specified header type are tagged in the sentence, i.e., there can be more than one phase in a same sentence.

* Finally 1000 random sentences that contain the specified phrases are exported to Label Studio where these phrases are manually labelled:

 * free entity
 * bound entity 
 * incorrect entity     
 * unnatural shortening

### Code structure 
TODO: Update this section. It is out of sync.

Folder `estnltk_patches` contains definitions of classes needed for the analysis:

* `EntityTagger`, 
* `StanzaSyntaxTagger2`
* `StanzaSyntaxRetagger` 
* `SuperTagger` 

and additional files containing functions for operating with syntax trees.

File `EntityTagger example.ipynb` contains examples of sentences tagged the taggers.

### Outcomes
Folder `labelstudio` contains the resultinf  
 

## 1\_collection\_splitting.py 

The script takes 3 arguments:

* module and remainder for BlockQuery 
* the name/path of configuration file 

The first two arguments are for parallelisation: `module` specifies the number of parallel tasks and `reminder` specifies the current slice to be processed. The indexing of texts starts with 0.

**Example:** Texts 0, 2, 4, 6, ... will be processed

```bash 
python 1_collection_splitting.py 2 0 conf.ini
```

To process the remainder of texts:

```bash
python 1_collection_splitting.py 2 1 conf.ini
```

Configuration file should have sections `source_database` and `target_database`. Both sections should have fields: 

* `host`, 
* `port`, 
* `database_name`, 
* `username`, 
* `password`, 
* `work_schema`, 
* `role`, 
* `collection` 

filled out. Source database is where the texts will be read from and target database is where the sentences will be saved.
The configuration file name can be given without path (if `conf.ini` file is in the same folder as script) or with full path.

## 2\_add\_stanza\_syntax\_layer.py 

The script takes 3 arguments:

* module and remainder for BlockQuery 
* the name/path of configuration file 

The first two arguments are for parallelisation: `module` specifies the number of parallel tasks and `reminder` specifies the current slice to be processed. The indexing of texts starts with 0.

The configuration file must contain an additional section `stanza_syntax` with field `model_path` has to be defined.
Model path should be defined as:
`model_path=r"path\to\stanza\syntax\tagger"`

**Example:**

```bash
python 2_add_stanza_syntax_layer.py 2 0 conf.ini
``` 


## 3\_add\_ignore_entity\_layer.py 

The script takes 4 arguments:

* module and remainder for BlockQuery 
* the name/path of configuration file 
* the  syntactic relation deprel to be used for phrases

This script can be run if the stanza_syntax layer exists.

**Example:**

```bash
python 3_add_ignore_entity_layer.py advmod 2 0 conf.ini 
```

## 4\_export\_2\_labelstudio.py

The script takes 4 arguments:

* the  syntactic relation deprel to be used for phrases
* the name/path of configuration file
* the name of the output file 
* the initial percentage to be sampled 
* the random seed to make the experiment replicable


**Example:**

```bash
python 4_export_2_labelstudio.py advmod conf.ini ls_export_v1.json 20 12345
```