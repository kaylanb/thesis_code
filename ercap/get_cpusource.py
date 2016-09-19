import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.table import vstack, Table, Column
from argparse import ArgumentParser
import numpy as np
import os
import sys
import glob
import pickle
#from functools import partial
#import traceback
#from subprocess import check_output


def read_lines(fn):
    fin=open(fn,'r')
    lines=fin.readlines()
    fin.close()
    return np.sort(np.array( list(np.char.strip(lines)) ))

def rem_if_exists(name):
    if os.path.exists(name):
        if os.system(' '.join(['rm','%s' % name]) ): raise ValueError

def read_150k_cats(args=None):
    from mpi4py import MPI
    parser = ArgumentParser(description="test")
    parser.add_argument("--cats",action="store",help='text file listing absolute paths to Tractor Catalogues to read CPU_SOURCE from',required=True)
    args = parser.parse_args(args=args)
    
    comm = MPI.COMM_WORLD
    rank= comm.rank
    nodes= comm.size
    #
    fits_files= read_lines(args.cats) 
    cnt=0
    i=rank+cnt*nodes
    out_fn="rank%d.txt" % rank
    rem_if_exists(out_fn)
    while i < len(fits_files):
        # Read catalogue
        cat_fn=fits_files[i]
        tractor = Table(fits.getdata(cat_fn, 1))
        # Save info to node specified file
        fobj=open(out_fn,'a')
        fobj.write("%s %.2f\n" % (cat_fn,tractor['cpu_source'].sum()))
        fobj.close() 
        # Read next catalogue
        cnt+=1
        i=comm.rank+cnt*comm.size
    print "rank %d finished" % rank

def gather_results(args=None):
    parser = ArgumentParser(description="test")
    parser.add_argument("--search",action="store",default='rank*.txt',help='wildcard string to search for',required=False)
    parser.add_argument("--savefn",action="store",default='results.pickle',required=False)
    args = parser.parse_args(args=args)
    
    fns=glob.glob(args.search)
    if len(fns) < 1: 
        print "fns=",fns
        raise ValueErrror
    for cnt,fn in enumerate(fns):
        if cnt == 0:
            allcats,alltime= np.loadtxt(fn, dtype=str, delimiter=' ',unpack=True)
            alltime=alltime.astype(float)
        else:
            cats,time= np.loadtxt(fn, dtype=str, delimiter=' ',unpack=True)
            time=time.astype(float)
            allcats=np.concatenate((cats,allcats), axis=0)
            alltime=np.concatenate((time,alltime), axis=0)
    print 'finished gather'
    # extract brick names
    bricks=np.zeros(allcats.size).astype(str)
    for i in range(allcats.size):
        bricks[i]= allcats[i][allcats[i].find('tractor-')+8:-5]
    print 'finished post processing'
    if os.path.exists(args.savefn): 
        os.remove(args.savefn)
    fobj=open(args.savefn,'w')
    pickle.dump((allcats,bricks,alltime),fobj)
    fobj.close()    
    print 'saved results to %s' % args.savefn

def add_scatter(ax,x,y,c='b',m='o',lab='hello',s=80,drawln=False):
    ax.scatter(x,y, s=s, lw=2.,facecolors='none',edgecolors=c, marker=m,label=lab)
    if drawln: ax.plot(x,y, c=c,ls='-')

def plot_medt_grz(cpu,append='',max_exp=9):
    name='medt_grz_%s.png' % append 
    fig,ax=plt.subplots()
    add_scatter(ax,np.arange(cpu.size), cpu, c='b',m='o',lab='',drawln=True)
    plt.legend(loc='lower right',scatterpoints=1)
    #ax.set_yscale('log')
    #ax.set_ylim([1e-3,1e2])
    xlab=ax.set_ylabel('MPP hours (Median over Bricks)')
    ylab=ax.set_xlabel('nexp g+r+z (g,r,z <= %d)' % max_exp)
    plt.savefig(name, bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
    plt.close() 
 
def plot_medt_grz_errbars(cpu,cdf,max_exp=9):
    name='medt_grz_errbars.png'
    yerr=np.vstack((cpu['med']-cpu['min'],cpu['max']-cpu['med'])) 
    plt.errorbar(range(cpu['med'].size), cpu['med'],yerr=yerr,\
                 marker='o',fmt='o',c='b')
    # nexp= 3,6,9 are special
    imp=np.arange(max_exp*3)[::3][1:]
    yerr=yerr[:,imp] 
    plt.errorbar(np.arange(cpu['med'].size)[imp], cpu['med'][imp],yerr=yerr,\
                 marker='o',fmt='o',c='r')
    for i in imp:
        plt.text(i,cpu['med'][i],'%.2f' % (cpu['med'][i],),ha='left',va='top',fontsize='small')
        plt.text(i,cpu['max'][i],'%.2f' % (cpu['max'][i],),ha='left',va='top',fontsize='small')
        plt.text(i,cpu['min'][i],'%.2f' % (cpu['min'][i],),ha='left',va='top',fontsize='small')
    # cumulative %
    for i in range(max_exp*3):
        plt.text(i,cpu['max'][i],'%d%%' % (cdf[i],),ha='center',va='bottom',fontsize='small')
    #plt.legend(loc='lower right',scatterpoints=1)
    #ax.set_yscale('log')
    #ax.set_ylim([1e-3,1e2])
    xlab=plt.ylabel('MPP hours (Median over Bricks)')
    ylab=plt.xlabel('nexp g+r+z (g,r,z <= %d)' % max_exp)
    plt.savefig(name, bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
    plt.close() 
 
def analyze_results(args=None,max_exp=6):
    '''max_band_exp = 9 b/c at most have 3 exposures overlapping same time, 3 passes each'''
    parser = ArgumentParser(description="test")
    parser.add_argument("--savefn",action="store",default='results.pickle',required=False)
    args = parser.parse_args(args=args)

    fobj=open(args.savefn,'r')
    cats,bricks,times=pickle.load(fobj)
    fobj.close()

    fn='/project/projectdirs/cosmo/work/legacysurvey/dr3/survey-bricks-dr3.fits.gz'
    info=Table(fits.getdata(fn, 1))
    # sort both sets of data by brickname so they are rank aligned
    i=np.argsort(bricks)
    bricks,times=bricks[i],times[i]
    i=np.argsort(info['brickname'])
    info=info[i]
    assert( np.all(info['brickname'] == bricks) )
    # indices
    b={}
    for band in ['g','r','z']:
        b['%s' % band]=info['nexp_%s' % band] <= max_exp
    grz= info['nexp_g']+info['nexp_r']+info['nexp_z']
    for i in range(max_exp*3):
        b['grz%d' % i]= grz == i
    # data
    cdf=np.zeros(max_exp*3).astype(float)
    cpu={}
    for nam in ['min','max','med']: cpu[nam]= np.zeros(max_exp*3)-1
    for i in range(max_exp*3):
        cut= b['g']*b['r']*b['z']*b['grz%d' % i]
        cpu['med'][i]= np.median( times[cut] )
        cpu['min'][i]= np.min( times[cut] )
        cpu['max'][i]= np.max( times[cut] )
        cdf[i]= times[cut].size
    cdf=np.cumsum(cdf)
    cdf= cdf/bricks.size*100
    cdf.astype(int)
    # Convert to MPP hours, this is what nersc charges
    # MPP hours = wall[hrs] * nodes * cores * machine factor (2/2.5 edison/cori) * queue factor
    for nam in ['min','max','med']: 
        cpu[nam]= cpu[nam]/6./3600. * 1. * 6. * 2.5 * 2. #sum(cpu_source in cat)/6 is ~ wall time
    # plot
    for nam in ['min','max','med']: plot_medt_grz(cpu[nam],append=nam,max_exp=max_exp)
    plot_medt_grz_errbars(cpu,cdf,max_exp=max_exp)
    # Print MPP hours 
    print "total MPP hours dr3 'fitblobs'= %.2f" % (times.sum()/6./3600. * 1. * 6. * 2.5 * 2.,)
    for passes in [1,2,3]:
        b=np.ones(info['nexp_g'].size).astype(bool)
        for band in ['g','r','z']: b*= (info['nexp_%s' % band] >= passes)
        print "fraction of bricks with median g,r,z >= %d is %.2f" % \
                (passes,float(info['brickname'][b].size)/info['brickname'].size)

def main(args=None,program='analyze'):
    if program == 'analyze':
        analyze_results()
    elif program == 'gather':
        gather_results()
    else: 
        read_150k_cats()

if __name__ == '__main__':
    main()

