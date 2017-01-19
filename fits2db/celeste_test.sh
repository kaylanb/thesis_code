#!/bin/bash

#module load postgresql
db='/usr/bin/psql -U desi_admin -d desi -h scidb2.nersc.gov'
ops="--sql=postgres --create --verbose --explode --concat"
tab_name=celeste10k
for fn in `find /global/cscratch1/sd/rthomas/kaylan/ -name "celeste-*.fits"`;do 
    echo uploading $fn
    date
    ./fits2db $ops --table=${tab_name} $fn | $db
    date
done
