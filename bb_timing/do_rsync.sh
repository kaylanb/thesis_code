#!/bin/bash
#nohup nice rsync -Larv edison:/scratch1/scratchdirs/desiproc/dust ./ > dust.rsync &
#nohup nice rsync -Larv edison:/scratch1/scratchdirs/ameisner/unwise-coadds/fulldepth_sv ./ > fulldepth_sv.rsync &
#nohup nice rsync -Larv edison:/scratch1/scratchdirs/desiproc/unwise-coadds ./ > unwise-coadds.rsync &
#nohup nice rsync -Larv edison:/scratch1/scratchdirs/ameisner/unwise-coadds/time_resolved_dr3 ./ > time_resolved_dr3.rsync &
#mkdir -p dr3-mzls/images dr3-mzls/calib
#nohup nice rsync -Larv edison:/scratch1/scratchdirs/dstn/dr3-mzls/*.gz dr3-mzls/ > dr3-mzls_gz.rsync &
#nohup nice rsync -Larv edison:/scratch1/scratchdirs/dstn/dr3-mzls/images/mosaic dr3-mzls/images/ > dr3-mzls_images.rsync &
#nohup nice rsync -Larv edison:/scratch1/scratchdirs/dstn/dr3-mzls/calib/mosaic dr3-mzls/calib/ > dr3-mzls_calib.rsync &
mkdir -p dr3-decam/images dr3-decam/calib
nohup nice rsync -Larv /global/cscratch1/sd/desiproc/dr3/*.gz dr3-decam/ > dr3-decam_gz.rsync.${HOSTNAME} &
nohup nice rsync -Larv /global/cscratch1/sd/desiproc/dr3/images/* dr3-decam/images/ > dr3-decam_images.rsync.${HOSTNAME} &
nohup nice rsync -Larv /global/cscratch1/sd/desiproc/dr3/calib/* dr3-decam/calib/ > dr3-decam_calib.rsync.${HOSTNAME} &
echo 'done'
