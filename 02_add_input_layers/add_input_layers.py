from estnltk.storage import PostgresStorage

from experiment_taggers.experiment_1.am_experiment_1_tagger import AMExperiment1Tagger
from experiment_taggers.experiment_1.gm_experiment_1_tagger import GMExperiment1Tagger
from experiment_taggers.experiment_10.am_experiment_10_tagger import AMExperiment10Tagger
from experiment_taggers.experiment_10.gm_experiment_10_tagger import GMExperiment10Tagger
from experiment_taggers.experiment_11.am_experiment_11_tagger import AMExperiment11Tagger
from experiment_taggers.experiment_11.gm_experiment_11_tagger import GMExperiment11Tagger
from experiment_taggers.experiment_12.am_experiment_12_tagger import AMExperiment12Tagger
from experiment_taggers.experiment_12.gm_experiment_12_tagger import GMExperiment12Tagger
from experiment_taggers.experiment_13.am_experiment_13_tagger import AMExperiment13Tagger
from experiment_taggers.experiment_13.gm_experiment_13_tagger import GMExperiment13Tagger
from experiment_taggers.experiment_14.am_experiment_14_tagger import AMExperiment14Tagger
from experiment_taggers.experiment_14.gm_experiment_14_tagger import GMExperiment14Tagger
from experiment_taggers.experiment_2.am_experiment_2_tagger import AMExperiment2Tagger
from experiment_taggers.experiment_2.gm_experiment_2_tagger import GMExperiment2Tagger
from experiment_taggers.experiment_3.am_experiment_3_tagger import AMExperiment3Tagger
from experiment_taggers.experiment_3.gm_experiment_3_tagger import GMExperiment3Tagger
from experiment_taggers.experiment_3_2.am_experiment_3_2_tagger import AMExperiment3_2Tagger
from experiment_taggers.experiment_3_2.gm_experiment_3_2_tagger import GMExperiment3_2Tagger
from experiment_taggers.experiment_4.am_experiment_4_tagger import AMExperiment4Tagger
from experiment_taggers.experiment_4.gm_experiment_4_tagger import GMExperiment4Tagger
from experiment_taggers.experiment_4_2.am_experiment_4_2_tagger import AMExperiment4_2Tagger
from experiment_taggers.experiment_4_2.gm_experiment_4_2_tagger import GMExperiment4_2Tagger
from experiment_taggers.experiment_5.am_experiment_5_tagger import AMExperiment5Tagger
from experiment_taggers.experiment_5.gm_experiment_5_tagger import GMExperiment5Tagger
from experiment_taggers.experiment_6.am_experiment_6_tagger import AMExperiment6Tagger
from experiment_taggers.experiment_6.gm_experiment_6_tagger import GMExperiment6Tagger
from experiment_taggers.experiment_6_2.am_experiment_6_2_tagger import AMExperiment6_2Tagger
from experiment_taggers.experiment_6_2.gm_experiment_6_2_tagger import GMExperiment6_2Tagger
from experiment_taggers.experiment_7.am_experiment_7_tagger import AMExperiment7Tagger
from experiment_taggers.experiment_7.gm_experiment_7_tagger import GMExperiment7Tagger
from experiment_taggers.experiment_7_2.am_experiment_7_2_tagger import AMExperiment7_2Tagger
from experiment_taggers.experiment_7_2.gm_experiment_7_2_tagger import GMExperiment7_2Tagger
from experiment_taggers.experiment_8.am_experiment_8_tagger import AMExperiment8Tagger
from experiment_taggers.experiment_8.gm_experiment_8_tagger import GMExperiment8Tagger
from experiment_taggers.experiment_8_2.am_experiment_8_2_tagger import AMExperiment8_2Tagger
from experiment_taggers.experiment_8_2.gm_experiment_8_2_tagger import GMExperiment8_2Tagger
from experiment_taggers.experiment_9.am_experiment_9_tagger import AMExperiment9Tagger
from experiment_taggers.experiment_9.gm_experiment_9_tagger import GMExperiment9Tagger


def add_input_layers(collection_name: str):
    storage = PostgresStorage(pgpass_file='../db_conn.pgpass',
                              password='',
                              schema='syntaxexperiments'
                              )

    collection = storage[collection_name]

    #gm_experiment_1 = GMExperiment1Tagger()
    #am_experiment_1 = AMExperiment1Tagger()
    #collection.create_layer(tagger=gm_experiment_1)
    #collection.create_layer(tagger=am_experiment_1)

    #gm_experiment_2 = GMExperiment2Tagger()
    #am_experiment_2 = AMExperiment2Tagger()
    #collection.create_layer(tagger=gm_experiment_2)
    #collection.create_layer(tagger=am_experiment_2)

    gm_experiment_3 = GMExperiment3Tagger()
    am_experiment_3 = AMExperiment3Tagger()
    collection.create_layer(tagger=gm_experiment_3)
    collection.create_layer(tagger=am_experiment_3)

    gm_experiment_3_2 = GMExperiment3_2Tagger()
    am_experiment_3_2 = AMExperiment3_2Tagger()
    collection.create_layer(tagger=gm_experiment_3_2)
    collection.create_layer(tagger=am_experiment_3_2)

    gm_experiment_4 = GMExperiment4Tagger()
    am_experiment_4 = AMExperiment4Tagger()
    collection.create_layer(tagger=gm_experiment_4)
    collection.create_layer(tagger=am_experiment_4)

    gm_experiment_4_2 = GMExperiment4_2Tagger()
    am_experiment_4_2 = AMExperiment4_2Tagger()
    collection.create_layer(tagger=gm_experiment_4_2)
    collection.create_layer(tagger=am_experiment_4_2)

    #gm_experiment_5 = GMExperiment5Tagger()
    #am_experiment_5 = AMExperiment5Tagger()
    #collection.create_layer(tagger=gm_experiment_5)
    #collection.create_layer(tagger=am_experiment_5)

    gm_experiment_6 = GMExperiment6Tagger()
    am_experiment_6 = AMExperiment6Tagger()
    collection.create_layer(tagger=gm_experiment_6)
    collection.create_layer(tagger=am_experiment_6)

    gm_experiment_6_2 = GMExperiment6_2Tagger()
    am_experiment_6_2 = AMExperiment6_2Tagger()
    collection.create_layer(tagger=gm_experiment_6_2) #not sure about the am in edt
    collection.create_layer(tagger=am_experiment_6_2)

    gm_experiment_7 = GMExperiment7Tagger()
    am_experiment_7 = AMExperiment7Tagger()
    collection.create_layer(tagger=gm_experiment_7)
    collection.create_layer(tagger=am_experiment_7)

    gm_experiment_7_2 = GMExperiment7_2Tagger()
    am_experiment_7_2 = AMExperiment7_2Tagger()
    collection.create_layer(tagger=gm_experiment_7_2)
    collection.create_layer(tagger=am_experiment_7_2)

    gm_experiment_8 = GMExperiment8Tagger()
    am_experiment_8 = AMExperiment8Tagger()
    collection.create_layer(tagger=gm_experiment_8)
    collection.create_layer(tagger=am_experiment_8)

    gm_experiment_8_2 = GMExperiment8_2Tagger()
    am_experiment_8_2 = AMExperiment8_2Tagger()
    collection.create_layer(tagger=gm_experiment_8_2)
    collection.create_layer(tagger=am_experiment_8_2)

    #gm_experiment_9 = GMExperiment9Tagger()
    #am_experiment_9 = AMExperiment9Tagger()
    #collection.create_layer(tagger=gm_experiment_9)
    #collection.create_layer(tagger=am_experiment_9)

    #gm_experiment_10 = GMExperiment10Tagger()
    #am_experiment_10 = AMExperiment10Tagger()
    #collection.create_layer(tagger=gm_experiment_10)
    #collection.create_layer(tagger=am_experiment_10)

    #gm_experiment_11 = GMExperiment11Tagger()
    #am_experiment_11 = AMExperiment11Tagger()
    #collection.create_layer(tagger=gm_experiment_11)
    #collection.create_layer(tagger=am_experiment_11)

    #gm_experiment_12 = GMExperiment12Tagger()
    #am_experiment_12 = AMExperiment12Tagger()
    #collection.create_layer(tagger=gm_experiment_12)
    #collection.create_layer(tagger=am_experiment_12)

    #gm_experiment_13 = GMExperiment13Tagger(collection=collection)
    #am_experiment_13 = AMExperiment13Tagger(collection=collection)
    #collection.create_layer(tagger=gm_experiment_13)
    #collection.create_layer(tagger=am_experiment_13)

    #gm_experiment_14 = GMExperiment14Tagger(collection=collection)
    #am_experiment_14 = AMExperiment14Tagger(collection=collection)
    #collection.create_layer(tagger=gm_experiment_14)
    #collection.create_layer(tagger=am_experiment_14)
    storage.close()




if __name__ == '__main__':
    add_input_layers(collection_name='est_ud')
    add_input_layers(collection_name='edt')
