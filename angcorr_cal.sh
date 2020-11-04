#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 2
#SBATCH -t 00:30:00
#SBATCH --account=desi
#SBATCH -o ./slurm_output/slurm_%j.out 
#SBATCH -L SCRATCH,project
#SBATCH -C haswell
#SBATCH --mail-user=kong.291@osu.edu  
#SBATCH --mail-type=ALL

#this environment  has treecorr in it but DOES NOT have nbodykit as it will breakdown mpi
conda activate corr  

source parameters/set0.sh  


srun -n 32 -c 4 python angcorr_cal.py
