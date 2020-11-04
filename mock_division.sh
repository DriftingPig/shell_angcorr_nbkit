#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH --account=desi
#SBATCH -o ./slurm_output/mock_division_%j.out
#SBATCH -L SCRATCH,project
#SBATCH -C haswell
#SBATCH --mail-user=kong.291@osu.edu  
#SBATCH --mail-type=ALL

#this code divide the generated mock catalog into a lot of shells

#this environment needs to have nbodykit in it
conda activate cfastpm
#source the parameter file you want
source parameters/set0.sh  

# NERSC / Cray / Cori / Cori KNL things
export KMP_AFFINITY=disabled
export MPICH_GNI_FORK_MODE=FULLCOPY
export MKL_NUM_THREADS=1
export OMP_NUM_THREADS=1
# Protect against astropy configs
export XDG_CONFIG_HOME=/dev/shm


srun -n 1 -c 64 python mock_division.py
echo Finished mock division

python redshfit_hist.py
echo Finished recoding redshift distribution

