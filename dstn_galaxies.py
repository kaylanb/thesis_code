import matplotlib
matplotlib.use('Agg')
import numpy as np
import pylab as plt
from argparse import ArgumentParser

from fits import tractor_cat

from tractor.pointsource import PointSource
from tractor.galaxy import *
from tractor.sersic import *
from tractor.image import Image
from tractor.psf import NCircularGaussianPSF
from tractor.wcs import PixPos
from tractor.brightness import Flux
from tractor.ellipses import EllipseE,EllipseESoft

def deg_to_arcsec(deg):
    return deg*3600.

class Grid(object):
    def __init__(self,ramin,ramax,decmin,decmax,pixscale):
        self.npix_ra= int(deg_to_arcsec(ramax-ramin)/pixscale + 1)
        self.npix_dec= int(deg_to_arcsec(decmax-decmin)/pixscale + 1)
        self.ra_centers= np.linspace(ramin,ramax,num=self.npix_ra)
        self.dec_centers= np.linspace(decmin,decmax,num=self.npix_dec)
    def nearest_cell_index(self,ra,dec):
        '''return x,y index for img of nearest ra,dec pixel center to ra,dec'''
        return np.argsort(np.abs(self.ra_centers-ra))[0], np.argsort(np.abs(self.dec_centers-dec))[0]

parser = ArgumentParser(description="test")
parser.add_argument("-cat",action="store",help='tractor catalogue')
parser.add_argument("-pixscale",type=float,action="store",help='tractor catalogue')
args = parser.parse_args()

cat=tractor_cat(args.cat)
grid= Grid(cat['ra'].min(),cat['ra'].max(),cat['dec'].min(),cat['dec'].max(),args.pixscale)

# size of image
W,H = grid.npix_ra,grid.npix_dec

# PSF size
psfsigma = 1.

# per-pixel noise
noisesigma = 1.e-2

# create tractor.Image object for rendering synthetic galaxy
# images
tim = Image(data=np.zeros((H,W)), invvar=np.ones((H,W)) / (noisesigma**2),
            psf=NCircularGaussianPSF([psfsigma], [1.]))

types={'PSF ':1,'SIMP':2,'EXP ':3,'DEV ':4,'COMP':5}
g,r= 1,2
sources=[]
for i in range(len(cat['ra'])):
    x,y= grid.nearest_cell_index(cat['ra'][i],cat['dec'][i])
    gflux= cat['decam_flux'][i][g]
    if gflux <=0: continue 
    if types[cat['type'][i]] == 1:
        sources.append( PointSource(PixPos(x,y), Flux(gflux)) )
    elif types[cat['type'][i]] == 2:
        sources.append( ExpGalaxy(PixPos(x,y), Flux(gflux), EllipseE(0.45,0.,0.)) )
    elif types[cat['type'][i]] == 3:
        radius,e1,e2= cat['shapeexp_r'][i],cat['shapeexp_e1'][i],cat['shapeexp_e2'][i]
        sources.append( ExpGalaxy(PixPos(x,y), Flux(gflux), EllipseE(radius,e1,e2)) )
    elif types[cat['type'][i]] == 4:
        radius,e1,e2= cat['shapedev_r'][i],cat['shapedev_e1'][i],cat['shapedev_e2'][i]
        sources.append( DevGalaxy(PixPos(x,y), Flux(gflux), EllipseE(radius,e1,e2)) )
    elif types[cat['type'][i]] == 5:
        fdev= cat['fracdev'][i]
        exp_r,exp_1,exp_2= cat['shapeexp_r'][i],cat['shapeexp_e1'][i],cat['shapeexp_e2'][i]
        dev_r,dev_1,dev_2= cat['shapedev_r'][i],cat['shapedev_e1'][i],cat['shapedev_e2'][i]
        sources.append( FixedCompositeGalaxy(PixPos(x,y),Flux(gflux),
                                            fdev,EllipseE(exp_r,exp_1,exp_2),EllipseE(dev_r,dev_1,dev_2)) )
    else: raise ValueError
#sources = [ PointSource(PixPos(40,40), Flux(10.)),
#            ExpGalaxy(PixPos(30,10), Flux(10.), EllipseE(0.45,0.,0.)),
#            ExpGalaxy(PixPos(10,10), Flux(10.), EllipseE(3., 0.5, 45.)),
#            DevGalaxy(PixPos(30,30), Flux(10.), EllipseE(3., 0., -0.5)),
#            FixedCompositeGalaxy(PixPos(10,30),Flux(10.), 0.8,
#                            EllipseE(2.,0.,0.),EllipseE(1., 0., 0.))]
#photocal = NullPhotoCal()
#counts = photocal.brightnessToCounts(source.getBrightness())

tractor = Tractor([tim], sources)

mod = tractor.getModelImage(0,minsb=0.,srcs=sources)

# Plot
plt.clf()
plt.imshow(np.log(mod + noisesigma),
           interpolation='nearest', origin='lower', cmap='gray')
plt.title('Galaxies')
plt.savefig('test.png')

