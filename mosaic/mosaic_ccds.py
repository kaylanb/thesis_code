'''PTF analysis flow:
1. legacypipe/cp_files.py -- copy all images want to analyze into path/to/images/
2. this script -- make 1 directory in path/to/ to write ccd.fits table for all images, decals_dir, soft links, psfex, etc
3. run tractor on dir pointing it to the decals_dir,output dir each time'''


import os
import numpy as np
import fitsio
from argparse import ArgumentParser
import glob
from astrometry.util.fits import fits_table
from astrometry.util.starutil_numpy import degrees_between, hmsstring2ra, dmsstring2dec
from astrometry.util.util import Tan, Sip, anwcs_t

def exposure_metadata(filenames, hdus=None, trim=None):
    '''
    Creates a CCD table row object by reading metadata from a FITS
    file header.

    Parameters
    ----------
    filenames : list of strings
        Filenames to read
    hdus : list of integers; None to read all HDUs
        List of FITS extensions (HDUs) to read
    trim : string
        String to trim off the start of the *filenames* for the
        *image_filename* table entry

    Returns
    -------
    A table that looks like the CCDs table.
    '''
    nan = np.nan
    primkeys = [('FILTER',''),
                ('RA', nan),
                ('DEC', nan),
                ('AIRMASS', nan),
                ('DATE-OBS', ''),
                ('EXPTIME', nan),
                ('EXPNUM', 0),
                ('MJD-OBS', 0),
                ('PROPID', ''),
                ('INSTRUME', ''),
                ]
    hdrkeys = [('AVSKY', nan),
               ('ARAWGAIN', nan),
               ('FWHM', nan),
               ('CRPIX1',nan),
               ('CRPIX2',nan),
               ('CRVAL1',nan),
               ('CRVAL2',nan),
               ('CD1_1',nan),
               ('CD1_2',nan),
               ('CD2_1',nan),
               ('CD2_2',nan),
               ('EXTNAME',''),
               ('CCDNUM',''),
               ]

    otherkeys = [('IMAGE_FILENAME',''), ('IMAGE_HDU',0),
                 ('HEIGHT',0),('WIDTH',0),
                 ]

    allkeys = primkeys + hdrkeys + otherkeys

    vals = dict([(k,[]) for k,d in allkeys])

    for i,fn in enumerate(filenames):
        print('Reading', (i+1), 'of', len(filenames), ':', fn)
        F = fitsio.FITS(fn)
        primhdr = F[0].read_header()
        expstr = '%08i' % primhdr.get('NOCID') #'EXPNUM')

        # # Parse date with format: 2014-08-09T04:20:50.812543
        # date = datetime.datetime.strptime(primhdr.get('DATE-OBS'),
        #                                   '%Y-%m-%dT%H:%M:%S.%f')
        # # Subract 12 hours to get the date used by the CP to label the night;
        # # CP20140818 includes observations with date 2014-08-18 evening and
        # # 2014-08-19 early AM.
        # cpdate = date - datetime.timedelta(0.5)
        # #cpdatestr = '%04i%02i%02i' % (cpdate.year, cpdate.month, cpdate.day)
        # #print 'Date', date, '-> CP', cpdatestr
        # cpdateval = cpdate.year * 10000 + cpdate.month * 100 + cpdate.day
        # print 'Date', date, '-> CP', cpdateval

        cpfn = fn
        if trim is not None:
            cpfn = cpfn.replace(trim, '')
        print('CP fn', cpfn)

        if hdus is not None:
            hdulist = hdus
        else:
            hdulist = range(1, len(F))

        for hdu in hdulist:
            hdr = F[hdu].read_header()

            info = F[hdu].get_info()
            #'extname': 'S1', 'dims': [4146L, 2160L]
            H,W = info['dims']

            for k,d in primkeys:
                vals[k].append(primhdr.get(k, d))
            for k,d in hdrkeys:
                vals[k].append(hdr.get(k, d))

            vals['IMAGE_FILENAME'].append( os.path.join('mosaic/',os.path.basename(cpfn)) )
            vals['ARAWGAIN'][-1]= hdr.get('GAIN') #e/ADU
            vals['FWHM'][-1]= hdr.get('SEEING1')/0.258 #pixscale=0.258 arcsec/pix
            vals['IMAGE_HDU'].append(hdu)
            vals['WIDTH'].append(int(W))
            vals['HEIGHT'].append(int(H))

    T = fits_table()
    for k,d in allkeys:
        T.set(k.lower().replace('-','_'), np.array(vals[k]))
    #T.about()

    # DECam: INSTRUME = 'DECam'
    T.rename('instrume', 'camera')
    T.camera = np.array(['mosaic' for t in T.camera]) #t.lower() for t in T.camera])

    #T.rename('extname', 'ccdname')
    T.ccdname = np.array([t.strip() for t in T.extname])
    
    T.filter = np.array(['z' for s in T.filter])  #s.split()[0] for s in T.filter])
    T.ra_bore  = np.array([hmsstring2ra (s) for s in T.ra ])
    T.dec_bore = np.array([dmsstring2dec(s) for s in T.dec])

    T.ra  = np.zeros(len(T))
    T.dec = np.zeros(len(T))
    for i in range(len(T)):
        W,H = T.width[i], T.height[i]

        wcs = Tan(T.crval1[i], T.crval2[i], T.crpix1[i], T.crpix2[i],
                  T.cd1_1[i], T.cd1_2[i], T.cd2_1[i], T.cd2_2[i], float(W), float(H))
        
        xc,yc = W/2.+0.5, H/2.+0.5
        rc,dc = wcs.pixelxy2radec(xc,yc)
        T.ra [i] = rc
        T.dec[i] = dc

#
#    T.ra  = np.zeros(len(T))
#    T.dec = np.zeros(len(T))
#    for i in range(len(T)):
#        W,H = T.width[i], T.height[i]
#
#        wcs = Tan(T.crval1[i], T.crval2[i], T.crpix1[i], T.crpix2[i],
#                  T.cd1_1[i], T.cd1_2[i], T.cd2_1[i], T.cd2_2[i], float(W), float(H))
#        
#        xc,yc = W/2.+0.5, H/2.+0.5
#        rc,dc = wcs.pixelxy2radec(xc,yc)
#        T.ra [i] = rc
#        T.dec[i] = dc

    return T



parser = ArgumentParser(description="test")
parser.add_argument("-images_dir",action="store",default='/project/projectdirs/cosmo/staging/mosaicz/Test/MOS151213_8a7fcee/',help='path/to/images/')
parser.add_argument("-search_str",action="store",default='k4m_151214_021723_oki_zd_v1.fits.fz',help='oki files')
args = parser.parse_args()

scie_files= glob.glob(os.path.join(args.images_dir,args.search_str))
if len(scie_files) == 0: raise ValueError
#make ccd table
T=exposure_metadata(scie_files, hdus=None, trim=None)
T.writeto('./mine-mosaic-ccds.fits')
print 'wrote ccds table'
