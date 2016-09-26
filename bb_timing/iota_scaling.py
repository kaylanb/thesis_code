'''
pulls out ipm profiling info from stdout and *.xml files
'''


import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os
from argparse import ArgumentParser

def bash_result(cmd):
    res= subprocess.check_output(cmd,\
                        stderr=subprocess.STDOUT,\
                        shell=True)
    return res.strip()

def grep_wall_cores(args):
    machine='bb'
    if args.lstr: machine='lstr'
    appendfn= 'iota_timings_%s.txt' % machine
    ncores= str(bash_result("grep 'Command-line args:' %s|cut -d ',' -f 11" % args.stdout) )
    ncores= int( ncores.replace('"','').replace("'",'') )
    wall= str( bash_result("grep 'Grand total Wall' %s| tail -n 1" % args.stdout) )
    wall= float(wall.split(' ')[-2])
    fout=open(appendfn,'a')
    fout.write("#cores wallt[s] stdout\n")
    fout.write("%d %.2f %s %s\n" % (ncores,wall, machine,args.stdout))
    fout.close()
    print "appended to %s" % appendfn



if __name__ == '__main__':
    # Tractor stdout file, parse profiling info
    parser = ArgumentParser(description="test")
    parser.add_argument("--stdout",action="store",required=True)
    parser.add_argument("--lstr",action="store_true",help='set to store as lustre, assumes burst buffer',required=False)
    args = parser.parse_args()
    # 
    grep_wall_cores(args)
    print "done"
