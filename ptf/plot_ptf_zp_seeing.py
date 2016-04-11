import numpy as np
from pickle import load
from argparse import ArgumentParser

from thesis_code import plots 
from thesis_code.ptf.find_good_ptf import Band

parser = ArgumentParser(description="test")
parser.add_argument("-photo_pickle",default="ptf/ptf_photometric_cosmos.pickle",action="store",help='pickle file containing zp and seeing info for a set of PTF images')
args = parser.parse_args()

fin=open(args.photo_pickle,'r')
r,g= load(fin)
#zp_img,zp_am1,see= load(fin)
fin.close()

g.nump()
r.nump()

assert(len(g.zp_img)+len(r.zp_img) == 817) #total for cosmos.pickle
print '%d are g, %d are R' % (len(g.zp_img),len(r.zp_img))
h=np.array([g.zp_img,g.zp_am1,g.see,g.zp_img-g.zp_am1]) #shape(3,N)
plots.multi_hist(2,2,h,xlabs=['img_zp','am1_zp','seeing','img_zp - am1_zp'],fname='g')
h=np.array([r.zp_img,r.zp_am1,r.see,r.zp_img-r.zp_am1]) #shape(3,N)
plots.multi_hist(2,2,h,xlabs=['img_zp','am1_zp','seeing','img_zp - am1_zp'],fname='R')
