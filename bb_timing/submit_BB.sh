#!/bin/bash -l

#SBATCH -p debug
#SBATCH -N 64
#SBATCH -t 00:30:00
#SBATCH -J bb_multi
#SBATCH -o bb_multi.o%j
#SBATCH --mail-user=kburleigh@lbl.gov
#SBATCH --mail-type=END,FAIL
#DW persistentdw name=tractorSmall
#DW stage_out source=$DW_PERSISTENT_STRIPED_tractorSmall/bb_multi destination=/global/cscratch1/sd/kaylanb/BB/bb_multi type=directory

export outdir=$DW_PERSISTENT_STRIPED_tractorSmall/bb_multi
mkdir ${outdir}
#export cori_outdir=/global/cscratch1/sd/kaylanb/BB/myout
#rm -r ${cori_outdir}/*

ncores=32
#export savedir=$SLURM_SUBMIT_DIR/testipm_${ncores}
#mkdir ${savedir}

export LEGACY_SURVEY_DIR=$DW_PERSISTENT_STRIPED_tractorSmall/dr3
export DUST_DIR=$DW_PERSISTENT_STRIPED_tractorSmall/dr3/dust/v0_0
## also need these dirs as tarballs
## /global/cscratch1/sd/desiproc/dr3
## /global/cscratch1/sd/desiproc/unwise-coadds
## /global/cscratch1/sd/ameisner/unwise-coadds/{time_resolved_dr3,fulldepth_sv}
## Dust map
## this? /global/homes/d/dstn/tractor/wise/wise-psf-avg.fits


## Point it to a specific bashrc??
## https://github.com/legacysurvey/legacypipe/blob/master/bin/bashrc

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

##brick=2501p162
brick=2523p355

module use /project/projectdirs/m888/csdaley/Modules/${NERSC_HOST}/modulefiles
module unload darshan
module load ipm-wrap-more-io-kernel-stats/2.0.3-git_serial-io-preload

export do_multi=yes
if [ "$do_multi" == "yes" ]; then
    # Multi node test
    ncores=32
    for node in {1..64}; do
        tracdir=${outdir}/multi64/tractor/node${node}
        ipmdir="${outdir}/multi64/ipm/node${node}"
        mkdir -p $ipmdir
        export IPM_LOGDIR=$ipmdir
        srun -N 1 -n 1 -c ${ncores} --export=ALL,LD_PRELOAD=$IPM_LOAD python legacypipe/runbrick.py --zoom 1 1600 1 1600 --force-all --no-write --pipe --threads ${ncores} --skip --skip-calibs --brick $brick --outdir ${tracdir} --nsigma 6 &
    done
    wait
elif [ "$do_multi" == "no" ]; then
    tracdir=${outdir}/tractor/ncores${ncores}
    ipmdir="${outdir}/ipm/ncores${ncores}"
    rm -r ${tracdir} 
    rm -r ${ipmdir} 
    mkdir -p $ipmdir
    export IPM_LOGDIR=$ipmdir
    srun -n 1 -c ${ncores} --export=ALL,LD_PRELOAD=$IPM_LOAD python legacypipe/runbrick.py \
            --zoom 1 1600 1 1600 \
            --force-all --no-write \
            --pipe \
            --threads ${ncores} \
            --skip \
            --skip-calibs \
            --brick $brick --outdir ${tracdir} --nsigma 6
fi 
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

echo ls ${outdir}
ls ${outdir}


#mv ${cori_outdir}/* ${savedir}/
#if [ "$do_ipm" == "yes" ]; then
#    mv ./kaylanb*.xml ${savedir}/
#elif [ "$do_strace" == "yes" ]; then
#    mv ./{strace_time.out,strace.out} ${savedir}/
#fi

echo DONE
