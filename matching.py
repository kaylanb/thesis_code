import numpy as np
from scipy.spatial import KDTree

def match_radec(ref_ra,ref_dec, ra,dec, k=1, dsmax=1./3600,verb=True):
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
