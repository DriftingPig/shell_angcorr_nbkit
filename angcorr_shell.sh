#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 40
#SBATCH -t 00:30:00
#SBATCH --account=desi
#SBATCH -J angshell
#SBATCH -o ./slurm_output/SV_south_%j.out
#SBATCH -L SCRATCH,project
#SBATCH -C haswell
#SBATCH --mail-user=kong.291@osu.edu  
#SBATCH --mail-type=ALL


#for VARIABLE in {1..19}
#do
#	srun -N 1 -n 1 -c 64 python angcorr_shell.py $VARIABLE &
#done
#
#VARIABLE=20
#
#srun -N 1 -n 1 -c 64 python angcorr_shell.py $VARIABLE

#wait

# NERSC / Cray / Cori / Cori KNL things
#export KMP_AFFINITY=disabled
#export MPICH_GNI_FORK_MODE=FULLCOPY
#export MKL_NUM_THREADS=1
#export OMP_NUM_THREADS=1
# Protect against astropy configs
#export XDG_CONFIG_HOME=/dev/shm


source /global/common/software/m3035/conda-activate.sh 3.7

#bcast-pip pyyaml
#bcast-pip LSSTDESC.Coord
#bcast-pip cffi

#bcast-pip treecorr
source parameters/set2.sh 
srun -n 320 -c 8 python angcorr_shell.py
