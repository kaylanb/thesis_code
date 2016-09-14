from __future__ import print_function
from mpi4py import MPI

from legacypipe.runbrick import main

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
print("hello world from process ", rank)

#from argparse import ArgumentParser
#parser = ArgumentParser(description="test")
#parser.add_argument("--threads",type=int,action="store",required=True)
#parser.add_argument("--brick",action="store",required=True)
#parser.add_argument("--outdir",action="store",required=True)
#opt = parser.parse_args()

main(args=['--zoom', '1','200','1','200',\
           '--force-all', '--no-write','--pipe','--skip','--skip-calibs',\
           '--nsigma','6',\
           '--threads','1',\
           '--brick','2523p355',\
           '--outdir', '.'])

