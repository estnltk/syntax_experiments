#!/usr/bin/env python
# coding: utf-8

# # Hoverplot for tag distribution by verb-case pairing

# This notebook creates hoverplots. The hoverplots show the location of a verb and case pair based on two values:
# 1. y-axis: How many of the verb's dependents in said case have an user specified tag(s) or other tags. The higher the score the more dependents have the user speficied tag, the lower the score the more dependents have some other tag.
# 2. x-axis had two possibilities:
#     * How many of the the verb's dependents in said case were semantically annotated at all. The higher the score the more words were annotated, the lower the score the more words recieved no annotation.
#     * How many unique dependents a verb has in said case that are annotated. The higher the score the more words unique annotated dependents the verb had in that case, the lower the score the less unique dependents in said case a verb has.

# The hoverplots are created by going through the following steps:
# 1. reading database table with data used for the hoverplot into a dataframe
# 2. finding example dependents for each verb-case pair to show on hover. There are 3 classes of example dependents: user_specified tag, other tag, not_annotated
# 3. adding new hovername column to the dataframe.
# 4. defining what kind of hoverplot will be created

# This notebook reuses some code made by Kaire, which can be found [here](https://github.com/estnltk/syntax_experiments/blob/verb_templates/workflows/006_analysis_of_manually_annotated_actor_patterns/06_analysis_illustrations/05_verb_live_vs_nonlive_hoverplot.ipynb).

import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from scipy.signal import argrelextrema
from scipy.interpolate import UnivariateSpline
import plotly.graph_objects as go
import copy
import argparse
import json
import configparser
import re


# ## Functions

def load_config(path):
    """Loads config.
    """
    config = configparser.ConfigParser()
    status = config.read(path) 
    assert status == [path]
    return config



# DATABASE FUNCTIONS

def read(database, table_name):
    """read data in from database"""
    #connect to database 
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    #insert data to dataframe
    df_log = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    conn.close()
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

    conn.close()
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

    conn.close()
    return base_df



# PLOTTING FUNCTIONS

def hovername1(base_df, deptype = 'obl'):
    """DEPRECATED! add new column for what's shown on hover"""
    base_df = base_df.fillna('[puudub]')

    if deptype == 'obl':
        base_df['hovername'] = (base_df['verb'] + ' ' + base_df['verb_compound']+ ' (' + base_df['morph_case']+ ')' 
                           + ': ' + base_df['tag_example'] + ', ' + base_df['other_example'] + ', ' + base_df['not_annotated_example'])
    elif deptype == 'adv':
        base_df['hovername'] = (base_df['verb'] + ' ' + base_df['verb_compound'] 
                           + ': ' + base_df['tag_example'] + ', ' + base_df['other_example'] + ', ' + base_df['not_annotated_example'])
    return base_df


def hovername(base_df, examples_df, deptype='obl'):
    base_df = base_df.fillna('[puudub]')
    examples_df = examples_df.copy()

    # -----------------------------
    # 1. Parse JSON examples
    # -----------------------------
    def parse_examples(val):
        if pd.isna(val):
            return []
        if isinstance(val, list):
            ex = val
        else:
            try:
                ex = json.loads(val)
            except Exception:
                return []

        if not isinstance(ex, list):
            return []

        return [
            e.get("highlighted") or e.get("sentence", "")
            for e in ex
            if isinstance(e, dict)
        ]

    examples_df["examples_list"] = examples_df["examples"].apply(parse_examples)

    # -----------------------------
    # 2. Build tag-level blocks
    # -----------------------------
    def build_tag_block(row):
        tag = row["tag"]
        pct = row["pct"]
        examples = row["examples_list"]

        block = f"<b>{tag}</b> ({pct:.1f}%)"

        for ex in examples[:3]:
            block += f"<br>{ex}"

        return block

    examples_df["tag_block"] = examples_df.apply(build_tag_block, axis=1)

    # -----------------------------
    # 3. Aggregate to verbcase level
    # -----------------------------
    hover_df = (
        examples_df
        .sort_values("pct", ascending=False)
        .groupby(["verb", "verb_compound", "morph_case"], dropna=False)
        .agg({
            "tag_block": lambda x: "<br><br>".join([b for b in x if b])
        })
        .reset_index()
        .rename(columns={"tag_block": "examples_hover"})
    )

    # -----------------------------
    # 4. Merge into base_df
    # -----------------------------
    merged_df = base_df.merge(
        hover_df,
        on=["verb", "verb_compound", "morph_case"],
        how="left"
    )

    merged_df["examples_hover"] = merged_df["examples_hover"].fillna("")

    # -----------------------------
    # 5. Build final hover
    # -----------------------------
    if deptype == 'obl':
        merged_df["verb_full"] = (
            merged_df["verb"] + " " + merged_df["verb_compound"]
        ).str.strip()

        merged_df["hovername"] = (
            merged_df["verb_full"] + " (" + merged_df["morph_case"] + ")"

            # --- original examples ---
            #+ "<br><br><b>Examples:</b>"
            #+ "<br><b>tag:</b> " + merged_df["tag_example"]
            #+ "<br><b>other:</b> " + merged_df["other_example"]
            #+ "<br><b>not annotated:</b> " + merged_df["not_annotated_example"]

            # --- new aggregated tag blocks ---
            + merged_df["examples_hover"].apply(
                lambda x: "<br><br><b>Tag distribution:</b><br>" + x if x else ""
            )
        )

    return merged_df


def siksaki_alumised_punktid(df, y_col):
    min_indices = argrelextrema(df[y_col].values, np.less)[0] #finds indices where the y-value is less than its neighbor
    lower_points = df.iloc[min_indices]

    return lower_points


def center_line1(df, x_col="log2_x", y_col="log2_y_pos80"):
    """Zig-zag line midpoints"""
    x = df[x_col].values
    y = df[y_col].values

    # clean
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]

    # find turning points (both peaks and troughs)
    peaks = argrelextrema(y, np.greater, order=2)[0]
    troughs = argrelextrema(y, np.less, order=2)[0]

    extrema = np.sort(np.concatenate([peaks, troughs]))

    # include endpoints
    extrema = np.r_[0, extrema, len(y) - 1]

    mid_x = []
    mid_y = []

    # midpoint between consecutive extrema (THIS is the key idea)
    for i in range(len(extrema) - 1):
        i1, i2 = extrema[i], extrema[i+1]

        mid_x.append((x[i1] + x[i2]) / 2)
        mid_y.append((y[i1] + y[i2]) / 2)

    return np.array(mid_x), np.array(mid_y)


def center_line(df, x_col="log2_x", y_col="log2_y_pos80", smooth_factor=0.2):
    """Smooth line over zigzag line (result is not very accurate but is for visuals)"""
    x = df[x_col].values
    y = df[y_col].values

    # clean
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]

    # sort by x (important for spline)
    order = np.argsort(x)
    x, y = x[order], y[order]

    # find extrema
    peaks = argrelextrema(y, np.greater, order=2)[0]
    troughs = argrelextrema(y, np.less, order=2)[0]
    extrema = np.sort(np.concatenate([peaks, troughs]))

    # include endpoints
    extrema = np.r_[0, extrema, len(y) - 1]

    # compute midpoints
    mid_x = (x[extrema[:-1]] + x[extrema[1:]]) / 2
    mid_y = (y[extrema[:-1]] + y[extrema[1:]]) / 2

    # spline smoothing
    if smooth_factor is None:
        smooth_factor = len(mid_x)  # good default, increase for smoother

    spline = UnivariateSpline(mid_x, mid_y, s=smooth_factor)

    # generate smooth curve
    x_smooth = np.linspace(mid_x.min(), mid_x.max(), 500)
    y_smooth = spline(x_smooth)

    return x_smooth, y_smooth#, mid_x, mid_y


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
    x_vals, y_vals = center_line(lines_df, y_col="log2_y_pos80")
    fig.add_trace(go.Scatter(
        x=x_vals , #list(base_df[x_axis]),
        y=y_vals ,
        mode='lines',
        line=dict(color='orange', width=3),
        name='80'
    ))
    
    x_vals, y_vals = center_line(lines_df, y_col="log2_y_pos90")
    fig.add_trace(go.Scatter(
        x=x_vals , #list(base_df[x_axis]),
        y=y_vals ,
        mode='lines',
        line=dict(color='lightgreen', width=3),
        name='90'
    ))
    
    x_vals, y_vals = center_line(lines_df, y_col="log2_y_pos70")
    fig.add_trace(go.Scatter(
        x=x_vals , #list(base_df[x_axis]),
        y=y_vals ,
        mode='lines',
        line=dict(color='purple', width=3),
        name='70'
    ))
    
    x_vals, y_vals = center_line(lines_df, y_col="log2_y_pos30")
    fig.add_trace(go.Scatter(
        x=x_vals , #list(base_df[x_axis]),
        y=y_vals ,
        mode='lines',
        line=dict(color='deeppink', width=3),
        name='30'
    ))
    
    x_vals, y_vals = center_line(lines_df, y_col="log2_y_pos20")
    fig.add_trace(go.Scatter(
        x=x_vals , #list(base_df[x_axis]),
        y=y_vals ,
        mode='lines',
        line=dict(color='blue', width=3),
        name='20'
    ))
    
    x_vals, y_vals = center_line(lines_df, y_col="log2_y_pos10")
    fig.add_trace(go.Scatter(
        x=x_vals , #list(base_df[x_axis]),
        y=y_vals ,
        mode='lines',
        line=dict(color='yellow', width=3),
        name='10'
    ))
    
    """
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
    """

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


# CREATE AND MODIFY DATAFRAMES BEFORE PLOTTING

def highlight_example(example):
    sentence = example["sentence"]
    form = example["form"]
    phrase = example.get("phrase")
    row_loc = example.get("row_loc")
    verb_form = example.get("verb_form")
    verb_comp = str(example["verb_compound"])

    count = sentence.count(form)
    words = sentence.split()

    if count > 1:
        # try to find the right word to color
        # split while preserving punctuation spacing better
        if 1 <= row_loc <= len(words):
            idx = row_loc - 1
            # compare cleaned token with cleaned form
            token_clean = re.sub(r"[^\w-]", "", words[idx]).lower()
            form_clean = re.sub(r"[^\w-]", "", form).lower()

            if token_clean == form_clean:
                original_word = words[idx]
                words[idx] = (
                    f'<span style="color:yellow;font-weight:bold;">'
                    f'{original_word}'
                    f'</span>'
                )
        highlighted = " ".join(words)

    elif count == 1:
        """# highlight ONLY the indexed token
        if 1 <= row_loc <= len(words) :
            idx = row_loc - 1
            words[idx] = (
                f'<span style="color:yellow;font-weight:bold;">'
                f'{form}'
                f'</span>'
            )"""
        highlighted = " ".join(words)
        highlighted = highlighted.replace(
            form,
            f'<span style="color:yellow;font-weight:bold;">{form}</span>',
            1
        )

    # underline verb_compound
    if verb_comp:
        verb_comp = verb_comp.strip()
        highlighted = highlighted.replace(
            verb_comp,
            f'<span style="text-decoration: underline; color: lightgreen;">{verb_comp}</span>',
            1
        )

    # underline verb
    if verb_form:
        highlighted = highlighted.replace(
            verb_form,
            f'<span style="text-decoration: underline; color: lightgreen;">{verb_form}</span>',
            1
        )

    example["highlighted"] = highlighted

    return example

    
def process_examples(examples_json):
    if pd.isna(examples_json):
        return None
    examples = json.loads(examples_json)
    examples = [highlight_example(ex) for ex in examples]
    return json.dumps(examples, ensure_ascii=False)    
    

def example_process(df2):
    # Post-process highlighting in Python
    df2["examples"] = df2["examples"].apply(process_examples)
    df2["tag"] = df2["tag"].replace("", "-")
    
    return df2


def prepare_data(database, examples_df, obl_table, tag_col, table_name, user_tags, other_tags, deptype = 'obl'):
    """prepare data for hoverplotting"""
    dataframe = read(database, table_name)
    dataframe = tag(database, obl_table, tag_col, dataframe, 'tag_example', user_tags, deptype)
    dataframe = tag(database, obl_table, tag_col, dataframe, 'other_example', other_tags, deptype)
    dataframe = not_annotated(database, obl_table, tag_col, dataframe, deptype)
    dataframe = hovername(dataframe, examples_df, deptype)
    #dataframe = hovername1(dataframe, deptype)
    return dataframe


# MAIN FUNCTIONS

def run(conf_file):

    DATABASE = conf_file["configuration"]["database"]
    OBL_TABLE = conf_file["configuration"]["obl_table"] # spatial_obl table 
    TAG_COL = conf_file["configuration"]["tags_column"] # column with tags: 'tags' etc
    CONFIDENCE_VALUES = conf_file["configuration"]["confidence_values_table"] # table with n-line data 
    TARGET_TAG = conf_file["configuration"]["target_tag"].split(",") # what tags the user is interested in (A, T, ELT etc)
    OTHER_TAGS = conf_file["configuration"]["other_tags"].split(",") # all other tags in the data
    OTHER_TAGS = [elem.strip() for elem in OTHER_TAGS]
    RES_DIR = conf_file["configuration"]["dir_scatter_results"] # where to save scatterplots

    # table with n80, n90, n10 etc line data 
    lines_df = read(DATABASE, CONFIDENCE_VALUES)

    examples_df = read(DATABASE, "spatial_obl_plotting_examples")

    # for highlighting etc, can be commented out and code should still work 
    examples_df = example_process(examples_df)

    df_log_loc = prepare_data(DATABASE,examples_df,  OBL_TABLE, TAG_COL, f'verb_case_log_{TARGET_TAG[0]}', 
                              TARGET_TAG, 
                              OTHER_TAGS)
    #print(len(df_log_loc))

    # ## Create hoverplots (all the hoverplots save the result in html)

    # This section creates hoverplots from the data compiled in the above sections.
    # The user has to define: 
    # * dataframe the info is from
    # * column used as x_axis
    # * x-axis label
    # * y_axis label
    # * filename for the saved hoverplot, needs to be html

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


