#!/bin/bash
SLEEP_INTERVAL="${SLEEP_INTERVAL:-0.01}"
CONTROL_FILE="${CONTROL_FILE:-/tmp/control_file.txt}"

echo "Checking for $CONTROL_FILE at interval $SLEEP_INTERVAL"
echo "STAMP LAUNCH BEGIN $(date --rfc-3339=ns)"
t1=$(date +%s.%N)
until [ -f ${CONTROL_FILE} ]
do
     sleep ${SLEEP_INTERVAL}
done
t2=$(date +%s.%N)
tdiff=$(echo "$t2 - $t1" | bc -l)
echo "TIME LAUNCH $tdiff"
echo "STAMP LAUNCH END $(date --rfc-3339=ns)"

env LD_PRELOAD=/global/common/cori/software/darshan/3.0.1/lib/libdarshan.so "$@"
