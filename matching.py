import argparse
import numpy as np
from scipy.spatial import KDTree

from thesis_code import timing
from astrometry.libkd.spherematch import match_radec

def kdtree_match(ref_ra,ref_dec, ra,dec, k=1, dsmax=1./3600,verb=True):
    '''computes distance (deg separation)= sqrt{(dec1-dec2)^2+ cos[0.5*(dec1+dec2)]^2*(ra1-ra2)^2}
    return two dicts:
    1)indices of reference data where matched and unmatched
    2)indices of comparison data where matched, unmatched
    UNITS: degrees for all
    '''
    assert(len(ref_ra) == len(ref_dec))
    assert(len(ra) == len(dec))
    #index tree
    tree = KDTree(np.transpose([dec.copy(),np.cos(dec.copy()*np.pi/180)*ra.copy()])) #data has shape NxK, N points and K dimensions (K=2 for ra,dec) 
    #look in tree for each references point, return k=1 NN
    ds, i_tree = tree.query(np.transpose([ref_dec.copy(),np.cos(ref_dec.copy()*np.pi/180)*ref_ra.copy()]), k=k) #id for each data.query source that is NN of each input source
    #make sense of results
    i_ref,i_other={},{}
    i_ref['match']= np.arange(len(ref_ra))[ds<=dsmax]
    i_ref['nomatch']= np.arange(len(ref_ra))[ds>dsmax]
    i_other['match']= i_tree[ds<=dsmax]
    i_other['nomatch']= i_tree[ds>dsmax]
    assert(len(ref_ra[i_ref['match']]) == len(ra[i_other['match']]))
    if verb: print "%d/%d Refs matched, %d/%d Refs unmatched" % \
                    (i_ref['match'].size,len(ref_ra),i_ref['nomatch'].size,len(ref_ra))
    return i_ref['match'],i_other['match'],ds[ds<=dsmax]

def kdtree_match(ref_ra,ref_dec, ra,dec, k=1, dsmax=1./3600,verb=True):
    '''computes distance (deg separation)= sqrt{(dec1-dec2)^2+ cos[0.5*(dec1+dec2)]^2*(ra1-ra2)^2}
    return two dicts:
    1)indices of reference data where matched and unmatched
    2)indices of comparison data where matched, unmatched
    UNITS: degrees for all
    '''
    assert(len(ref_ra) == len(ref_dec))
    assert(len(ra) == len(dec))
    #index tree
    tree = KDTree(np.transpose([dec.copy(),np.cos(dec.copy()*np.pi/180)*ra.copy()])) #data has shape NxK, N points and K dimensions (K=2 for ra,dec) 
    #look in tree for each references point, return k=1 NN
    ds, i_tree = tree.query(np.transpose([ref_dec.copy(),np.cos(ref_dec.copy()*np.pi/180)*ref_ra.copy()]), k=k) #id for each data.query source that is NN of each input source
    #make sense of results
    i_ref,i_other={},{}
    i_ref['match']= np.arange(len(ref_ra))[ds<=dsmax]
    i_ref['nomatch']= np.arange(len(ref_ra))[ds>dsmax]
    i_other['match']= i_tree[ds<=dsmax]
    i_other['nomatch']= i_tree[ds>dsmax]
    assert(len(ref_ra[i_ref['match']]) == len(ra[i_other['match']]))
    if verb: print "%d/%d Refs matched, %d/%d Refs unmatched" % \
                    (i_ref['match'].size,len(ref_ra),i_ref['nomatch'].size,len(ref_ra))
    return i_ref['match'],i_other['match'],ds[ds<=dsmax]

def dist(r1,d1,r2,d2):
    return np.sqrt(np.power(d1-d2,2)+np.power(np.cos((d1+d2)/2*np.pi/180),2)*np.power(r1-r2,2))

def n2_match(ref_ra,ref_dec, ra,dec, dsmax=1./3600,verb=True):
    i_ref,i_other,ds=[],[],[]
    d12=np.zeros((ref_ra.shape[0],ra.shape[0]))+np.nan
    for cnt,r,d in zip(range(ra.shape[0]),ra,dec):
        d12[:,cnt]= dist(ref_ra,ref_dec,r,d)
    for cnt in range(ref_ra.shape[0]):
        imin= np.argsort(d12[cnt,:])[0]
        if d12[cnt,:][imin] <= dsmax:
            i_ref.append(cnt)
            i_other.append(imin)
            ds.append( d12[cnt,:][imin] )
    if verb: print "%d/%d Refs matched" % (len(i_ref),ref_ra.shape[0])
    return np.array(i_ref),np.array(i_other),np.array(ds)
            



#def main():
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='DECaLS simulations.')
args = parser.parse_args()

rand = np.random.RandomState(10)
n_ref,n_other=10000,5000
ra_ref = rand.uniform(150.,150.25,n_ref)
dec_ref = rand.uniform(20.,20.25,n_ref)
ra = rand.uniform(150.,150.25,n_other)
dec = rand.uniform(20.,20.25,n_other)

i_ref,i_other,ds={},{},{}
t1=timing.now()
i_ref['astrom'],i_other['astrom'],ds['astrom']= match_radec(ra_ref.copy(),dec_ref.copy(), ra.copy(),dec.copy(), 5./3600)
t2=timing.now()
i_ref['n2'],i_other['n2'],ds['n2']= n2_match(ra_ref.copy(),dec_ref.copy(), ra.copy(),dec.copy(), dsmax=5./3600)
t3=timing.now()
print 'time for astrom[sec]=',timing.diff(t1,t2)
print 'time for n2[sec]=',timing.diff(t2,t3)
#i_ref['kd'],i_other['kd'],ds['kd']= kdtree_match(ra_ref.copy(),dec_ref.copy(), ra.copy(),dec.copy(), dsmax=5./3600)
for key in ['astrom','n2']:
    i=np.argsort(i_ref[key])
    i_ref[key]= i_ref[key][i]
    i_other[key]= i_other[key][i]

#if __name__ == "__main__":
#    main()
