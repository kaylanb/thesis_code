#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 2
#SBATCH -t 00:05:00
#SBATCH -J bb_multi
#SBATCH -o output.%j
#SBATCH -e error.%j
#SBATCH -d singleton
#SBATCH --mail-user=kburleigh@lbl.gov
#SBATCH --mail-type=END,FAIL
#DW persistentdw name=tractorSmall
#DW stage_out source=$DW_PERSISTENT_STRIPED_tractorSmall/bb_multi destination=/global/cscratch1/sd/kaylanb/BB/bb_multi type=directory

set -x
LAUNCH="./sync_launch.sh"
export CONTROL_FILE="$SCRATCH/control_file_${SLURM_JOBID}.txt"

export outdir=$DW_PERSISTENT_STRIPED_tractorSmall/bb_multi
mkdir ${outdir}

ncores=32

export LEGACY_SURVEY_DIR=$DW_PERSISTENT_STRIPED_tractorSmall/dr3
export DUST_DIR=$DW_PERSISTENT_STRIPED_tractorSmall/dr3/dust/v0_0

## Equally distributed across nodes
#module load dws
#echo dwstat --all
#dwstat --all

echo reservation dir=$DW_PERSISTENT_STRIPED_tractorSmall
echo outdir=${outdir}
echo LEGACY_SURVEY_DIR=${LEGACY_SURVEY_DIR}
echo DUST_DIR=${DUST_DIR}
echo ls $DW_PERSISTENT_STRIPED_tractorSmall
ls $DW_PERSISTENT_STRIPED_tractorSmall
echo ls ${outdir}
ls ${outdir}

brick=2523p355

set +x
module use /project/projectdirs/m888/csdaley/Modules/${NERSC_HOST}/modulefiles
module unload darshan
module load ipm-wrap-more-io-kernel-stats/2.0.3-git_serial-io-preload
##module load ipm-wrap-more-io-kernel-stats-verbose/2.0.3-git_serial-io-preload
set -x

EXE=python ../legacypipe/runbrick.py \
    --zoom 1 1600 1 1600 \
    --force-all --no-write \
    --pipe \
    --threads ${ncores} \
    --skip \
    --skip-calibs \
    --brick $brick --outdir ${tracdir} --nsigma 6

for process in $(seq 1 ${SLURM_JOB_NUM_NODES}); do
    echo "Launching process ${process}"
	mkdir bb_${process}
	cd bb_${process}
    srun \
	-N 1 \
	-n 1 \
	-c ${ncores} \
	-o "output.runbrick.%j.${process}" \
	-e "error.runbrick.%j.${process}" \
	$LAUNCH $EXE &
    cd ..
done
sleep 10
touch $CONTROL_FILE
echo "STAMP RUNBRICK $(date --rfc-3339=ns)"
t1=$(date +%s.%N)
wait
rm $CONTROL_FILE
t2=$(date +%s.%N)
tdiff=$(echo "$t2 - $t1" | bc -l)
echo "TIME RUNBRICK $tdiff"

# Copy the stdout, stderr and IPM XML file - CD: commented out for now but may be needed when we run on the BB
#for process in $(seq 1 ${SLURM_JOB_NUM_NODES}); do
#    cp -n -v {output*,error*,*.xml} ${SOME_FINAL_PFS_DIR}
#done

#echo RUNNING WITH strace
#module use /project/projectdirs/m888/csdaley/Modules/${NERSC_HOST}/modulefiles
#module load strace/4.12
#srun -n 1 -c ${ncores} $STRACE_LOG python legacypipe/runbrick.py \
#    --zoom 1 1600 1 1600 \
#    --force-all --no-write \
#    --pipe \
#    --threads ${ncores} \
#    --skip \
#    --skip-calibs \
#    --brick $brick --outdir ${outdir} --nsigma 6

#mv ${cori_outdir}/* ${savedir}/
#if [ "$do_ipm" == "yes" ]; then
#    mv ./kaylanb*.xml ${savedir}/
#elif [ "$do_strace" == "yes" ]; then
#    mv ./{strace_time.out,strace.out} ${savedir}/
#fi

echo DONE
