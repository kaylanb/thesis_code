nohup nice tar -cvf dr3.tar /global/cscratch1/sd/desiproc/dr3/{*.gz,calib,images} > dr3.out &
nohup nice tar -cvf dust.tar /scratch1/scratchdirs/desiproc/dust > dust.out &
nohup nice tar -cvf unwise_sv.tar /scratch1/scratchdirs/ameisner/unwise-coadds/fulldepth_sv > unwise_sv.out &
nohup nice tar -cvf unwise_coadds.tar /scratch1/scratchdirs/desiproc/unwise-coadds > unwise_coadds.out &
nohup nice tar -cvf unwise_lc.tar /scratch1/scratchdirs/ameisner/unwise-coadds/time_resolved_dr3 > unwise_lc.out &
nohup nice tar -cvhf dr3-mzls.tar edison:/scratch1/scratchdirs/dstn/dr3-mzls/{*.gz} > dr3-mzls.out &
