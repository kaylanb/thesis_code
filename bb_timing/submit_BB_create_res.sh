#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 1
#SBATCH -t 00:05:00
#SBATCH -J bb
#SBATCH -o bb.o%j
#BB create_persistent name=tractorLarge capacity=7.0TB access=striped type=scratch 

scontrol show burst
echo DONE
