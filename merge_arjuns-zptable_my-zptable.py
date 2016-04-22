from astrometry.util.fits import fits_table,merge_tables
import numpy as np
from argparse import ArgumentParser
import os

parser = ArgumentParser(description="test")
parser.add_argument("-arjuns",action="store",help='from decstat,mostat,bokstat',required=True)
parser.add_argument("-mine",action="store",help='from my header parsing script',required=True)
parser.add_argument("-camera",choices=['mosaic','bok','decam'],action="store",help='camera zps are for',required=True)
args = parser.parse_args()

a=fits_table(args.arjuns)
m=fits_table(args.mine)
comb=fits_table(args.mine) #copy of mine
#fill zeros in my table for fields will fill in from arjun's table
cols= ['ccdzpt','ccdzpta','ccdzptb','ccdphoff','ccdphrms','ccdskyrms','ccdraoff','ccddecoff','ccdtransp','ccdnstar','ccdnmatch','ccdnmatcha','ccdnmatchb','ccdmdncol'] #fwhm,arawgain
if args.camera == 'bok':
    cols+= ['arawgain','avsky','mjd_obs','expnum']
    for rm_col in ['ccdphoff','ccdskyrms','ccdtransp']: cols.pop( cols.index(rm_col) ) #ians bok ccds.fits does not have these
for col in cols: comb.set(col, np.zeros(m.get('ra').shape).astype(a.get(col).dtype) ) #junk for now, but with correct dtype
#for each filename, get index of matching ccd number, fill in new info at that index
for fn in m.get('image_filename'):
    fn= os.path.basename(fn)
    for ccd in range(1,5):
        if args.camera == 'mosaic': i_arj_fn= a.get('filename') == fn
        else: i_arj_fn= a.get('image_filename') == fn
        i_arj_ccd= a.get('ccdnum') == ccd
        i_arj= np.all((i_arj_fn,i_arj_ccd),axis=0)
        assert(np.any(i_arj))
        i_me_fn= m.get('image_filename') == args.camera+'/'+fn #arjuns fn is basname, my file name is camera/basename
        i_me_ccd= m.get('ccdnum').astype(int) == ccd
        i_me= np.all((i_me_fn,i_me_ccd),axis=0)
        assert(np.any(i_me))
        #fill in arjun's info
        for col in cols: 
            #if 'zpt' in col and m.get('camera')[i_me] == 'mosaic': #no need for this, was to correct arjun's zpts for exp time
            #    comb.get(col)[i_me]= a.get(col)[i_arj] +2.5*np.log10(m.get('exptime')[i_me])
            comb.get(col)[i_me]= a.get(col)[i_arj]
#write new table
comb.writeto('arjun-my-%s-ccds.fits' % args.camera)
print 'done'
