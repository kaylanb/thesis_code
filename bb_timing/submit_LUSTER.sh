#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 2
#SBATCH -t 00:05:00
#SBATCH -J lstr_multi
#SBATCH -o output.%j
#SBATCH -e error.%j
#SBATCH -d singleton
#SBATCH --mail-user=kburleigh@lbl.gov
#SBATCH --mail-type=END,FAIL

set -x
LAUNCH="./sync_launch.sh"
export CONTROL_FILE="$SCRATCH/control_file_${SLURM_JOBID}.txt"

ncores=32

export LEGACY_SURVEY_DIR=/global/cscratch1/sd/kaylanb/dr3_testdir_for_bb
export DUST_DIR=${LEGACY_SURVEY_DIR}/dust/v0_0

## Equally distributed across nodes
#module load dws
#echo dwstat --all
#dwstat --all

brick=2523p355

set +x
module use /project/projectdirs/m888/csdaley/Modules/${NERSC_HOST}/modulefiles
module unload darshan
module load ipm-wrap-more-io-kernel-stats/2.0.3-git_serial-io-preload
##module load ipm-wrap-more-io-kernel-stats-verbose/2.0.3-git_serial-io-preload
set -x

##python ../legacypipe/runbrick.py --zoom 1 200 1 200 --force-all --no-write --pipe --threads 1  --skip --skip-calibs  --brick 2523p355 --outdir . --nsigma 6

for process in $(seq 1 ${SLURM_JOB_NUM_NODES}); do
    echo "Launching process ${process}"
    EXE=python legacypipe/runbrick.py \
            --zoom 1 1600 1 1600 \
            --force-all --no-write \
            --pipe \
            --threads ${ncores} \
            --skip \
            --skip-calibs \
            --brick $brick --outdir tractor${process} --nsigma 6
	#mkdir lstr_${process}
	#cd lstr_${process}
    srun \
	-N 1 \
	-n 1 \
	-c ${ncores} \
	-o "output.runbrick.%j.${process}" \
	-e "error.runbrick.%j.${process}" \
	$LAUNCH $EXE &
    #cd ..
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
