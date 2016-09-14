#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 1
#SBATCH -t 00:05:00
#SBATCH -J bb
#SBATCH -o bb.o%j
#BB destroy_persistent name=tractorLarge  

scontrol show burst
echo DONE
