#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 13
#SBATCH -t 00:30:00
#SBATCH --account=desi
#SBATCH -o ./slurm_output/slurm_%j.out 
#SBATCH -L SCRATCH,project
#SBATCH -C haswell
#SBATCH --mail-user=kong.291@osu.edu  
#SBATCH --mail-type=ALL

#this environment  has treecorr in it but DOES NOT have nbodykit as it will breakdown mpi
#this thing might need to start from a super clean environmen, sometimes there are some weird issue of astropy-mpi related stuff, but they seem to vanish when I start from a purely clean environment. I still don't know which part is going wrong here


conda activate corr  

source parameters/set2.sh  

# NERSC / Cray / Cori / Cori KNL things   
export KMP_AFFINITY=disabled   
export MPICH_GNI_FORK_MODE=FULLCOPY   
export MKL_NUM_THREADS=1
export OMP_NUM_THREADS=1


# Protect against astropy configs 
export XDG_CONFIG_HOME=/dev/shm   


srun -n 104 -c 8 python angcorr_cal.py
