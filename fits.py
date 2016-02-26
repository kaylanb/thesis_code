import numpy as np
from astropy.io import fits
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
