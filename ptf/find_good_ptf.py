'''reads headers of all PTF*scie*.fits images and stores magzp,imagezp,seeing in numpy arrays, for each band'''
import numpy as np

def radec_to_float(ra,dec):
    '''ra = "10:30:00.00'" in hms
    dec = "22:30:23" in deg'''
    ra= np.array(ra.split(':')).astype(float)
    dec= np.array(dec.split(':')).astype(float)
    return 15*(ra[0]+ra[1]/60.+ra[2]/3600.), dec[0]+dec[1]/60.+dec[2]/3600. 

class Band(object):
    def __init__(self):
        self.zp_img,self.zp_am1,self.see,self.expt= [],[],[],[]
    def nump(self):
        self.zp_img,self.zp_am1,self.see,self.expt= np.array(self.zp_img),np.array(self.zp_am1),np.array(self.see),np.array(self.expt)
    def zp_expt(self):
        self.zp_img_expt= self.zp_img+ 2.5*np.log10(self.expt)
        self.zp_am1_expt= self.zp_am1+ 2.5*np.log10(self.expt)

if __name__ == 'main':
	import os
	from argparse import ArgumentParser
	import glob
	from astropy.io import fits
	import sys
	from pickle import dump

	parser = ArgumentParser(description="test")
	parser.add_argument("-search_str",action="store",help='root dir + search string for processed mosaic data')
	args = parser.parse_args()

	fns= glob.glob(args.search_str)
	if len(fns) == 0: print 'WARNING, 0 files found'
	r,g= Band(),Band()
	for cnt,fn in enumerate(fns[:5]):
		print 'reading image %d/%d, %s' % (cnt,len(fns),fn)
		data=fits.open(fn)
		hdr=data[0].header
		try:
			a= float(hdr['IMAGEZPT']) 
			b= float(hdr['MAGZPT']) 
			c= float(hdr['FWHMSEX']) 
			d= float(hdr['EXPTIME']) 
		except TypeError:
			print 'bad image found: %s' % fn
			print '---> zp_img=',hdr['IMAGEZPT'],'zp_am1=',hdr['MAGZPT'],'see=',hdr['FWHMSEX'],hdr['EXPTIME']
			continue
		if hdr['FILTER'].strip() == 'R':
			r.zp_img.append( a )
			r.zp_am1.append( b )
			r.see.append( c )
			r.expt.append( d )
		elif hdr['FILTER'].strip() == 'g':
			g.zp_img.append( a )
			g.zp_am1.append( b )
			g.see.append( c )
			g.expt.append( d )
		else:
			print "hdr['FILTER'].strip()= ",hdr['FILTER'].strip() 
			raise ValueError
	print "%d/%d images are good" % (len(r.see)+len(g.see),len(fns))
	r.nump()
	g.nump()
	r.zp_expt()
	g.zp_expt()
	print "saving pickle file"
	fout=open('ptf_photometric.pickle','w')
	dump((r,g),fout)
	fout.close()
	print "done"
