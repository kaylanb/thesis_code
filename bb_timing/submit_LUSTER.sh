#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH -J lstr
#SBATCH -o output.%j
#SBATCH -e error.%j
#SBATCH -d singleton
#SBATCH --mail-user=kburleigh@lbl.gov
#SBATCH --mail-type=END,FAIL

set -x
LAUNCH="${SLURM_SUBMIT_DIR}/sync_launch.sh"
export CONTROL_FILE="${SLURM_SUBMIT_DIR}/control_file_${SLURM_JOBID}.txt"

ncores=1
export OMP_NUM_THREADS=$ncores

export LEGACY_SURVEY_DIR=/global/cscratch1/sd/kaylanb/dr3_testdir_for_bb
export DUST_DIR=${LEGACY_SURVEY_DIR}/dust/v0_0

## Equally distributed across nodes
#module load dws
#echo dwstat --all
#dwstat --all

brick=2523p355

set +x
## IOTA
#name=iota
#module use /project/projectdirs/m888/csdaley/Modules/${NERSC_HOST}/modulefiles
#module unload darshan
# IOTA production
#module load iota-ts/c3bd61a
# regular IOTA
#module load iota-ts/0520234
## IPM
name=ipm
module use /project/projectdirs/m888/csdaley/Modules/${NERSC_HOST}/modulefiles
module unload darshan
module load ipm-wrap-more-io-kernel-stats-verbose/2.0.3-git_serial-io-preload
## STRACE
#name=strace
#module use /project/projectdirs/m888/csdaley/Modules/${NERSC_HOST}/modulefiles
#module load strace/4.12
set -x

##python ../legacypipe/runbrick.py --zoom 1 200 1 200 --force-all --no-write --pipe --threads 1  --skip --skip-calibs  --brick 2523p355 --outdir . --nsigma 6

for process in $(seq 1 ${SLURM_JOB_NUM_NODES}); do
    echo "Launching process ${process}"
    mydir=${name}${process}_${SLURM_JOB_NUM_NODES}nodes_${ncores}cores
    rm -rf ${mydir} && mkdir ${mydir}
	cd ${mydir} && ln -s ../legacypipe legacypipe
    EXE="python legacypipe/runbrick.py \
            --zoom 1 1600 1 1600 \
            --force-all --no-write \
            --pipe \
            --threads ${ncores} \
            --skip \
            --skip-calibs \
            --brick $brick --outdir . --nsigma 6"
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
