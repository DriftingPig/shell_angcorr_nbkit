#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 13
#SBATCH -t 00:30:00
#SBATCH --account=desi
#SBATCH -o ./slurm_output/3dcorr_%j.out 
#SBATCH -L SCRATCH,project
#SBATCH -C haswell
#SBATCH --mail-user=kong.291@osu.edu  
#SBATCH --mail-type=ALL

#this environment  has treecorr in it but DOES NOT have nbodykit as it will breakdown mpi
conda activate corr  

source parameters/set2.sh  


srun -n 104 -c 8 python 3dcorr_cal.py
