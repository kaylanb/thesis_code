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

def analyze_results(args=None):
    parser = ArgumentParser(description="test")
    parser.add_argument("--savefn",action="store",default='results.pickle',required=False)
    args = parser.parse_args(args=args)

    fobj=open(args.savefn,'r')
    f,b,t=pickle.load(fobj)
    fobj.close()

    print t.sum()/3600

def main(args=None,program='analyze'):
    if program == 'analyze':
        analyze_results()
    elif program == 'gather':
        gather_results()
    else: 
        read_150k_cats()

if __name__ == '__main__':
    main()

