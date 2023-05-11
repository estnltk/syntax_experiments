#!/bin/bash
#SBATCH -J v10_collect_verb_compound_obl
#SBATCH --partition=intel
#SBATCH -t 2-0:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=8000

# your code goes below
#module load python/3.8.6
eval "$(conda shell.bash hook)"
#conda init bash
conda activate estnltk_collocations_py38
srun python ./v10_collect_verb_compound_obl.py