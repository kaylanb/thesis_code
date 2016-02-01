import numpy as np
from astropy.io import fits

def getdata(hdulist,hdu):
	'''returns tuple: data array,keys'''
	return np.asarray(hdulist[hdu].data), hdulist[hdu].columns.names
