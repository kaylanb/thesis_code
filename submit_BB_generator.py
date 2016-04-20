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
#parser.add_argument("--not-prod-run",dest='prod_run',action="store_false",default=True,help='all stages forced and no pickles written unless this option given',required=False)
#parser.add_argument("--time-stages",dest='time_stages',action="store_true",default=False,help='stages will NOT be timed and run individually unless this option is given',required=False)
parser.add_argument("-cores",type=int,action="store",help='# of images to copy from /project to /scratch',required=True)
parser.add_argument("-wh",type=int,action="store",help='width and height in arcsec',required=True)
parser.add_argument("-nptf",type=int,choices=[2,50,100,150,200,242],action="store",help='which band',required=True)
parser.add_argument("-hours",type=int,choices=[1,2,3,4,5,6],action="store",help='how many hours run for',required=True)
parser.add_argument("-decals_dir",action="store",help='absolute path, MUST be on scratch',required=True)
parser.add_argument("-legacypipe_dir",action="store",help='absolute path, MUST be on scratch',required=True)
parser.add_argument("-ptf_images",action="store",help='absolute path, MUST be on scratch',required=True)
#parser.add_argument("-mosaic_images",action="store",help='absolute path, MUST be on scratch')
args = parser.parse_args()

#set true/false args
tf=dict(T=True,F=False)
args.prod_run= tf[args.prod_run]
args.time_stages= tf[args.time_stages]

#tractor output dir on scratch  
job_name='c%d_wh%d_nptf%d' % (args.cores,args.wh,args.nptf)
name= 'BB_prodrun-%s_timestages-%s_%s' % (str(args.prod_run),str(args.time_stages), job_name)
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
ap('#DW jobdw capacity=50GB access_mode=striped type=scratch\n')
#if time_stages, copy over pickles dir
if args.time_stages:
    ap('#DW stage_in source=%s destination=$DW_JOB_STRIPED/pickles type=directory' % os.path.join(args.legacypipe_dir,'pickles/'))
ap('#get images')
#ap('#DW stage_in source=%s destination=$DW_JOB_STRIPED/mosaic type=directory' % (args.mosaic_images))
ap('#DW stage_in source=%s destination=$DW_JOB_STRIPED/ptf type=directory' % (args.ptf_images))
ap('#get decals-dir')
ap('#DW stage_in source=%s destination=$DW_JOB_STRIPED/decals-dir type=directory' % args.decals_dir)
ap('#soft link ccds.fits')
ap('cd $DW_JOB_STRIPED/decals-dir')
ap('ln -s sub%d.fits survey-ccds.fits' % args.nptf)
ap('#soft link images')
ap('cd images')
#ap('ln -s $DW_JOB_STRIPED/mosaic mosaic')
ap('ln -s $DW_JOB_STRIPED/ptf ptf')
ap('#get tractor codebase')
ap('#DW stage_in source=%s destination=$DW_JOB_STRIPED/legacypipe type=directory' % args.legacypipe_dir)
ap('#RUN')
ap('cd $SLURM_SUBMIT_DIR')
ap('#set up file transfer from output on bb to scratch')
ap('#DW stage_out source=$DW_JOB_STRIPED/tractor destination=%s type=directory' % scr_tractor)
#sanity check printing
ap('echo directories that should be on BB')
ap('echo ptf soft links to/N images:; ls -l $DW_JOB_STRIPED/decals-dir/images/ptf; ls $DW_JOB_STRIPED/decals-dir/images/ptf |wc -l')
ap('echo ls pickle dir:; ls $DW_JOB_STRIPED/pickles')
ap('echo ccd file soft links to:; ls  -l $DW_JOB_STRIPED/decals-dir/survey-ccds.fits')
ap('echo ls decals_dir:; ls  $DW_JOB_STRIPED/decals-dir')
ap('echo ls tractor out:; ls  $DW_JOB_STRIPED/tractor')
#
ap('export OMP_NUM_THREADS=%d' % (args.cores))
ap('echo cores=%d, wh=%d, PTF images=%d' % (args.cores,args.wh,args.nptf))
#select appropriate runbrick call
cmd= 'srun -n 1 -c %d python legacypipe/runbrick.py --brick 3523p002 --no-wise --width %d --height %d --survey-dir $DW_JOB_STRIPED/decals-dir --outdir $DW_JOB_STRIPED/tractor --threads %d' % (args.cores,args.wh,args.wh,args.cores)
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

