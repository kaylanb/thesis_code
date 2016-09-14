#!/bin/bash -l

#SBATCH -p regular
#SBATCH -N 1
#SBATCH -t 01:00:00
#SBATCH -J bb
#SBATCH -o bb.o%j
#DW persistentdw name=tractorLarge
#DW stage_in source=/global/cscratch1/sd/nugent/decam.tar destination=$DW_PERSISTENT_STRIPED_tractorLarge/dr3/decam.tar type=filename
#DW stage_in source=/global/cscratch1/sd/nugent/fits.tar destination=$DW_PERSISTENT_STRIPED_tractorLarge/dr3/fits.tar type=filename

ls $DW_PERSISTENT_STRIPED_tractorLarge/dr3
du -shc $DW_PERSISTENT_STRIPED_tractorLarge/dr3/decam.tar
du -shc $DW_PERSISTENT_STRIPED_tractorLarge/dr3/fits.tar

echo DONE
