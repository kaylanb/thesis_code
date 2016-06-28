import numpy as np
from astropy.io import fits
from astropy.table import vstack, Table
from astrometry.util.fits import fits_table

def getdata(hdulist,hdu):
	'''returns tuple: data,keys
	data: dict of numpy arrays
	keys is correctly ordered list for data.keys()'''
	data,ordered_keys= np.asarray(hdulist[hdu].data), hdulist[hdu].columns.names
	d={}
	for key in ordered_keys:
		d[key]= data[key]
	return d,ordered_keys

def tractor_cat(fn):
	'''uses Dustin's fits_table() function to read his tractor catalog then returns it as dictionary of np arrays
	his fits_table handles booleans with weird values like 84 for "brick_primary", and converts that to True/False'''
	temp = fits_table(fn)
	data={}
	for key in temp.columns(): data[key]= temp.get(key)
	return data

def overlap_bricks(bricks_fn,ra,dec,dx):
    '''given bricks table, return all bricknames with brick centers [ra-dx,ra+dx],[dec-dx,dec+dx]'''
    b=fits_table(bricks_fn)
    ra1,ra2= ra-dx, ra+dx
    dec1,dec2= dec-dx, dec+dx
    ind= np.all((b.get('ra') >= ra1,b.get('ra') <= ra2,b.get('dec') >= dec1,b.get('dec') <= dec2),axis=0)
    print 'these bricks have centers between %.1f < ra < %.1f and %.1f < dec < %.1f' % (ra1,ra2,dec1,dec2)
    for name,ra,dec in zip(b.get('brickname')[ind],b.get('ra')[ind],b.get('dec')[ind]): print name,ra,dec

def load(name):
    '''read in fits table as astropy Table'''
    return Table(fits.getdata(name, 1))
