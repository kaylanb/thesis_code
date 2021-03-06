#! /usr/bin/env python
'''
This is a script that does the equivalent of for all the jobs I want to run:
spec:
 _tasks:
 - _fw_name: ScriptTask
script: srun -n 1 python script.py 10

'''

import os
from argparse import ArgumentParser
from fireworks import Firework, LaunchPad, ScriptTask

def bash(cmd):
    ret= os.system('%s' % cmd)
    if ret:
        print 'command failed: %s' % cmd
        sys.exit() 

def read_lines(fn):
    fin=open(fn,'r')
    lines=fin.readlines()
    fin.close()
    return lines

parser = ArgumentParser(description="test")
parser.add_argument("--file_list",action="store",required=True)
parser.add_argument("--outdir",action="store",required=False)
parser.add_argument("--script",action="store",help='absolute path to script.py',required=False)
parser.add_argument("--cores",type=int,action="store",default='32',required=False)
parser.add_argument("--brick",action="store",default='2523p355',required=False)
parser.add_argument("--zoom",type=int,action="store",default='1600',required=False)
args = parser.parse_args()

launchpad= LaunchPad(host="mongodb01",name="tractor_fireworks",username="tractor_fireworks_admin",password="w2e23sddf21")
launchpad.reset('', require_password=False)

fns= read_lines(args.file_list)
for cnt,fn in enumerate(fns):
    cmd="python sleep_on_it.py %d" % cnt #(args.script,fn)
    firetask= ScriptTask.from_str(cmd)
    firework= Firework(firetask, name=os.path.basename(fn))
    launchpad.add_wf(firework)
print 'added %d fireworks' % (len(fns))
#os.chdir(os.rundir)
#for i in range(ntasks):
#    outdir=os.path.join(args.outdir,"b%s_zm%d_task%d" % (args.brick,args.zoom,i))
#    #os.removedirs(outdir); os.makedirs(outdir); os.chdir(outdir); bash('ln -s %s legacypipe' % args.rundir)
#    name="task-"+str(i)
#    script="python legacypipe/runbrick.py \
#                --zoom 1 %d 1 %d \
#                --force-all --no-write \
#                --pipe \
#                --threads %d \
#                --skip \
#                --skip-calibs \
#                --brick %s --outdir %s. --nsigma 6" % \
#            (args.zooom,args.zoom,args.ncores,args.brick,\
#             outdir)

