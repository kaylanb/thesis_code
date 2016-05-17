from astrometry.util.fits import fits_table,merge_tables
import numpy as np
from argparse import ArgumentParser
import os

parser = ArgumentParser(description="test")
parser.add_argument("-ians",action="store",help='Ians bok ccd table',required=True)
parser.add_argument("-mine",action="store",help='table from bok-ccd.py',required=True)
parser.add_argument("-pixscale",type=float,default=0.445,action="store",help='bok',required=False)
args = parser.parse_args()

ians=fits_table(args.ians)
mine=fits_table(args.mine)
comb=fits_table(args.mine) #combined table for legacypipe, initialize as copy of mine
#fill zeros in my table for fields will fill in from arjun's table
cols= ['ccdzpt','ccdzpta','ccdzptb','ccdphrms','ccdraoff','ccddecoff','ccdnstar','ccdnmatch','ccdnmatcha','ccdnmatchb','ccdmdncol']
cols+= ['seeing','arawgain','avsky','mjd_obs','expnum']
for col in cols: comb.set(col, np.zeros(m.get('ra').shape).astype(a.get(col).dtype) ) #junk for now, but with correct dtype
#for each filename, get index of matching ccd number, fill in new info at that index
for fn in m.get('image_filename'):
    fn= os.path.basename(fn)
    for ccd in range(1,5):
        i_arj_fn= a.get('image_filename') == fn
        i_arj_ccd= a.get('ccdnum') == ccd
        i_arj= np.all((i_arj_fn,i_arj_ccd),axis=0)
        assert(np.any(i_arj))
        i_me_fn= m.get('image_filename') == args.camera+'/'+fn #arjuns fn is basname, my file name is camera/basename
        i_me_ccd= m.get('ccdnum').astype(int) == ccd
        i_me= np.all((i_me_fn,i_me_ccd),axis=0)
        assert(np.any(i_me))
        #fill in arjun's info
        for col in cols: 
            comb.get(col)[i_me]= a.get(col)[i_arj]
			if 'zpt' in col: comb.get(col)[i_me]+= 2.5*np.log10(m.get('exptime')[i_me]) #correct for exptime
			#seeing --> fwhm 
			comb.get('fwhm')[i_me]= ians.get('seeing')[i_arj] / args.pixscale
#write new table
comb.writeto('bok-ccds-for-legacypipe.fits' % args.camera)
print 'done'
