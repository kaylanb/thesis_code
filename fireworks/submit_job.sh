#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 1
#SBATCH -t 00:05:00
#SBATCH -J job
#SBATCH -L SCRATCH

#module load python/2.7-anaconda
module unload python
module load fireworks python
export OMP_NUM_THREADS=1
srun -n 1 python sleep_on_it.py 1


