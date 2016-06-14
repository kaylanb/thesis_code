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

def add_box(ax, xy_lim,img_shape,test=False):
    '''draw yellow box on image already drawn onto ax
    ax -- axis to draw to
    xy_lim -- np.array of shape (N sims, 4), 4 is for xmin,xmax,ymin,ymax of bounding box
    test -- set to True to set delta x,delta y to 25-75% of image to see what this func does'''
    xmin,xmax,ymin,ymax= tuple(xy_lim)
    assert(img_shape[0] >= ymax-ymin) #compare y with image[0] b/c inverted array indices
    assert(img_shape[1] >= xmax-xmin)
    p= patches.Rectangle((xmin,ymin), xmax-xmin, ymax-ymin,
                                  fc = 'none', ec = 'yellow')
    ax.add_patch(p)

def one_image(image,name='test.png'):
    kwargs=dict(origin='lower',interpolation='nearest',cmap='gray')
    fig,ax=plt.subplots() #,sharey=True,sharex=True)
    ax.imshow(image,**kwargs)
    ax.tick_params(direction='out')
    ax.set_xlim(0,image.shape[0])
    ax.set_ylim(0,image.shape[1])
    plt.savefig(name, bbox_inches='tight',dpi=150) 

def image_v_stamp(images,xy_lim=None,name='test.png',titles=['image+sims','image','sims'],test=False):
    '''images= [img1,img2,img3]
    xy_lim -- np.array of shape (N sims, 4), 4 is for xmin,xmax,ymin,ymax of bounding box
    name -- filename
    test -- set to True to set delta x,delta y to 25-75% of image to see what this func does'''
    assert(len(images) == len(titles))
    kwargs=dict(origin='lower',interpolation='nearest',cmap='gray')
    ncol= len(images)
    fig,ax=plt.subplots(1,ncol) #,sharey=True,sharex=True)
    plt.subplots_adjust(wspace=0.4) #,hspace=0.2)
    for i,title in zip(range(ncol),titles):
        ax[i].imshow(images[i],**kwargs)
        ax[i].tick_params(direction='out')
        ax[i].set_xlim(0,images[i].shape[0])
        ax[i].set_ylim(0,images[i].shape[1])
        ti=ax[i].set_title(title)
        if xy_lim is not None: 
            if len(xy_lim.shape) == 2: 
                for cnt in range(xy_lim.shape[0]): add_box(ax[i],xy_lim[cnt,:],images[i].shape, test=test)
            else: add_box(ax[i],xy_lim,images[i].shape, test=test)
    plt.savefig(name, bbox_inches='tight',dpi=150, bbox_extra_artists=[ti]) 
