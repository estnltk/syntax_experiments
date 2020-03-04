#!/bin/bash

#SBATCH -p main

#SBATCH -J train_malt

#SBATCH -N 1

#SBATCH --ntasks-per-node=1

#SBATCH -t 24:00:00

#SBATCH --mem=7000

python train_models.py
