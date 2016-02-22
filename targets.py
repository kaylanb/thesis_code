import numpy as np

def cut_neg_fluxes(data):
    ind= np.all((data['gflux']>0,data['rflux']>0, data['zflux']>0,data['w1flux']>0,data['w2flux']>0), axis=0)
    for key in data.keys(): data[key]= data[key][ind]

def flux_w_ext(data):
    for b in ['g', 'r', 'z','w1','w2']:
        data[b+'flux_ext']= data[b+'flux']/data[b+'_ext']

def flux_to_mag_ab(data):
    for b in ['g', 'r', 'z','w1','w2']:
        data[b+'mag']= 22.5 -2.5*np.log10(data[b+'flux_ext'])
        
def BGS_cuts(data):
    data['bgs']= np.all((data['type'] != 'PSF ',\
                         data['rmag']<19.35),\
                        axis=0)

def LRG_cuts(data):
    data['lrg']= np.all((data['rmag']<23.0,\
                       data['zmag']<20.56,\
                       data['w1mag']<19.35,\
                       data['rmag']-data['zmag']> 1.6,\
                       data['rmag']-data['w1mag']> 1.33*(data['rmag']-data['zmag']) -0.33),\
                        axis=0)

def ELG_cuts(data):
    data['elg']= np.all((data['rmag']<23.4,\
                       data['rmag']-data['zmag']> 0.3,\
                        data['rmag']-data['zmag']< 1.5,\
                       data['gmag']-data['rmag']< 1.0*(data['rmag']-data['zmag']) -0.2,\
                        data['gmag']-data['rmag']< -1.0*(data['rmag']-data['zmag']) +1.2),\
                        axis=0)

def QSO_cuts(data):
    wavg= 0.75*data['w1mag']+ 0.25*data['w2mag']
    data['qso']= np.all((data['type']=='PSF ',\
                        data['rmag']<23.0,
                       data['gmag']-data['rmag']< 1.0,\
                        data['rmag']-data['zmag']> -0.3,\
                       data['rmag']-data['zmag']< 1.1,\
                        data['rmag']-wavg> 1.2*(data['gmag']-data['rmag']) -0.4),\
                        axis=0)

def get_targets(data):
    cut_neg_fluxes(data)
    flux_w_ext(data)
    flux_to_mag_ab(data)
    #indices for each class
    BGS_cuts(data)
    LRG_cuts(data)
    ELG_cuts(data)
    QSO_cuts(data)
    data['non_ptsrc']= np.any((data['qso'],data['lrg'],data['bgs'],data['elg']), axis=0)
    data['ptsrc']= data['non_ptsrc'] == False
