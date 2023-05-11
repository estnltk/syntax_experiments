## How to run

$ sbatch my_job.sh 

Submitted batch job 38626018

$ ls
first_job.sh  hello_word.py  slurm-38626018.out

$ less slurm-38626018.out

Kill job

$  scancel 38626018

User jobs
$ squeue -j | grep zummy