import numpy as np

def read_from_tractor_cat(fn,same_keys=['ra','dec','type']):
	'''returns data dict for DECaLS()
	same_keys -- keys that have identical names b/w tractor cat and data dict expected by DeCALS()'''
	from fits import tractor_cat
	a=tractor_cat(fn)
	data={}
	for k in same_keys:
		data[k]= a[k]
	data['type']= np.char.strip(data['type'])
	for band,ind in zip(['g','r','z'],[1,2,4]):
		data[band+'flux']= a['decam_flux'][:,ind]
		data[band+'flux_ivar']= a['decam_flux_ivar'][:,ind]
		data[band+'_ext']= a['decam_mw_transmission'][:,ind]
	for band,ind in zip(['w1'],[0]):
		data[band+'flux']= a['wise_flux'][:,ind]
		data[band+'flux_ivar']= a['wise_flux_ivar'][:,ind]
		data[band+'_ext']= a['wise_mw_transmission'][:,ind]
	return data

def read_from_psql_file(fn,use_cols=range(14),str_cols=['type']):
	'''return data dict for DECaLS()
	fn -- file name of psql db txt file
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

def data_extract(data,indices):
    '''data -- returned by read_from_*
    indicies -- return data but only at these indices'''
    #return {data[k][indices] for 
    cpy={}
    for k in data.keys(): 
        cpy[k]= data[k][indices]
    return cpy


class PTF(object):
	def __init__(self,data): #,cut_neg_flux=False):
		#data from psql db txt file
		self.data= data
		self.bands=['g','r']
		#convert to AB mag and select targets
		#if cut_neg_flux: self.cut_neg_fluxes()
		self.flux_w_ext()
		build_nan_inf_mask(self.data,self.bands) #mask out, don't remove neg. fluxes
		self.flux_to_mag_ab()
	
	#def cut_neg_fluxes(self):
	#	ind= np.all((self.data['gflux']>0,self.data['rflux']>0), axis=0)
	#	for key in self.data.keys(): self.data[key]= self.data[key][ind]

	def flux_w_ext(self):
		for b in ['g', 'r']:
			self.data[b+'flux_ext']= self.data[b+'flux']/self.data[b+'_ext']

	def flux_to_mag_ab(self):
		for b in ['g', 'r']:
			self.data[b+'mag']= -2.5*np.log10(self.data[b+'flux_ext'])	


class DECaLS(object):
	def __init__(self,data,w1=False,w2=False): #,cut_neg_flux=False):
		#data from psql db txt file
		self.data= data
		self.bands= ['g', 'r', 'z']
		if w1: self.bands+= ['w1']
		if w2: self.bands+= ['w2']
		#mask
		self.apply_mask() 
		#convert to AB mag and select targets
		self.flux_w_ext()
		self.flux_to_mag_ab()
		#target selection, self.lrg is True wherever LRG is
		self.BGS_cuts()
		self.ELG_cuts()
		self.LRG_cuts()
		self.QSO_cuts()
		#sanity checks
		#self.assert_same_mask()
		#self.assert_TS_not_where_masked()
	def apply_mask(self,add_mask=None):
		'''create mask or combine existing mask with add_mask, then apply it to all self.data.keys() fields'''
		if add_mask is None:
			self.mask=np.all((self.data['gflux'] <= 0,\
							self.data['rflux'] <= 0,\
							self.data['zflux'] <= 0),axis=0)
		else: 
			self.mask= np.any((mask,add_mask),axis=0)
				#test= np.log10(data[b+'flux_ext'])
				#data[b+'flux_ext']= np.ma.masked_array(data[b+'flux_ext'], \
				#							mask=np.any((np.isnan(test),np.isinf(test)),axis=0))
		for key in self.data.keys():
			print "applying mask to key= %s" % key
			self.data[key]= np.ma.masked_array(self.data[key],mask=self.mask)
	def assert_same_mask(self):
		'''self.mask should be applied to all self.data.keys() fields'''
		for key in self.data.keys():
			print 'key=',key,"np.where(self.data[key].mask)[0].size=",np.where(self.data[key].mask)[0].size,"np.where(self.mask)[0].size",np.where(self.mask)[0].size
			if key not in ['w1mag']: assert(np.all(self.data[key].mask == self.mask))
	def assert_TS_not_where_masked(self):
		assert(np.all( self.bgs[self.mask] == False )) #no galaxies should be selected where mask is true
		assert(np.all( self.lrg[self.mask] == False )) 
		assert(np.all( self.elg[self.mask] == False )) 
		assert(np.all( self.qso[self.mask] == False )) 
	def count_total(self):
		'''return total number of objects'''
		return self.data['ra'].size
	def count_not_masked(self):
		'''return total number of NOT masked objects'''
		return np.where(self.data['gmag'].mask == False)[0].size

	def flux_w_ext(self):
		for b in self.bands:
			self.data[b+'flux_ext']= self.data[b+'flux']/self.data[b+'_ext']

	def flux_to_mag_ab(self):
		for b in self.bands:
			self.data[b+'mag']= 22.5 -2.5*np.log10(self.data[b+'flux_ext'])
			self.data[b+'mag_ivar']= np.power(np.log(10.)/2.5*self.data[b+'flux'], 2)* self.data[b+'flux_ivar']
			
	#color cuts are automatically masks where input colors are already masked...
	def BGS_cuts(self):
		self.bgs= np.all((self.data['type'] != 'PSF',\
							self.data['rmag']<19.35),axis=0)
	def LRG_cuts(self):
		if 'w1' in self.bands:
			self.lrg= np.all((self.data['rmag']<23.0,\
								self.data['zmag']<20.56,\
								self.data['w1mag']<19.35,\
								self.data['rmag']-self.data['zmag']> 1.6,\
								self.data['rmag']-self.data['w1mag']> 1.33*(self.data['rmag']-self.data['zmag']) -0.33),axis=0)
		else: print "WARNING, cannot make LRG cut because no W1"

	def ELG_cuts(self):
		self.elg= np.all((self.data['rmag']<23.4,\
					self.data['rmag']-self.data['zmag']> 0.3,\
					self.data['rmag']-self.data['zmag']< 1.5,\
					self.data['gmag']-self.data['rmag']< 1.0*(self.data['rmag']-self.data['zmag']) -0.2,\
					self.data['gmag']-self.data['rmag']< -1.0*(self.data['rmag']-self.data['zmag']) +1.2),axis=0)

	def QSO_cuts(self):
		if 'w1' in self.bands and 'w2' in self.bands:
			wavg= 0.75*self.data['w1mag']+ 0.25*self.data['w2mag']
			self.qso= np.all((self.data['type']=='PSF ',\
							self.data['rmag']<23.0,\
							self.data['gmag']-self.data['rmag']< 1.0,\
							self.data['rmag']-self.data['zmag']> -0.3,\
							self.data['rmag']-self.data['zmag']< 1.1,\
							self.data['rmag']-wavg> 1.2*(self.data['gmag']-self.data['rmag']) -0.4),axis=0)
		else: print "WARNING, cannot make QSO cut because no W1,W2"

	
