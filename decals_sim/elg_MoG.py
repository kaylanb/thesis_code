#!/usr/bin/env python

"""Generate the figures for Sec 3.3 (ELG target selection) of the FDR.

J. Moustakas
Siena College
2016 Feb 24

"""

from __future__ import division, print_function

import matplotlib
matplotlib.use('Agg')
import os
import sys
import argparse

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.table import Table

from thesis_code import fits as myfits

def plot_elgs(zcat, figfile='test.png'):
	sns.set(style='white', font_scale=1.4, palette='Set2')
	col = sns.color_palette()
	area = 0.4342   # [deg^2]
	oiicut1 = 8E-17 # [erg/s/cm2]
	zmin = 0.6
	zmax = 1.6
	rfaint = 23.4
	grrange = (-0.3,2.0)
	rzrange = (-0.5,2.1)
	#print("zcat['CFHTLS_R']= ",zcat['CFHTLS_R']<rfaint)
	loz = np.all((zcat['ZBEST']<zmin,\
				  zcat['CFHTLS_R']<rfaint),axis=0)
	oiifaint = np.all((zcat['ZBEST']>zmin,\
					   zcat['CFHTLS_R']<rfaint,\
					   zcat['OII_3727_ERR']!=-2.0,\
					   zcat['OII_3727']<oiicut1),axis=0)
	oiibright_loz = np.all((zcat['ZBEST']>zmin,\
							zcat['ZBEST']<1.0,\
							zcat['CFHTLS_R']<rfaint,\
							zcat['OII_3727_ERR']!=-2.0,\
							zcat['OII_3727']>oiicut1),axis=0)
	oiibright_hiz = np.all((zcat['ZBEST']>1.0,\
							zcat['CFHTLS_R']<rfaint,\
							zcat['OII_3727_ERR']!=-2.0,\
							zcat['OII_3727']>oiicut1),axis=0)
	print(len(loz), len(oiibright_loz), len(oiibright_hiz), len(oiifaint))

	def getgrz(zcat, index):
		gr = zcat['CFHTLS_G'][index] - zcat['CFHTLS_R'][index]
		rz = zcat['CFHTLS_R'][index] - zcat['CFHTLS_Z'][index]
		return gr, rz

	fig, ax = plt.subplots(1, 1, figsize=(8,5))
	gr, rz = getgrz(zcat, loz)
	ax.scatter(rz, gr, marker='^', color=col[2], label=r'$z<0.6$')

	gr, rz = getgrz(zcat, oiifaint)
	ax.scatter(rz, gr, marker='s', color='tan', 
			   label=r'$z>0.6, [OII]<8\times10^{-17}$')

	gr, rz = getgrz(zcat, oiibright_loz)
	ax.scatter(rz, gr, marker='o', color='powderblue', 
			   label=r'$z>0.6, [OII]>8\times10^{-17}$')

	gr, rz = getgrz(zcat, oiibright_hiz)
	ax.scatter(rz, gr, marker='o', color='powderblue', edgecolor='black', 
			   label=r'$z>1.0, [OII]>8\times10^{-17}$')

	#gr, rz = getgrz(stars, np.where((stars['FIELD']==1)*1)[0])
	#sns.kdeplot(rz, gr, cmap='Greys_r', clip=(rzrange, grrange),
	#            levels=(1-0.75, 1-0.5, 1-0.25, 1-0.1))
	#            #levels=(0.5, 0.6, 0.75, 0.9, 0.99))
	
	ax.set_xlabel(r'$(r - z)$')
	ax.set_ylabel(r'$(g - r)$')
	ax.set_xlim(rzrange)
	ax.set_ylim(grrange)
	plt.legend(loc='upper left', prop={'size': 14}, labelspacing=0.2,
			   markerscale=1.5)
	#fig.subplots_adjust(left=0.3, bottom=0.3, wspace=0.1)
	print('Writing {}'.format(figfile))
	plt.savefig(figfile, bbox_inches='tight')
    

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--targdir', action='store', help='',required=False)

	#if len(sys.argv)==1:
	#    parser.print_help()
	#    sys.exit(1)
	args = parser.parse_args()

	key = 'DESI_ROOT'
	if key in os.environ:
		desidir = os.getenv(key)
	else:
		desidir = './'
	#targdir = os.path.join(desidir, 'target/analysis/deep2/v1.0')
	targdir = os.path.join(desidir, 'target/analysis/deep2/v2.0')
	if args.targdir: targdir= args.targdir
	#targdir = os.path.join(desidir, 'target/analysis/truth')
	outdir = 'figures' # output directory
	if not os.path.exists(outdir): os.mkdir(outdir)

	## Build the samples.
	#if args.build_cfhtls:
	#    build_sample(topdir, build_cfhtls=True)
	#if args.build_sdss:
	#    build_sample(topdir, build_sdss=True)

	# Read the samples
	zcat = myfits.load(os.path.join(targdir, 'deep2egs-oii.fits.gz'))
	print("zcat.colnames= ",zcat.colnames)
	#phot = fits.getdata('deep2-phot.fits.gz', 1)
	#zcat = fits.getdata(os.path.join(targdir, 'deep2-oii.fits.gz'), 1)
	#stars = fits.getdata(os.path.join(targdir, 'deep2-stars.fits.gz'), 1)
	#zcat = fits.getdata(os.path.join(targdir, 'deep2egs-oii.fits.gz'), 1)
	#stars = fits.getdata(os.path.join(targdir, 'deep2egs-stars.fits.gz'), 1)

	# --------------------------------------------------
	# g-r vs r-z coded by [OII] strength
	name = os.path.join(outdir, 'mine_deep2-elg-grz-oii.png')
	plot_elgs(zcat, figfile=name)

if __name__ == "__main__":
    main()
