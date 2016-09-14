from mpi4py import MPI
from astropy.io import fits
from astropy.table import vstack, Table, Column
from argparse import ArgumentParser
import numpy as np
import os
import sys
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

def main(args):
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

if __name__ == '__main__':
    parser = ArgumentParser(description="test")
    parser.add_argument("--cats",action="store",help='text file listing absolute paths to Tractor Catalogues to read CPU_SOURCE from',required=True)
    args = parser.parse_args()

    main(args)
