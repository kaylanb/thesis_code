#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 1
#SBATCH -t 00:05:00
#SBATCH -J bb
#SBATCH -o bb.o%j
#SBATCH --mail-user=kburleigh@lbl.gov
#SBATCH --mail-type=END,FAIL
#DW persistentdw name=tractorSmall

echo reservation dir=$DW_PERSISTENT_STRIPED_tractorSmall
echo ls $DW_PERSISTENT_STRIPED_tractorSmall
ls $DW_PERSISTENT_STRIPED_tractorSmall

rm -r $DW_PERSISTENT_STRIPED_tractorSmall/\$outdir

echo ls $DW_PERSISTENT_STRIPED_tractorSmall
ls $DW_PERSISTENT_STRIPED_tractorSmall
echo DONE
