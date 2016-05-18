import numpy as np

def build_nan_inf_mask(data,bands):
	'''np mask array negative fluxes that give NaN or inf when convert to AB magnitude after taking log
	instead of removing these indices, the mask allows comparison of telescopes (say matched decam vs. bok/mosaic)
	'''
	for b in bands:
		test= np.log10(data[b+'flux_ext'])
		data[b+'flux_ext']= np.ma.masked_array(data[b+'flux_ext'], \
									mask=np.any((np.isnan(test),np.isinf(test)),axis=0))


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
		#indices for each class
		#self.BGS_cuts()
		self.ELG_cuts()
		self.LRG_cuts()
		self.QSO_cuts()
		if 'w1' in self.bands and 'w2' in self.bands:
			self.data['non_ptsrc']= np.any((self.data['qso'],self.data['lrg'],self.data['bgs'],self.data['elg']), axis=0)
			self.data['ptsrc']= self.data['non_ptsrc'] == False

	#def cut_neg_fluxes(self):
	#	ind= np.all((self.data['gflux']>0,self.data['rflux']>0, self.data['zflux']>0), axis=0)
	#	if self.wise: ind= np.all((ind,self.data['w1flux']>0,self.data['w2flux']>0), axis=0)
	#	for key in self.data.keys(): self.data[key]= self.data[key][ind]

	def flux_w_ext(self):
		for b in self.bands:
			self.data[b+'flux_ext']= self.data[b+'flux']/self.data[b+'_ext']
	
	def flux_to_mag_ab(self):
		for b in self.bands:
			self.data[b+'mag']= 22.5 -2.5*np.log10(self.data[b+'flux_ext'])
			
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

	
