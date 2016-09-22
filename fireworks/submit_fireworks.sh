#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 1
#SBATCH -t 00:10:00
#SBATCH -J lstr
#SBATCH -o output.%j
#SBATCH -e error.%j
#SBATCH -d singleton
#SBATCH --mail-user=kburleigh@lbl.gov
#SBATCH --mail-type=END,FAIL

module unload python
module load fireworks python
#lpad init
#localhost = mongodb03
#username= db_name+admin

ncores=32
brick=2523p355
zoom=1600
export OMP_NUM_THREADS=$ncores
export LEGACY_SURVEY_DIR=/global/cscratch1/sd/kaylanb/dr3_testdir_for_bb
export DUST_DIR=${LEGACY_SURVEY_DIR}/dust/v0_0

chmod u+x add_firworks.py
./add_fireworks.py

#mydir=$SLURM_SUBMIT_DIR/cores${ncores}_zoom${zoom}
#rm -rf ${mydir} && mkdir -p ${mydir}
#cd ${mydir} && ln -s $SLURM_SUBMIT_DIR/legacypipe legacypipe
#EXE="python legacypipe/runbrick.py \
#        --zoom 1 ${zoom} 1 ${zoom} \
#        --force-all --no-write \
#        --pipe \
#        --threads ${ncores} \
#        --skip \
#        --skip-calibs \
#        --brick $brick --outdir . --nsigma 6"
LAUNCH="rlaunch -l $SLURM_SUBMIT_DIR/my_launchpad.yaml"
cd $SLURM_SUBMIT_DIR
srun \
-N 1 \
-n 1 \
-c ${ncores} \
-o "output.runbrick.%j.${process}" \
-e "error.runbrick.%j.${process}" \
$LAUNCH singleshot
#$LAUNCH rapidfire

echo DONE
