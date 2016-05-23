import numpy as np

def build_nan_inf_mask(data,bands):
    '''np mask array negative fluxes that give NaN or inf when convert to AB magnitude after taking log
    instead of removing these indices, the mask allows comparison of telescopes (say matched decam vs. bok/mosaic)
    '''
    for b in bands:
        test= np.log10(data[b+'flux_ext'])
        data[b+'flux_ext']= np.ma.masked_array(data[b+'flux_ext'], \
                                    mask=np.any((np.isnan(test),np.isinf(test)),axis=0))
    #mask out if ALL bands if any ONE band is masked
    mask= np.any((data['gflux_ext'].mask,data['rflux_ext'].mask,data['zflux_ext'].mask),axis=0)
    for b in bands: data[b+'flux_ext'].mask= mask

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
        #convert to AB mag and select targets
        #if cut_neg_flux: self.cut_neg_fluxes()
        self.flux_w_ext()
        build_nan_inf_mask(self.data,self.bands) #mask out, don't remove neg. fluxes
        self.flux_to_mag_ab()
        self.assert_grz_same_mask()
        #indices for each class
        #self.BGS_cuts()
        self.ELG_cuts()
        self.LRG_cuts()
        self.QSO_cuts()
        if 'w1' in self.bands and 'w2' in self.bands:
            self.data['non_ptsrc']= np.any((self.data['qso'],self.data['lrg'],self.data['bgs'],self.data['elg']), axis=0)
            self.data['ptsrc']= self.data['non_ptsrc'] == False
    def assert_grz_same_mask(self):
        '''grz all share same mask, test this is true'''
        a= np.all(self.data['gmag'].mask == self.data['rmag'].mask)
        b= np.all(self.data['zmag'].mask == self.data['gmag'].mask)
        assert(a and b)
    def propogate_new_mask(self,mask):
        '''updates mask in all masked arrays
        grz all share same mask, but may want update mask for some reason to make more stringent'''
        for b in self.bands:
            self.data[b+'flux_ext'].mask= mask
            self.data[b+'mag'].mask= mask

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
            
    def BGS_cuts(self):
        self.data['i_bgs']= np.all((self.data['type'] != 'PSF ',\
                             self.data['rmag']<19.35),\
                            axis=0)

    def LRG_cuts(self):
        if 'w1' in self.bands:
            self.data['i_lrg']= np.all((self.data['rmag']<23.0,\
                               self.data['zmag']<20.56,\
                               self.data['w1mag']<19.35,\
                               self.data['rmag']-self.data['zmag']> 1.6,\
                               self.data['rmag']-self.data['w1mag']> 1.33*(self.data['rmag']-self.data['zmag']) -0.33),\
                                axis=0)
        else: pass

    def ELG_cuts(self):
        self.data['i_elg']= np.all((self.data['rmag']<23.4,\
                           self.data['rmag']-self.data['zmag']> 0.3,\
                            self.data['rmag']-self.data['zmag']< 1.5,\
                           self.data['gmag']-self.data['rmag']< 1.0*(self.data['rmag']-self.data['zmag']) -0.2,\
                            self.data['gmag']-self.data['rmag']< -1.0*(self.data['rmag']-self.data['zmag']) +1.2),\
                            axis=0)

    def QSO_cuts(self):
        if 'w1' in self.bands and 'w2' in self.bands:
            wavg= 0.75*self.data['w1mag']+ 0.25*self.data['w2mag']
            self.data['i_qso']= np.all((self.data['type']=='PSF ',\
                                self.data['rmag']<23.0,
                               self.data['gmag']-self.data['rmag']< 1.0,\
                                self.data['rmag']-self.data['zmag']> -0.3,\
                               self.data['rmag']-self.data['zmag']< 1.1,\
                                self.data['rmag']-wavg> 1.2*(self.data['gmag']-self.data['rmag']) -0.4),\
                                axis=0)
        else: pass

	
