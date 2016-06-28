from __future__ import division, print_function

import matplotlib
matplotlib.use('Agg') #display backend
import matplotlib.pyplot as plt
import os
import sys
import logging
import numpy as np
import argparse

from astropy.io import fits
from astropy.table import vstack, Table

from astrometry.libkd.spherematch import match_radec

from thesis_code.qso_ts import dr3_cats

def match_two_cats(ref_cats_file,test_cats_file):
    # Set the debugging level
    lvl = logging.INFO
    logging.basicConfig(format='%(message)s', level=lvl, stream=sys.stdout)
    log = logging.getLogger('__name__')

    #get lists of tractor cats to compare
    fns_1= read_lines(ref_cats_file) 
    fns_2= read_lines(test_cats_file) 
    log.info('Comparing tractor catalogues: ')
    for one,two in zip(fns_1,fns_2): log.info("%s -- %s" % (one,two)) 
    #if fns_1.size == 1: fns_1,fns_2= [fns_1],[fns_2]
    #object to store concatenated matched tractor cats
    ref_matched = []
    ref_missed = []
    test_matched = []
    test_missed = []
    d_matched= 0.
    deg2= dict(ref=0.,test=0.,matched=0.)
    #for cnt,cat1,cat2 in zip(range(len(fns_1)),fns_1,fns_2):
    for cnt,cat1,cat2 in zip([0],[fns_1[0]],[fns_2[0]]):
        log.info('Reading %s -- %s' % (cat1,cat2))
        ref_tractor = Table(fits.getdata(cat1, 1))
        test_tractor = Table(fits.getdata(cat2, 1))
        m1, m2, d12 = match_radec(ref_tractor['ra'].copy(), ref_tractor['dec'].copy(),\
                                  test_tractor['ra'].copy(), test_tractor['dec'].copy(), \
                                  1.0/3600.0)
        miss1 = np.delete(np.arange(len(ref_tractor)), m1, axis=0)
        miss2 = np.delete(np.arange(len(test_tractor)), m2, axis=0)
        log.info('matched %d/%d' % (len(m2),len(test_tractor['ra'])))

        # Build combined catalogs
        if len(ref_matched) == 0:
            ref_matched = ref_tractor[m1]
            ref_missed = ref_tractor[miss1]
            test_matched = test_tractor[m2]
            test_missed = test_tractor[miss2]
            d_matched= d12
        else:
            ref_matched = vstack((ref_matched, ref_tractor[m1]))
            ref_missed = vstack((ref_missed, ref_tractor[miss1]))
            test_matched = vstack((test_matched, test_tractor[m2]))
            test_missed = vstack((test_missed, test_tractor[miss2]))
            d_matched= np.concatenate([d_matched, d12])
        deg2['ref']+= deg2_lower_limit(ref_tractor['ra'],ref_tractor['dec'])
        deg2['test']+= deg2_lower_limit(test_tractor['ra'],test_tractor['dec'])
        deg2['matched']+= deg2_lower_limit(ref_matched['ra'],ref_matched['dec'])
    
    return dict(ref_matched = ref_matched,
                ref_missed = ref_missed,
                test_matched = test_matched,
                test_missed = test_missed,
                d_matched= d_matched,
                deg2= deg2)


class Mags(object):
    def __init__(self,data):
        self.mag={}
        self.magivar={}
        for band,iband in zip(['g', 'r', 'z'],[1, 2, 4]):
            self.mag[band]= 22.5- 2.5*np.log10(data['decam_flux'][:,iband]/data['decam_mw_transmission'][:,iband])
            self.magivar[band]= np.power(np.log(10.)/2.5*data['decam_flux'][:,iband], 2)* \
                                    data['decam_flux_ivar'][:,iband]  
        for band,iband in zip(['w1', 'w2'],[0, 1]):
            self.mag[band]= 22.5- 2.5*np.log10(data['wise_flux'][:,iband]/data['wise_mw_transmission'][:,iband])
            self.magivar[band]= np.power(np.log(10.)/2.5*data['wise_flux'][:,iband], 2)* \
                                    data['wise_flux_ivar'][:,iband]  

parser=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='Validation plots')
parser.add_argument('--star', help='star file',required=False)
parser.add_argument('--qso', help='qso file',required=False)
args = parser.parse_args()

# Read in training data
path='/global/project/projectdirs/desi/target/analysis/truth/'
qso= Table(fits.getdata(os.path.join(path,'AllQSO.DECaLS.dr2.fits'), 1))
star= Table(fits.getdata(os.path.join(path,'Stars_str82_355_4.DECaLS.dr2.fits'), 1))

# Make list of DR3 Tractor Cat that exist for ra,dec of samples
dr3_cats.list_them(ra1=qso['ra_1'].data.min(),\
                    ra2=qso['ra_1'].data.max(),\
                    dec1=qso['dec_1'].data.min(),\
                    dec2=qso['dec_1'].data.max(),\
                    outname='dr3_cats_qso.txt')
dr3_cats.list_them(ra1=star['ra_1'].data.min(),\
                    ra2=star['ra_1'].data.max(),\
                    dec1=star['dec_1'].data.min(),\
                    dec2=star['dec_1'].data.max(),\
                    outname='dr3_cats_star.txt')

# AB mags
qso_mags= Mags(qso)
star_mags= Mags(star)

# Output ra,dec lists
def radec_list(tab, name):
    fout=open(name,'w')
    fout.write('# id ra dec\n')
    for i in range(len(tab)): fout.write("%d %s %s\n" % (i+1,tab['ra_1'].data[i],tab['dec_1'].data[i]))
    fout.close()
radec_list(qso, 'qso_radec.txt')
radec_list(star, 'star_radec.txt')

# Plot
def cnt_to_rowcol(cnt, nrows=9,ncols=5):
    '''cnt is 1st indexed'''
    col= cnt- int(np.floor((cnt-1)/ncols))*ncols
    row= 1+int(np.floor((cnt-1)/ncols))
    return row,col

def get_mag_diff(obj, color):
    '''returns color as string and array of colors
    color -- "gr" or "rz" etc
    obj -- qso_mag, star_mag'''
    c1,c2=color[0],color[1]
    cmap=dict(g='g',r='r',z='z',m='w1',n='w2')
    return '%s - %s' % (cmap[c1],cmap[c2]), obj.mag[ cmap[c1] ] - obj.mag[ cmap[c2] ]

def plot_colors(qso_mags,star_mags):
    nrows,ncols=9,5
    fig, ax = plt.subplots(nrows, ncols)
    fig.set_size_inches(20, 20)
    plt.subplots_adjust(hspace=0.5,wspace=1)

    colors=['gr','gz','gm','gn','rz','rm','rn','zm','zn','mn']
    cnt=1
    for i_c1,c1 in enumerate(colors):
        for i_c2,c2 in enumerate(colors):
            if i_c2 >= i_c1: continue
            else:
                row,col= cnt_to_rowcol(cnt)
                print("cnt=%d row,col= %d,%d" % (cnt,row,col))
                ylab,y= get_mag_diff(qso_mags, c1)
                xlab,x= get_mag_diff(qso_mags, c2)
                ax[row-1,col-1].scatter(x,y, s=35) #c=qso['z'], vmin=0., vmax=qso['z'].max(), s=35, cmap=cm)
                ax[row-1,col-1].set_ylabel(ylab)
                ax[row-1,col-1].set_xlabel(xlab)
                cnt+=1
    plt.tight_layout()
    plt.savefig('colors.png',dpi=150) #,bbox_extra_artists=[xlab,ylab], bbox_inches='tight')
    plt.close()

#plot_colors(qso_mags,star_mags)

#cm = plt.cm.get_cmap('RdYlBu')
#for irow,row in enumerate(range(5)):
#    for col in range(5):
#        sc= ax[row,col].scatter(qso_mags['g']-qso_mags['r'], qso_mags['r']-qso_mags['w1'], c=qso['z'], vmin=0., vmax=qso['z'].max(), s=35, cmap=cm)
#        if row == 4 and col == 4: ax[row,col].colorbar(sc)
#
#
