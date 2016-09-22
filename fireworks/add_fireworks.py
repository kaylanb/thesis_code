#! /usr/bin/env python

import os
from argparse import ArgumentParser
from fireworks import Firework, LaunchPad, ScriptTask

def bash(cmd):
    ret= os.system('%s' % cmd)
    if ret:
        print 'command failed: %s' % cmd
        sys.exit() 

parser = ArgumentParser(description="test")
parser.add_argument("--ncores",type=int,action="store",default='32',required=True)
parser.add_argument("--brick",action="store",default='2523p355',required=True)
parser.add_argument("--zoom",type=int,action="store",default='1600',required=True)
parser.add_argument("--outdir",action="store",required=True)
parser.add_argument("--rundir",action="store",help='absolute path to legacypie/py',required=True)
args = parser.parse_args()

launchpad= LaunchPad(host="mongodb03",name="db_name",username="db_name_admin",password="db_pass")
launchpad.reset('', require_password=False)

ntasks=10
os.chdir(os.rundir)
for i in range(ntasks):
    outdir=os.path.join(args.outdir,"b%s_zm%d_task%d" % (args.brick,args.zoom,i))
    #os.removedirs(outdir); os.makedirs(outdir); os.chdir(outdir); bash('ln -s %s legacypipe' % args.rundir)
    name="task-"+str(i)
    script="python legacypipe/runbrick.py \
                --zoom 1 %d 1 %d \
                --force-all --no-write \
                --pipe \
                --threads %d \
                --skip \
                --skip-calibs \
                --brick %s --outdir %s. --nsigma 6" % \
            (args.zooom,args.zoom,args.ncores,args.brick,\
             outdir)

    print script

    firetask= ScriptTask.from_str(script)
    firework= Firework(firetask,name=name)
    launchpad.add_wf(firework)
