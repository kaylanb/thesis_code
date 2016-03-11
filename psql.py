import numpy as np

def load_ofile(fn,getcols,str_kws=[]):
	'''fn -- file name of psql db dumped txt file
	getcols -- list of column indices to get, first column is 0
	str_kws -- optional, list of column names of type string, all other col names assumed to be float'''
	fin=open(fn,'r')
	keys=fin.readline()
	fin.close()
	keys= np.array(keys.split('|'))[getcols]
	for i in range(len(keys)): keys[i]= keys[i].strip()
	dtype=dict(formats=['f4']*len(keys), names=keys)  #holds more than 4 decimals
	#change str_kws to type string
	for kw in str_kws: dtype['formats'][keys.index(kw)]= 'S4' #length 4 strings
	#only tuples to np.loadtxt
	for k in dtype.keys(): dtype[k]= tuple(dtype[k])
	#load everything
	data= np.loadtxt(fn,skiprows=2,usecols=getcols,delimiter='|',dtype=dtype)
	#return as dict
	data= dict((key,data[key]) for key in keys)
	#check matched ra,dec if exist
	if 'dp_ra' in data.keys() and 'dr2_ra' in data.keys():
		assert( (data['dp_ra'] - data['dr2_ra']).max() < 1e-3)
		assert( (data['dp_dec'] - data['dr2_dec']).max() < 1e-3)
	return data
#
#	fin=open(fn,'r')
#	keys=fin.readline()
#	fin.close()
#	keys= keys.split('|')
#	for i in range(len(keys)): keys[i]= keys[i].strip()
#	print 'keys= ',keys
#	dtype=dict(formats=['f4']*len(keys), names=keys)  #holds more than 4 decimals
#	#change str_kws to type string
#	for kw in str_kws: dtype['formats'][keys.index(kw)]= 'S4' #length 4 strings
#	#only tuples to np.loadtxt
#	for k in dtype.keys(): dtype[k]= tuple(dtype[k])
#	#load everything
#	data= np.loadtxt(fn,skiprows=2,delimiter='|',dtype=dtype)
#	#return as dict
#	data= dict((key,data[key]) for key in keys)
#	#check matched ra,dec if exist
#	if 'dp_ra' in data.keys() and 'dr2_ra' in data.keys(): 
#		assert( (data['dp_ra'] - data['dr2_ra']).max() < 1e-3)
#		assert( (data['dp_dec'] - data['dr2_dec']).max() < 1e-3)
#	return data

