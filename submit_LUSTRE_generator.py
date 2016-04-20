import os
import sys
import argparse

def bash(cmd):
    ret= os.system('%s' % cmd)
    if ret:
        print 'command failed: %s' % cmd
        sys.exit() 

def ap(cmd):
    fin.write('%s\n' % cmd)


parser = argparse.ArgumentParser(description="test")
parser.add_argument("-prod_run",choices=['T','F'],action="store",help='true or false',required=True)
parser.add_argument("-time_stages",choices=['T','F'],action="store",help='true or false',required=True)
parser.add_argument("-cores",type=int,action="store",help='# of images to copy from /project to /scratch',required=True)
parser.add_argument("-wh",type=int,action="store",help='width and height in arcsec',required=True)
parser.add_argument("-nptf",type=int,choices=[2,50,100,150,200,242],action="store",help='which band',required=True)
parser.add_argument("-hours",type=int,choices=[1,2,3,4,5,6],action="store",help='how many hours run for',required=True)
parser.add_argument("-decals_dir",action="store",help='absolute path, MUST be on scratch',required=True)
#parser.add_argument("-mosaic_images",action="store",help='absolute path, MUST be on scratch')
args = parser.parse_args()

#set true/false args
tf=dict(T=True,F=False)
args.prod_run= tf[args.prod_run]
args.time_stages= tf[args.time_stages]

#tractor output dir on scratch  
job_name='c%d_wh%d_nptf%d' % (args.cores,args.wh,args.nptf)
name= 'LUSTRE_prodrun-%s_timestages-%s_%s' % (str(args.prod_run),str(args.time_stages), job_name)
scr_tractor= os.path.join(args.decals_dir,'tractor_runs/','tractor_%s' % name)
#bash script
fn='submit_%s.sh' % name
if os.path.exists(fn): bash('rm %s' % fn)
fin=open(fn,'w')
#fill in
ap('#!/bin/bash -l\n')
ap('#SBATCH -p regular') 
ap('#SBATCH -N 1')  
ap('#SBATCH -t 0%d:00:00' % args.hours)
job_name+='.o%j'
ap('#SBATCH -J %s' % job_name)      
ap('#SBATCH -o %s' % job_name)
ap('#SBATCH --mail-user=kburleigh@lbl.gov')
ap('#SBATCH --mail-type=END,FAIL')
#if time_stages, copy over pickles dir
ap('#soft link ccds.fits')
ap('cd %s' % args.decals_dir)
ap('rm survey-ccds.fits')
ap('ln -s sub%d.fits survey-ccds.fits' % args.nptf)
ap('cd $SLURM_SUBMIT_DIR')
ap('#RUN')
ap('export OMP_NUM_THREADS=%d' % (args.cores))
ap('echo cores=%d, wh=%d, PTF images=%d' % (args.cores,args.wh,args.nptf))
#select appropriate runbrick call
cmd= 'srun -n 1 -c %d python legacypipe/runbrick.py --brick 3523p002 --no-wise --width %d --height %d --survey-dir %s --outdir %s --threads %d' % (args.cores,args.wh,args.wh,args.decals_dir,scr_tractor,args.cores)
#timing runs get --no-write option and one of the force options
if args.prod_run:
    ap('echo START TIME:')
    ap('date')
    cmd+= ' --no-write'
    if args.time_stages:
        stages=['tims','image_coadds','srcs','fitblobs','fitblobs_finish','coadds','writecat']
        for s in stages:
            ap('echo STARTING STAGE %s' % s) 
            ap('date')
            ap(cmd+' --force-stage %s' % s)
            ap('date')
            ap('echo ENDED STAGE %s' % s)
    else: ap(cmd+'  --force-all') 
    ap('echo END TIME:')
    ap('date')
else: 
    ap(cmd+' --force-all')
ap('echo DONE')

