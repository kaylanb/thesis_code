import numpy as np

def load_ofile(fn,use_cols=range(14),str_cols=['type']):
	'''fn -- file name of psql db txt file
	use_cols -- list of column indices to get, first column is 0
	str_cols -- list of column names that should have type str not float'''
	#get column names
	fin=open(fn,'r')
	cols=fin.readline()
	fin.close()
	cols= np.char.strip( np.array(cols.split('|'))[use_cols] )
	#get data
	arr=np.loadtxt(fn,dtype='str',comments='(',delimiter='|',skiprows=2,usecols=use_cols)
	data={}
	for i,col in enumerate(cols):
		if col in str_cols: data[col]= np.char.strip( arr[:,i].astype(str) )
		else: data[col]= arr[:,i].astype(float)
	return data

