#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 64
#SBATCH -t 00:30:00
#SBATCH -J lstr_multi
#SBATCH -o lstr_multi.o%j
#SBATCH --mail-user=kburleigh@lbl.gov
#SBATCH --mail-type=END,FAIL
#SBATCH -L SCRATCH

ncores="$1"

module use /project/projectdirs/m888/csdaley/Modules/${NERSC_HOST}/modulefiles
module unload darshan
module load ipm-wrap-more-io-kernel-stats/2.0.3-git_serial-io-preload

export LEGACY_SURVEY_DIR=/global/cscratch1/sd/kaylanb/dr3_testdir_for_bb
export DUST_DIR=${LEGACY_SURVEY_DIR}/dust/v0_0
#brick=2501p162
brick=2523p355

export do_multi=yes
if [ "$do_multi" == "yes" ]; then
    # Multi node test
    ncores=32
    for node in {1..64}; do
        outdir=${SLURM_SUBMIT_DIR}/lstr_multi/multi64/tractor/node${node}
        ipmdir="${SLURM_SUBMIT_DIR}/lstr_multi/multi64/ipms/node${node}"
        mkdir -p $ipmdir
        export IPM_LOGDIR=$ipmdir
        srun -N 1 -n 1 -c ${ncores} --export=ALL,LD_PRELOAD=$IPM_LOAD python legacypipe/runbrick.py --zoom 1 1600 1 1600 --force-all --no-write --pipe --threads ${ncores} --skip --skip-calibs --brick $brick --outdir ${outdir} --nsigma 6 &
    done
    #node=2
    #outdir=${SLURM_SUBMIT_DIR}/lstr_multi/tractor/node${node}
    #ipmdir="${SLURM_SUBMIT_DIR}/lstr_multi/ipms/node${node}"
    #mkdir -p $ipmdir
    #export IPM_LOGDIR=$ipmdir
    #srun -N 1 -n 1 -c ${ncores} --export=ALL,LD_PRELOAD=$IPM_LOAD python legacypipe/runbrick.py --zoom 1 1600 1 1600 --force-all --no-write --pipe --threads ${ncores} --skip --skip-calibs --brick $brick --outdir ${outdir} --nsigma 6 &
    wait
elif [ "$do_multi" == "no" ]; then
    outdir=${SLURM_SUBMIT_DIR}/lstr_timing/wipm/ncores${ncores}
    ipmdir="${SLURM_SUBMIT_DIR}/lstr_timing/wipm/ipms/ncores${ncores}"
    mkdir -p $ipmdir
    export IPM_LOGDIR=$ipmdir
    srun -n 1 -c ${ncores} --export=ALL,LD_PRELOAD=$IPM_LOAD python legacypipe/runbrick.py \
            --zoom 1 1600 1 1600 \
            --force-all --no-write \
            --pipe \
            --threads ${ncores} \
            --skip \
            --skip-calibs \
            --brick $brick --outdir ${outdir} --nsigma 6
fi
echo DONE
