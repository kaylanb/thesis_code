#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 1
#SBATCH -t 00:10:00
#SBATCH -J bb
#SBATCH -o bb.o%j
# JUNKBB create_persistent name=tractorSmall capacity=10GB access=striped type=scratch 
#DW persistentdw name=tractorSmall

#DW stage_in source=/global/cscratch1/sd/kaylanb/dr3_testdir_for_bb destination=$DW_PERSISTENT_STRIPED_tractorSmall/dr3 type=directory
## also need these dirs as tarballs
## /global/cscratch1/sd/desiproc/dr3
## /global/cscratch1/sd/desiproc/unwise-coadds
## /global/cscratch1/sd/ameisner/unwise-coadds/{time_resolved_dr3,fulldepth_sv}
## Dust map
## this? /global/homes/d/dstn/tractor/wise/wise-psf-avg.fits

## Equally distributed across nodes
#module load dws
#dwstat --all

find $DW_PERSISTENT_STRIPED_tractorSmall

#echo reservation dir: $DW_PERSISTENT_STRIPED_tractorSmall
#ls $DW_PERSISTENT_STRIPED_tractorSmall
echo DONE
