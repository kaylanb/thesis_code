import numpy as np
from pickle import load

from thesis_code import plots 

fin=open('ptf/ptf_photometric_cosmos.pickle','r')
zp_img,zp_am1,see= load(fin)
fin.close()

h=np.array([zp_img,zp_am1,see]) #shape(3,N)
plots.multi_hist(2,2,h,xlabs=['zp','zp am=1','seeing'])
