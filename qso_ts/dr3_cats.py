from __future__ import division, print_function
from thesis_code.fits import load
import numpy as np
import os

def list_them(ra1=330.,ra2=30.,dec1=-1.25,dec2=1.25,outname='dr3_cats.txt'):
    print('searching for DR3 Tractor Catalgues in region:')
    print('ra1,ra2,dec1,dec2= %.1f,%.1f,%.1f,%.1f' % (ra1,ra2,dec1,dec2))
    dr3_dir= '/global/cscratch1/sd/desiproc/dr3/'
    b=load(os.path.join(dr3_dir,'survey-bricks.fits.gz'))
    bra= np.any((b['RA'].data >= ra1,b['RA'].data <= ra2),axis=0)
    btot=np.all((bra,b['DEC'].data >= dec1,b['DEC'].data <= dec2),axis=0)
    names= b['BRICKNAME'].data[btot]

    # Write name of tractor cat to file if it exists
    fout=open(outname,'w')
    for name in names:
        cat= os.path.join(dr3_dir,'tractor',name[:3],'tractor-%s.fits' % name)
        if os.path.exists(cat): fout.write('%s\n' % cat)
    fout.close()
    print("wrote %s" % outname)


