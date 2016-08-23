#!/bin/bash
fn="$1"
grep -e "Resources for" ${fn} -A 2|grep -e "Wall:" -e "Resources" > ${fn}_mem.txt
grep -e "Resources for stage" -e "Total serial Wall" -e "Total parallel Wall" -e "Grand total Wall" -e "Grand total CPU utilization" ${fn} > ${fn}_time.txt
echo 'done!'
