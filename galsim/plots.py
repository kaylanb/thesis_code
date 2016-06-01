import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os
from astropy.io import fits
from scipy.ndimage import imread

def get_basename(fn):
    '''returns basename without fits or fits.gz extension'''
    base=os.path.basename(fn)
    if '.fits.fz' in base: return base.replace('.fits.fz','')
    elif '.fits' in base: return base.replace('.fits','')
    else: 
        print "fn=%s" % fn
        raise ValueError

def image_array_from_fits(fn):
    '''use fits instead of jpg!'''
    img=fits.open(fn)
    return img[1].data

def image_array_from_png(fn):
    '''reading from png is fine (but NOT jpg!)'''
    return imread(fn)

def add_box(ax, sx,sy,img_shape,test=False):
    '''draw yellow box on image already drawn onto ax
    ax -- axis to draw to
    sx -- stamp x range, list or tuple (min,max)
    sy -- ditto for y
    test -- set to True to set sx,sy to 25-75% of image to see what this func does'''
    assert(img_shape[0] >= sy[1]-sy[0]) #compare sy with image[0] b/c inverted array indices
    assert(img_shape[1] >= sx[1]-sx[0])
    p= patches.Rectangle((sx[0],sy[0]), sx[1]-sx[0], sy[1]-sy[0],
                                  fc = 'none', ec = 'yellow')
    ax.add_patch(p)

def image_v_stamp(images,name,sx=None,sy=None,multi_sims=False,test=False):
    '''images= [img1,img2,img3]
    name -- filename
    sx,sy optional x and y rng for yellow box
    multi_sims -- if True sx,sy is a list of x and y ranges for multiple sims, if False sx,sy is a single x,y range'''
    kwargs=dict(origin='lower',interpolation='nearest',cmap='gray')
    ncol= len(images)
    fig,ax=plt.subplots(1,ncol) #,sharey=True,sharex=True)
    plt.subplots_adjust(wspace=0.4) #,hspace=0.2)
    for i,title in zip(range(ncol),['image+sims','image','sims']):
        ax[i].imshow(images[i],**kwargs)
        ax[i].tick_params(direction='out')
        ax[i].set_xlim(0,images[i].shape[0])
        ax[i].set_ylim(0,images[i].shape[1])
        ti=ax[i].set_title(title)
        if sx is not None and sy is not None: 
            if multi_sims: 
                for xrng,yrng in zip(sx,sy): add_box(ax[i],xrng,yrng,images[i].shape, test=test)
            else: add_box(ax[i],sx,sy,images[i].shape, test=test)
    plt.savefig(name, bbox_inches='tight',dpi=150, bbox_extra_artists=[ti]) 
