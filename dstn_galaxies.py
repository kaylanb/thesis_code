import matplotlib
matplotlib.use('Agg')
import numpy as np
import pylab as plt
from tractor.pointsource import PointSource
from tractor.galaxy import *
from tractor.sersic import *
from tractor.image import Image
from tractor.psf import NCircularGaussianPSF
from tractor.wcs import PixPos
from tractor.brightness import Flux
from tractor.ellipses import EllipseE,EllipseESoft

# size of image
W,H = 40,40

# PSF size
psfsigma = 1.

# per-pixel noise
noisesigma = 1.e-2

# create tractor.Image object for rendering synthetic galaxy
# images
tim = Image(data=np.zeros((H,W)), invvar=np.ones((H,W)) / (noisesigma**2),
            psf=NCircularGaussianPSF([psfsigma], [1.]))

sources = [ PointSource(PixPos(20,20), Flux(10.)),
            ExpGalaxy(PixPos(30,10), Flux(10.), EllipseE(0.45,0.,0.)),
            ExpGalaxy(PixPos(10,10), Flux(10.), EllipseE(3., 0.5, 45.)),
            DevGalaxy(PixPos(30,30), Flux(10.), EllipseE(3., 0., -0.5)),
            FixedCompositeGalaxy(PixPos(10,30),Flux(10.), 0.8,
                            EllipseE(2.,0.,0.),EllipseE(1., 0., 0.))]
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

