#!/usr/bin/env python
# coding: utf-8

# # Calculates confidence points to draw n80, n20 and n50 lines
# Theoretically doesn't need to be run for every tag as long as the max unique_lemma value is covered by CALCULATION_RANGE_MAX

import sqlite3
import pandas as pd
from tqdm import tqdm
import numpy as np
from scipy.stats import binom_test
from scipy.stats import binom
import argparse
import json
import configparser

np.seterr(invalid='ignore')

# FUNCTIONS

def load_config(path):
    """Loads config.
    """
    config = configparser.ConfigParser()
    status = config.read(path) 
    assert status == [path]
    return config


def get_min_success(n=100, p=0.8, kv=0.05):

    #n = 100       # number of trials
    #p = 0.8       # null hypothesis success rate

    # Find smallest k such that P(X ≥ k) < 0.05
    for k in range(n + 1):
        if binom.sf(k - 1, n, p) <= kv: #kv=0.05 95% puhul, 70% puhul peaks olema 0.05 asemel 0.95
            #print(f"Minimum k: {k}")
            #break
            return k
    
    #return np.nan
    return n


def get_max_failure(n=100, p=0.8, kv=0.05):
    # Find the largest k such that P(X ≤ k) < kv
    for k in range(n + 1):
        if binom.cdf(k, n, p) >= kv:
            return k
    #return np.nan
    return n



def run(conf_file):
    
    DATABASE = conf_file["configuration"]["database"]
    CALCULATION_RANGE_MAX = int(conf_file["configuration"]["confidence_range"])
    CONFIDENCE_DB_TABLE = conf_file["configuration"]["confidence_values_table"]

    # ## Calculate values for every confidence line

    # 80 joon
    min_values = []
    x_ann = [x for x in range(1,CALCULATION_RANGE_MAX)] 
    for i in tqdm(range(len(x_ann))):
        min_success = get_min_success(x_ann[i], p=0.8)
        min_values.append(min_success)

    lines_df = pd.DataFrame(columns = ["x", "y_pos80"])
    lines_df["x"] = x_ann
    lines_df["y_pos80"] = min_values
    lines_df["log2_x"] = np.log2(lines_df["x"])
    lines_df["y_neg80"] = lines_df["x"]-lines_df["y_pos80"]
    lines_df["log2_y_pos80"] = np.log2(lines_df["y_pos80"]/lines_df["y_neg80"])

    # 90 joon
    min_values = []
    x_ann = [x for x in range(1,CALCULATION_RANGE_MAX)] 
    for i in tqdm(range(len(x_ann))):
        min_success = get_min_success(n=x_ann[i], p=0.9 )
        min_values.append(min_success)

    lines_df["y_pos90"] = min_values
    lines_df["y_neg90"] = lines_df["x"]-lines_df["y_pos90"]
    lines_df["log2_y_pos90"] = np.log2(lines_df["y_pos90"]/lines_df["y_neg90"])

    # 70 joon
    max_values = []
    x_ann = [x for x in range(1,CALCULATION_RANGE_MAX)] 
    for i in tqdm(range(len(x_ann))):
        min_success = get_max_failure(n=x_ann[i], p=0.7, kv=0.05 )
        max_values.append(min_success)

    lines_df["y_pos70"] = max_values
    lines_df["y_neg70"] = lines_df["x"]-lines_df["y_pos70"]
    lines_df["log2_y_pos70"] = np.log2(lines_df["y_pos70"]/lines_df["y_neg70"])

    # 30 joon
    min_values = []
    x_ann = [x for x in range(1,CALCULATION_RANGE_MAX)] 
    for i in tqdm(range(len(x_ann))):
        min_success = get_min_success(n=x_ann[i], p=0.3, kv=0.05 )
        min_values.append(min_success)

    lines_df["y_pos30"] = min_values
    lines_df["y_neg30"] = lines_df["x"]-lines_df["y_pos30"]
    lines_df["log2_y_pos30"] = np.log2(lines_df["y_pos30"]/lines_df["y_neg30"])

    # 20 joon
    max_values = []
    x_ann = [x for x in range(1,CALCULATION_RANGE_MAX)] 
    for i in tqdm(range(len(x_ann))):
        min_success = get_max_failure(n=x_ann[i], p=0.2, kv=0.05 )
        max_values.append(min_success)

    lines_df["y_pos20"] = max_values
    lines_df["y_neg20"] = lines_df["x"]-lines_df["y_pos20"]
    lines_df["log2_y_pos20"] = np.log2(lines_df["y_pos20"]/lines_df["y_neg20"])

    # 10 joon
    max_values = []
    x_ann = [x for x in range(1,CALCULATION_RANGE_MAX)] 
    for i in tqdm(range(len(x_ann))):
        min_success = get_max_failure(n=x_ann[i], p=0.1, kv=0.05 )
        max_values.append(min_success)

    lines_df["y_pos10"] = max_values
    lines_df["y_neg10"] = lines_df["x"]-lines_df["y_pos10"]
    lines_df["log2_y_pos10"] = np.log2(lines_df["y_pos10"]/lines_df["y_neg10"])


    lines_df["log2_y_pos80_p1"] = np.log2((lines_df["y_pos80"]+1)/(lines_df["y_neg80"]-1))
    lines_df["log2_y_pos80_m1"] = np.log2((lines_df["y_pos80"]-1)/(lines_df["y_neg80"]+1))

    lines_df["log2_y_pos90_p1"] = np.log2((lines_df["y_pos90"]+1)/(lines_df["y_neg90"]-1))
    lines_df["log2_y_pos90_m1"] = np.log2((lines_df["y_pos90"]-1)/(lines_df["y_neg90"]+1))

    lines_df["log2_y_pos70_p1"] = np.log2((lines_df["y_pos70"]+1)/(lines_df["y_neg70"]-1))
    lines_df["log2_y_pos70_m1"] = np.log2((lines_df["y_pos70"]-1)/(lines_df["y_neg70"]+1))

    lines_df["log2_y_pos20_p1"] = np.log2((lines_df["y_pos20"]+1)/(lines_df["y_neg20"]-1))
    lines_df["log2_y_pos20_m1"] = np.log2((lines_df["y_pos20"]-1)/(lines_df["y_neg20"]+1))

    lines_df["log2_y_pos10_p1"] = np.log2((lines_df["y_pos10"]+1)/(lines_df["y_neg10"]-1))
    lines_df["log2_y_pos10_m1"] = np.log2((lines_df["y_pos10"]-1)/(lines_df["y_neg10"]+1))

    lines_df["log2_y_pos30_p1"] = np.log2((lines_df["y_pos30"]+1)/(lines_df["y_neg30"]-1))
    lines_df["log2_y_pos30_m1"] = np.log2((lines_df["y_pos30"]-1)/(lines_df["y_neg30"]+1))


    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    lines_df.to_sql(CONFIDENCE_DB_TABLE, conn, if_exists="replace", index=False)

    conn.close()

    print("Done!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", required=True, help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.conf)
    run(config)


if __name__ == "__main__":
    main()






