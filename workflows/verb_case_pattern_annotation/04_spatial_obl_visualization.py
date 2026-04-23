#!/usr/bin/env python
# coding: utf-8

# # Hoverplot for tag distribution by verb-case pairing
# 
# This notebook creates hoverplots. The hoverplots show the location of a verb and case pair based on two values:
# 
# 1. y-axis: How many of the verb's dependents in said case have an user specified tag(s) or other tags. The higher the score the more dependents have the user speficied tag, the lower the score the more dependents have some other tag.
# 2. x-axis had two possibilities:
#     * How many of the the verb's dependents in said case were semantically annotated at all. The higher the score the more words were annotated, the lower the score the more words recieved no annotation.
#     * How many unique dependents a verb has in said case that are annotated. The higher the score the more words unique annotated dependents the verb had in that case, the lower the score the less unique dependents in said case a verb has.
# 
# The hoverplots are created by going through the following steps:
# 1. reading database table with data used for the hoverplot into a dataframe
# 2. finding example dependents for each verb-case pair to show on hover. There are 3 classes of example dependents: user_specified tag, other tag, not_annotated
# 3. adding new hovername column to the dataframe. For each datapoint, this shows on hover: *verb verb_compound (case): usertag_example, othertag_example, not_annotated_example*. For example: *üürima välja (ad): tänaval, kaalutlustel, ajal*. If a class has no examples, then shows *[puudub]* instead of an example
# 4. defining what kind of hoverplot will be created
# 
# This notebook reuses some code made by Kaire, which can be found [here](https://github.com/estnltk/syntax_experiments/blob/verb_templates/workflows/006_analysis_of_manually_annotated_actor_patterns/06_analysis_illustrations/05_verb_live_vs_nonlive_hoverplot.ipynb).

# In[1]:


import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from scipy.signal import argrelextrema
import plotly.graph_objects as go
import copy
import argparse
import json
import configparser


# ## Functions

def load_config(path):
    """Loads config.
    """
    config = configparser.ConfigParser()
    status = config.read(path) 
    assert status == [path]
    return config


def read(database, table_name):
    """read data in from database"""
    #connect to database 
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    #insert data to dataframe
    df_log = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    return df_log


def tag(database, obl_table, tag_col, base_df, column_name, tags, deptype = 'obl'):
    """finds dependents with user specified tags for each verb+case pair"""
    #connect to database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    if deptype == 'obl':
        subqs = []
        for tag in tags:
            subqs.append(f"{tag_col} like '%|{tag}|%'")

        subq = " OR ".join(subqs) + " "
        # Fetch a single form per (verb, verb_compound, morph_case, tag)
        query = f"""
        SELECT verb, verb_compound, morph_case, MIN(form) as {column_name}
        FROM {obl_table}
        WHERE {subq}
        GROUP BY verb, verb_compound, morph_case;
        """

        # Load the filtered table into a DataFrame
        df_other = pd.read_sql(query, conn)

        # Merge with df_log based on verb, verb_compound, morph_case
        base_df = base_df.merge(df_other, on=['verb', 'verb_compound', 'morph_case'], how='left')

    elif deptype == 'adv':
        # Fetch an example form per (verb, verb_compound, tag)
        query = f"""
        SELECT verb, verb_compound, MIN(form) as {column_name}
        FROM advmod
        WHERE ekilex_tag IN {tags}
        GROUP BY verb, verb_compound;
        """

        # Load the filtered table into a DataFrame
        df_other = pd.read_sql(query, conn)

        # Merge with df_log based on verb, verb_compound
        base_df = base_df.merge(df_other, on=['verb', 'verb_compound'], how='left')

    return base_df


def not_annotated(database,  obl_table, tag_col, base_df, deptype = 'obl'):
    """finds dependents that haven't been annotated"""
    #connect to database
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    if deptype == 'obl':
         # Fetch a single form per (verb, verb_compound, morph_case, tag)
        query = f"""
        SELECT verb, verb_compound, morph_case, MIN(form) as not_annotated_example
        FROM {obl_table}
        WHERE {tag_col} = ''
        GROUP BY verb, verb_compound, morph_case;
        """
    
        # Load the filtered table into a DataFrame
        df_notag = pd.read_sql(query, conn)

        # Merge with df_log based on verb, verb_compound, morph_case
        base_df = base_df.merge(df_notag, on=['verb', 'verb_compound', 'morph_case'], how='left')

    if deptype == 'adv':
         # Fetch a single form per (verb, verb_compound, tag)
        query = """
        SELECT verb, verb_compound, MIN(form) as not_annotated_example
        FROM advmod
        WHERE ekilex_tag is null
        GROUP BY verb, verb_compound;
        """
    
        # Load the filtered table into a DataFrame
        df_notag = pd.read_sql(query, conn)

        # Merge with df_log based on verb, verb_compound, morph_case
        base_df = base_df.merge(df_notag, on=['verb', 'verb_compound'], how='left')

    return base_df


def hovername(base_df, deptype = 'obl'):
    """add new column for what's shown on hover"""
    base_df = base_df.fillna('[puudub]')

    if deptype == 'obl':
        base_df['hovername'] = (base_df['verb'] + ' ' + base_df['verb_compound']+ ' (' + base_df['morph_case']+ ')' 
                           + ': ' + base_df['tag_example'] + ', ' + base_df['other_example'] + ', ' + base_df['not_annotated_example'])
    elif deptype == 'adv':
        base_df['hovername'] = (base_df['verb'] + ' ' + base_df['verb_compound'] 
                           + ': ' + base_df['tag_example'] + ', ' + base_df['other_example'] + ', ' + base_df['not_annotated_example'])
    return base_df


def siksaki_alumised_punktid(df, y_col):
    """n lines zig-zag line bottom points for straighter line"""
    min_indices = argrelextrema(df[y_col].values, np.less)[0] #finds indices where the y-value is less than its neighbor
    lower_points = df.iloc[min_indices]
    return lower_points


def hoverplot(base_df, x_axis, x_name, y_name, filename, folder):
    """creates colored hoverplots"""
    #desired order of legend elements
    desired_order = [
    'not in Estonian Wordnet',
    '1',
    '2-3',
    '>3'
    ]
    
    fig = px.scatter(base_df, x=x_axis, y='log2_tag', color="synset_count", hover_name= 'hovername', 
                     labels = {x_axis: x_name, 'log2_tag': y_name, 'synset_count': 'Senses in Estonian Wordnet'},
                    category_orders={'synset_count': desired_order})

    fig.update_layout(hovermode='closest')

    #define axis tick intervals
    tickvals= list(range(-10, 13, 2))

    #renaming axis ticks
    tickvals = list(range(-10, 13, 2))
    def log2_to_ratio(log2_val):
        odds = 2 ** log2_val
        left = 100 * odds / (1 + odds)
        right = 100 - left
        if log2_val in [-8, 8]:
            return f"{left:.1f}:{right:.1f}"
        else:
            return f"{int(round(left))}:{int(round(right))}"
    
    ticktext_y = [log2_to_ratio(val) for val in tickvals]
    ticktext_x = [str(2 ** val) for val in tickvals]  # convert to original word counts

    fig.update_xaxes(tickvals=tickvals, ticktext=ticktext_x) 
    fig.update_yaxes(tickvals=tickvals, ticktext=ticktext_y)

    fig.add_hline(
        y=2,
        line_dash="solid",
        line_color="red",
        line_width=2
    )
    
    #lower color opacity for overlapping datapoints
    fig.update_traces({'opacity': 0.25}, selector={'name': 'not in Estonian Wordnet'})
    fig.update_traces({'opacity': 0.25}, selector={'name': '1'})
    fig.update_traces({'opacity': 0.25}, selector={'name': '2-3'})
    fig.update_traces({'opacity': 0.25}, selector={'name': '>3'})

    filepath = os.path.join(folder,filename)
    fig.write_html(filepath + ".html")
    #fig.show()


def colorless_hoverplot(base_df, x_axis, x_name, y_name, filename, folder):
    """creates colorless hoverplots"""
    fig = px.scatter(base_df, x=x_axis, y='log2_tag', hover_name= 'hovername', 
                     labels = {x_axis: x_name, 'log2_tag': y_name})

    fig.update_layout(hovermode='closest')

    fig.update_traces({'opacity': 0.25})

    tickvals= list(range(-10, 13, 2))

    #renaming axis ticks
    tickvals = list(range(-10, 13, 2))
    def log2_to_ratio(log2_val):
        odds = 2 ** log2_val
        left = 100 * odds / (1 + odds)
        right = 100 - left
        if log2_val in [-8, 8]:
            return f"{left:.1f}:{right:.1f}"
        else:
            return f"{int(round(left))}:{int(round(right))}"
    
    ticktext_y = [log2_to_ratio(val) for val in tickvals]
    ticktext_x = [str(2 ** val) for val in tickvals]  # convert to original word counts

    fig.update_xaxes(tickvals=tickvals, ticktext=ticktext_x) 
    fig.update_yaxes(tickvals=tickvals, ticktext=ticktext_y)

    fig.add_hline(
        y=2,
        line_dash="solid",
        line_color="red",
        line_width=2
    )
    
    filepath = os.path.join(folder,filename)
    fig.write_html(filepath + ".html")
    #fig.show()


def colorless_hoverplot2(base_df, x_axis, x_name, y_name, filename, folder, lines_df):
    """creates colorless hoverplots withn n lines"""
    
    fig = px.scatter(base_df, x=x_axis, y='log2_tag', hover_name= 'hovername', 
                     labels = {x_axis: x_name, 'log2_tag': y_name}, width=4000, height=2600)

    fig.update_layout(hovermode='closest')
    fig.update_traces({'opacity': 0.25})
    tickvals= list(range(-10, 13, 2))

    #renaming axis ticks
    tickvals = list(range(-10, 13, 2))
    def log2_to_ratio(log2_val):
        odds = 2 ** log2_val
        left = 100 * odds / (1 + odds)
        right = 100 - left
        if log2_val in [-8, 8]:
            return f"{left:.1f}:{right:.1f}"
        else:
            return f"{int(round(left))}:{int(round(right))}"
    
    ticktext_y = [log2_to_ratio(val) for val in tickvals]
    ticktext_x = [str(2 ** val) for val in tickvals]  # convert to original word counts

    fig.update_xaxes(tickvals=tickvals, ticktext=ticktext_x) 
    fig.update_yaxes(tickvals=tickvals, ticktext=ticktext_y)

    fig.add_hline(
        y=2,
        line_dash="solid",
        line_color="red",
        line_width=2
    )
    
    fig.add_hline(
        y=0,
        line_dash="solid",
        line_color="black",
        line_width=2
    )
    
    # silendatud jooned (siksaki alumise punktid)
    tmp_df = siksaki_alumised_punktid(lines_df, "log2_y_pos80")
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos80"] ,
        mode='lines',
        line=dict(color='orange', width=3),
        name='80'
    ))
    tmp_df = siksaki_alumised_punktid(lines_df, "log2_y_pos90")
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos90"] ,
        mode='lines',
        line=dict(color='lightgreen', width=3),
        name='90'
    ))
    tmp_df = siksaki_alumised_punktid(lines_df, "log2_y_pos70")
    #crossing = tmp_df[tmp_df["log2_y_pos70"]==tmp_df["log2_y_pos30"]]
    #tmp_df = tmp_df[crossing.loc[crossing.index.max()].name-5:]
    tmp_df = tmp_df.iloc[5:]
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos70"] ,
        mode='lines',
        line=dict(color='purple', width=3),
        name='70'
    ))
    tmp_df = siksaki_alumised_punktid(lines_df, "log2_y_pos30")
    #crossing = tmp_df[tmp_df["log2_y_pos70"]==tmp_df["log2_y_pos30"]]
    #tmp_df = tmp_df[crossing.loc[crossing.index.max()].name-5:]
    tmp_df = tmp_df.iloc[5:]
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos30"] ,
        mode='lines',
        line=dict(color='deeppink', width=3),
        name='30'
    ))
    tmp_df = siksaki_alumised_punktid(lines_df, "log2_y_pos20")
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos20"] ,
        mode='lines',
        line=dict(color='blue', width=3),
        name='20'
    ))
    tmp_df = siksaki_alumised_punktid(lines_df, "log2_y_pos10")
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos10"] ,
        mode='lines',
        line=dict(color='yellow', width=3),
        name='10'
    ))
    
    
    
    # esialgsed siksak jooned
    fig.add_trace(go.Scatter(
        x=lines_df["log2_x"] , #list(base_df[x_axis]),
        y=lines_df["log2_y_pos80"] ,
        mode='lines',
        line=dict(color='darkgrey', width=3),
        name='80'
    ))
    fig.add_trace(go.Scatter(
        x=lines_df["log2_x"] , #list(base_df[x_axis]),
        y=lines_df["log2_y_pos90"] ,
        mode='lines',
        line=dict(color='darkgrey', width=3),
        name='90'
    ))
    fig.add_trace(go.Scatter(
        x=lines_df["log2_x"] , #list(base_df[x_axis]),
        y=lines_df["log2_y_pos70"] ,
        mode='lines',
        line=dict(color='darkgrey', width=3),
        name='70'
    ))
    fig.add_trace(go.Scatter(
        x=lines_df["log2_x"] , #list(base_df[x_axis]),
        y=lines_df["log2_y_pos30"] ,
        mode='lines',
        line=dict(color='darkgrey', width=3),
        name='30'
    ))
    fig.add_trace(go.Scatter(
        x=lines_df["log2_x"] , #list(base_df[x_axis]),
        y=lines_df["log2_y_pos20"] ,
        mode='lines',
        line=dict(color='darkgrey', width=3),
        name='20'
    ))
    fig.add_trace(go.Scatter(
        x=lines_df["log2_x"] , #list(base_df[x_axis]),
        y=lines_df["log2_y_pos10"] ,
        mode='lines',
        line=dict(color='darkgrey', width=3),
        name='10'
    ))
    
    # pluss-miinus 1 siksak jooned
    tmp_df = lines_df.iloc[20:]
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos80_p1"] ,
        mode='lines',
        line=dict(color='orangered', width=3),
        name='80+1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos80_m1"] ,
        mode='lines',
        line=dict(color='orangered', width=3),
        name='80-1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos90_p1"] ,
        mode='lines',
        line=dict(color='darkgreen', width=3),
        name='90+1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos90_m1"] ,
        mode='lines',
        line=dict(color='darkgreen', width=3),
        name='90-1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos70_p1"] ,
        mode='lines',
        line=dict(color='darksalmon', width=3),
        name='70+1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos70_m1"] ,
        mode='lines',
        line=dict(color='darksalmon', width=3),
        name='70-1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos20_p1"] ,
        mode='lines',
        line=dict(color='blueviolet', width=3),
        name='20+1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos20_m1"] ,
        mode='lines',
        line=dict(color='blueviolet', width=3),
        name='20-1'
    ))    
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos10_p1"] ,
        mode='lines',
        line=dict(color='yellowgreen', width=3),
        name='10+1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos10_m1"] ,
        mode='lines',
        line=dict(color='yellowgreen', width=3),
        name='10-1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos30_p1"] ,
        mode='lines',
        line=dict(color='hotpink', width=3),
        name='30+1'
    ))
    fig.add_trace(go.Scatter(
        x=tmp_df["log2_x"] , #list(base_df[x_axis]),
        y=tmp_df["log2_y_pos30_m1"] ,
        mode='lines',
        line=dict(color='hotpink', width=3),
        name='30-1'
    ))
    
    filepath = os.path.join(folder,filename)
    fig.write_html(filepath + ".html")

    #fig.show()


def prepare_data(database, obl_table, tag_col, table_name, user_tags, other_tags, deptype = 'obl'):
    """prepare data for hoverplotting"""
    dataframe = read(database, table_name)
    dataframe = tag(database, obl_table, tag_col, dataframe, 'tag_example', user_tags, deptype)
    dataframe = tag(database, obl_table, tag_col, dataframe, 'other_example', other_tags, deptype)
    dataframe = not_annotated(database, obl_table, tag_col, dataframe, deptype)
    dataframe = hovername(dataframe, deptype)
    return dataframe



def run(conf_file):

    DATABASE = conf_file["configuration"]["database"]
    OBL_TABLE = conf_file["configuration"]["obl_table"]
    TAG_COL = conf_file["configuration"]["tags_column"]
    CONFIDENCE_VALUES = conf_file["configuration"]["confidence_values_table"]
    TARGET_TAG = conf_file["configuration"]["target_tag"].split(",")
    OTHER_TAGS = conf_file["configuration"]["other_tags"].split(",")
    RES_DIR = conf_file["configuration"]["dir_scatter_results"]

    # ## Prepare data for plotting
    # User has to define:
    # 1. database table name
    # 2. what tags the user is interested in
    # 3. all other tags in the data

    lines_df = read(DATABASE, CONFIDENCE_VALUES)
    df_log_loc = prepare_data(DATABASE, OBL_TABLE, TAG_COL, f'verb_case_log_{TARGET_TAG[0]}', 
                              TARGET_TAG, 
                              OTHER_TAGS)



    # ## Create hoverplots
    # 
    # This section creates hoverplots from the data compiled in the above sections.
    # The user has to define: 
    # * dataframe the info is from
    # * column used as x_axis
    # * x-axis label
    # * y_axis label
    # * filename for the saved hoverplot, needs to be htlm
    #     

    # ### 1. tag-not_tag vs annotated-not_annotated
    hoverplot(df_log_loc, 'log2_annotation', 'not_annotated vs annotated', f'{TARGET_TAG[0]} vs other tags', f'{TARGET_TAG[0]}_verbcase_annotated_unannotated', RES_DIR)

    # ### 2. tag-not_tag vs unique dependents
    # 1. y-axis: Whether the verb's dependents in said case are more likely locations or not locations. The higher the score the more likely dependents are locations, the lower the score the more likely dependents aren't locations
    # 2. x-axis: How many unique dependents a verb has in said case that are annotated. The higher the score the more words unique annotated dependents the verb had in that case, the lower the score the less unique dependents in said case a verb has
    colorless_hoverplot(df_log_loc, 'log2_unique_lemmas', 'unique annotated dependents', 
              f'ratio of {TARGET_TAG[0]}:other tags', f'{TARGET_TAG[0]}_all_colorless', RES_DIR)

    colorless_hoverplot2(df_log_loc, 'log2_unique_lemmas', 'unique annotated dependents', 
              f'ratio of {TARGET_TAG[0]}:other tags', f'{TARGET_TAG[0]}_scatter_w_lines_multi', RES_DIR, lines_df)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    run(config)


if __name__ == "__main__":
    main()


