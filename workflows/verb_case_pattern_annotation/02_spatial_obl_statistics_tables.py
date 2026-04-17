#!/usr/bin/env python
# coding: utf-8

# # Calculating semantic tag statistics for verb-case pairings
# I am trying to answer the research question: How much can a verb and its dependent's case determine the dependent's semantic type?
# This gathers statistics in order to answer that question. It is used to calculate various statistical information about semantic tags for verb and case pairs and put the results into database tables.
# For that purpose we go through the following steps:
# 1. Separate the case tag from the larger feats value.
# 2. Count for each verb how many dependents were annotated as an user specified tag, other tags, semantically annotated at all or recieved no semantic tag
# 3. Calculate percentages for how many of the verb+case pairs had words that are an user specified tag, other tags, annotated and not_annotated based on the counts from step 2.
# 4. Calculate proportion of location/not_location and annotated/not_annotated with binary logarithms. These will later be used to make graph showing if a verb's dependents in a specific case are more likely some user specified tags or other tags and how many of the words are annotated at all
# 5. Find how many unique lemmas each verb+case pair has, calculating its binary algorithm. Used later as a hoverplot's x-axis to show how much the tag proportions can be trusted.

import sqlite3
import pandas as pd
import numpy as np
from estnltk.wordnet import Wordnet
import argparse
import json
import configparser


# FUNCTIONS

def load_config(path):
    """Loads config.
    """
    config = configparser.ConfigParser()
    status = config.read(path) 
    assert status == [path]
    return config


def count_table(db_file, obl_table, tag_col, tag1, tag2 = ''):
    """
    Create a table with pure counts where each verb+case tag has how many of that verb's dependents in that case have user defined 
    semantic tags, other tags, are annotated, aren't annotated and how many times the verb took a dependent in that case
    The user has to insert the semantic tags they want counts of while calling the function *count_table*
    create a table that counts tags for verb+case pairs
    tag1 = first tag to count
    tag2 = tag you want to count together with the second tag
    """
    
    #Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    #define tag name in database table
    if tag2 == '':
        tag = tag1
    else:
        tag = tag1 + '_' + tag2
    
    #delete table if it exists
    cursor.execute("DROP TABLE IF EXISTS verb_case_counts_"+tag)

    # Step 1: Create the new counts table 
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS verb_case_counts_"""+tag+""" (
            verb TEXT,
            verb_compound TEXT,
            morph_case TEXT, 
            my_tag INT,
            other_tags INT,
            annotated INT,
            not_annotated INT,
            verb_case_count INT
        )
    """)

    # Step 2: Aggregate counts
    cursor.execute(
    f"""INSERT INTO verb_case_counts_{tag}
        (verb, verb_compound, morph_case, my_tag, other_tags, annotated, not_annotated, verb_case_count)
        SELECT 
            verb, 
            verb_compound,
            morph_case, 
            COUNT(CASE WHEN {tag_col} like '%|{tag1}|%' OR {tag_col} like '%|{tag2}|%' THEN 1 END) AS my_tag,
            COUNT(CASE WHEN {tag_col} != '' AND {tag_col} not like '%|{tag1}|%' AND {tag_col} not like '%|{tag2}|%' THEN 1 END) AS other_tags,
            COUNT(CASE WHEN {tag_col} != '' THEN 1 END) AS annotated,
            COUNT(CASE WHEN {tag_col} = '' THEN 1 END) AS not_annotated,
            COUNT(*) AS verb_case_count
        FROM {obl_table}
        GROUP BY verb, verb_compound, morph_case
    """
    )

    # Commit and close
    conn.commit()
    conn.close()


def semtype_percentages(db_file, table_name):
    """
    # Uses the counts from the previous table to calculate percentages of each class for every verb+case pair
    # * my_tag_pr = what percentage of annotated words had an user specified tag. User can specify multiple tags
    # * other_tags_pr: what percentage of annotated words didn't have those tags
    # * annotated_pr: what percentage of words were annotated
    # * not_annotated_pr: what percentage of words were not annotated
    # Users have to define database table name
    # Results are put into a new dataframe with a verb, verb compund, case and the percentages specified above
    """

    #connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    #read counts into dataframe
    df = pd.read_sql("SELECT * FROM " + table_name, conn)

    #only take rows that have more than 4 examples
    df = df.loc[df['verb_case_count'] > 4]

    #remove verb+case pairs that have no annotated dependents
    df = df.loc[df['annotated'] != 0]

    # Calculate percentages
    df["my_tag_pr"] = df["my_tag"] / df["annotated"]
    df["other_tags_pr"] = df["other_tags"] / df["annotated"]
    df["annotated_pr"] = df["annotated"] / df["verb_case_count"]
    df["not_annotated_pr"] = df["not_annotated"] / df["verb_case_count"]

    #create a new dataframe with only percentages
    df_pr = df[['verb', 'verb_compound', 'morph_case', "my_tag_pr", 'other_tags_pr', 'annotated_pr', 'not_annotated_pr', 'verb_case_count']].copy()

    # Commit and close
    conn.close()

    return df_pr


def percentage_table(db_file, pr_dataframe, table_name):
    """create a database table for percentages"""

    #connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    #drop table if it exists
    cursor.execute("DROP TABLE IF EXISTS " + table_name)

    # Step 1: Create the new results table 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS """ +  table_name  + """ (
            verb TEXT,
            verb_compound TEXT,
            morph_case TEXT,
            my_tag_pr REAL,
            other_tags_pr REAL,
            annotated_pr REAL,
            not_annotated_pr REAL,
            verb_case_count INT
        )
    """)

    # Step 2: Insert percentages from the dataframe into the database table
    pr_dataframe.to_sql(table_name, conn, if_exists="replace", index=False)

    # Commit and close
    conn.commit()
    conn.close()


def semtype_log(db_file, df_pr, table_name):
    """# This section:
    # * Calculates PMI for tag vs other_tags and annotated vs not_annotated per verb + case pair
    # * Adds logarithms to dataframe and
    # * Transforms the dataframe into a database table
    """

    #replace zeros with 0,001 to avoid taking log from zero
    #not replacing zero with a VERY small number like 1e-10 to avoid graph stretching out
    df_filt = df_pr.replace(0.0, 0.001)

    #calculate binary logarithm for specific tag(s) vs other tags
    df_filt["log2_tag"] = np.log2((df_filt["my_tag_pr"]) / (df_filt["other_tags_pr"]))

    #calculate binary logarithm for annotated/not_annotated
    df_filt["log2_annotation"] = np.log2((df_filt["annotated_pr"]) / (df_filt["not_annotated_pr"]))

    #create a new dataframe with only the proportions
    df_log2 = df_filt[['verb', 'verb_compound', 'morph_case', 'log2_tag', 'log2_annotation', 'verb_case_count']].copy()
    
    #connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    #drop table if it exists
    cursor.execute("DROP TABLE IF EXISTS " + table_name)

    # Step 1: Create the new results table 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS """ +  table_name  + """ (
            verb TEXT,
            verb_compound TEXT,
            morph_case TEXT,
            log2_tag REAL,
            log2_annotation REAL,
            verb_case_count INT
        )
    """)

    # Step 2: Insert percentages from the dataframe into the database table
    df_log2.to_sql(table_name, conn, if_exists="replace", index=False)

    # Commit and close
    conn.commit()
    conn.close()


def unique_lemma_counts(db_file, obl_table, tag_col):
    
    # Find unique lemma counts for verb+case pairs, calculate binary logarithm for them
    #Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Aggregate counts
    query = f"""
        SELECT 
            verb, 
            verb_compound,
            morph_case, 
            COUNT(DISTINCT lemma) AS unique_lemmas
        FROM {obl_table}
        WHERE {tag_col} != ''
        GROUP BY verb, verb_compound, morph_case
    """

    # Make into dataframe to calculate log2
    df_unique_lemmas = pd.read_sql(query, conn)

    #calculate binary logarithm for unique lemmas
    df_unique_lemmas["log2_unique_lemmas"] = np.log2(df_unique_lemmas["unique_lemmas"]) 
    
    # Create a new database table for the unique lemma counts and logarithms
    
    #delete table if it exists
    cursor.execute("DROP TABLE IF EXISTS verb_case_unique_lemmas")

    # Step 1: Create the new counts table 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verb_case_unique_lemmas (
            verb TEXT,
            verb_compound TEXT,
            morph_case TEXT,
            unique_lemmas INT,
            log2_unique_lemmas REAL
        )
    """)

    df_unique_lemmas.to_sql("verb_case_unique_lemmas", conn, if_exists="replace", index=False)

    # Commit and close
    conn.commit()
    conn.close()


def new_columns(table_name, db_file):
    #Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("""
        ALTER TABLE """ + table_name + """
        ADD COLUMN unique_lemmas INTEGER;
    """)

    cursor.execute("""
        ALTER TABLE """ + table_name + """
        ADD COLUMN log2_unique_lemmas REAL;
    """)
    
    conn.commit()
    conn.close()
    

def update_percentages_table(db_file, tag):
    #add unique lemma count column to percentages table too
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(f"""
        ALTER TABLE verb_case_percentages_{tag}
        ADD COLUMN unique_lemmas INTEGER;
    """)

    conn.commit()
    conn.close()


def unique_lemma(db_file, table_name):
    #Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        UPDATE {table_name}
        SET unique_lemmas = (
            SELECT unique_lemmas
            FROM verb_case_unique_lemmas
            WHERE 
                verb_case_unique_lemmas.verb = {table_name}.verb
                AND verb_case_unique_lemmas.verb_compound = {table_name}.verb_compound
                AND verb_case_unique_lemmas.morph_case = {table_name}.morph_case
    );
    """)

    # Commit and close
    conn.commit()
    conn.close()


def unique_lemma_log(db_file, table_name):
    #Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        UPDATE {table_name}
        SET log2_unique_lemmas = (
            SELECT log2_unique_lemmas
            FROM verb_case_unique_lemmas
            WHERE 
                verb_case_unique_lemmas.verb = {table_name}.verb
                AND verb_case_unique_lemmas.verb_compound = {table_name}.verb_compound
                AND verb_case_unique_lemmas.morph_case = {table_name}.morph_case
    );
    """)

    # Commit and close
    conn.commit()
    conn.close()


def verb_to_df(db_file, table_name):
    """extract verbs from database statistics table and put them in a dataframe """
    #Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    #query verbs from database table
    query = f"SELECT DISTINCT verb, verb_compound FROM {table_name}"
    #put results into dataframe
    df_verbs = pd.read_sql(query, conn)
    #combine verb and compound, strip extra spaces
    df_verbs['full_verb'] = (df_verbs['verb'] + ' ' + df_verbs['verb_compound']).str.strip()
    #close database connection
    conn.close()

    return df_verbs


def synset_count_df(dataframe):
    """find Wordnet synset counts for each verb, classify into 4 classes, add to dataframe"""
    #get verbs out as a list
    fullverb = dataframe['full_verb'].tolist()

    #create wordnet object
    wn = Wordnet()
    
    #find synset count for each verb, put counts into 3 classes
    synset_count = []
    for verb in fullverb:
        count = len(wn[verb, 'v'])
        if count == 0:
            synset_count.append('not in Estonian Wordnet')
        elif count == 1:
            synset_count.append('1')
        elif count == 2 or count == 3:
            synset_count.append('2-3')
        else:
            synset_count.append('>3')

    #add synset count to dataframe
    dataframe['synset_count'] = synset_count

    return dataframe


def synset_count_db(db_file, table_name, dataframe):
    """add synset counts to database statistics table"""
    #Connect to database
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    #insert all values into the temp table
    dataframe.to_sql('temp_synset', conn, if_exists="replace", index=False)

    #add synset count column to statistics table
    cursor.execute(f"""
        ALTER TABLE {table_name}
        ADD COLUMN synset_count TEXT;
    """)

    #fill synset count column with data from temporary table
    cursor.execute(
        f"""
        UPDATE {table_name}
        SET synset_count = (
            SELECT synset_count
            FROM temp_synset
            WHERE 
                temp_synset.verb = {table_name}.verb
                AND temp_synset.verb_compound = {table_name}.verb_compound
    );
    """)

    cursor.execute("DROP TABLE IF EXISTS temp_synset")

    # Commit and close
    conn.commit()
    conn.close()


def synsets_to_db(db_file, table_name):
    """go through all steps to add synset counts to database table"""

    #extract verbs from database table and put them in a dataframe 
    df_verbs = verb_to_df(db_file, table_name)

    #find Wordnet synset counts for each verb, classify into 4 classes, add them to dataframe for each verb
    df_synsets = synset_count_df(df_verbs)

    #add a verbs's synset counts to database table
    synset_count_db(db_file, table_name, df_synsets)



def run(conf_file):
    
    DB_FILE = conf_file["configuration"]["database"]
    OBL_TABLE = conf_file["configuration"]["obl_table"]
    TAG_COL = conf_file["configuration"]["tags_column"]
    TAG = conf_file["configuration"]["target_tag"]

    # ## 1. Count semantic tags
    #create count table for location vs other tags
    print("Creating counts table...")
    count_table(DB_FILE, OBL_TABLE, TAG_COL, TAG)

    # ## 2. Calculate percentages
    #percentage dataframe for location
    print("Creating percentages table...")
    df_pr_loc = semtype_percentages(DB_FILE, f'verb_case_counts_{TAG}')
    percentage_table(DB_FILE, df_pr_loc, f'verb_case_percentages_{TAG}')

    # ## 3. Calculate proportions
    # To better illustrate whether a verb+case pair prefers the user specified tag (ie location) or all the other tags (ie time+state+event), 
    # we calculate pointwise mutual information by dividing an user specified tag(s) percentage by every other_tags percentage and taking a binary logarithm of it. 
    #create log table for locations
    print("Calculating proportions...")
    semtype_log(DB_FILE, df_pr_loc, f'verb_case_log_{TAG}')

    print("Creating unique lemma counts...")
    # ## 4. Find how many different words each verb+case pair has
    # This is to show how trustworthy the tag proportions are for a verb+case pair. 
    # The more different words a verb's dependents in said case are, the more trustworthy the results are, because the sample was larger
    unique_lemma_counts(DB_FILE, OBL_TABLE, TAG_COL)
    # #### Add unique lemma columns to log statistics tables to ease hoverplot creation
    new_columns(f'verb_case_log_{TAG}', DB_FILE)
    update_percentages_table(DB_FILE, TAG)
    # #### Add unique lemma count data to log statistics table and percentages table
    unique_lemma(DB_FILE, f'verb_case_log_{TAG}')
    unique_lemma(DB_FILE, f'verb_case_percentages_{TAG}')
    # #### Add binary logarithm data of unique lemmas to log statistics table
    unique_lemma_log(DB_FILE, f'verb_case_log_{TAG}')

    # 5. Adding the number of synsets a verb has to verb+case data
    # In this we add the number of synsets a verb has to the database. We do this to see whether the certainty of a verb's dependent in said case being one semantic type can be correlated to the amount of meanings that word has. So basically is it more likely that **a verb has different valency patterns because it has multiple meanings** OR **because one meaning can have multiple valency patterns**
    # This is done by:
    # 1. extracting verbs from a database table and putting them into a dataframe
    # 2. finding Wordnet synset counts for each verb
    # 3. classifying the verbs into 4 classes based on the counts: not in Estonian Wordnet, 1 meaning, 2-3 meanings, >3 meanings
    # 4. adding the count classifications to the verb dataframe
    # 5. turning the dataframe into a database table
    # 6. importing the synset_count column from the newly created table into a previously existing table used for creating hoverplots
    print("Adding synset counts...")
    synsets_to_db(DB_FILE, f'verb_case_log_{TAG}') #this does work if the column doesn't already exist

    print("Done!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    run(config)


if __name__ == "__main__":
    main()


