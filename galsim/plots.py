import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from astropy.io import fits
from scipy.ndimage import imread

def image_array_from_fits(fn):
    '''use fits instead of jpg!'''
    img=fits.open(fn)
    return img[1].data

def image_array_from_png(fn):
    '''reading from png is fine (but NOT jpg!)'''
    return imread(fn)

def image_plus_stamp(img,sx,sy,test=False):
    '''img -- full image
    sx -- stamp x range, list or tuple (min,max)
    sy -- ditto for y
    test -- set to True to set sx,sy to 25-75% of image to see what this func does'''
    if test: 
        sx= [int(0.25*img.shape[1]),int(0.75*img.shape[1])]
        sy= [int(0.25*img.shape[0]),int(0.75*img.shape[0])]
    assert(img.shape[0] >= sy[1]-sy[0]) #compare sy with image[0] b/c inverted array indices
    assert(img.shape[1] >= sx[1]-sx[0])
    kwargs=dict(origin='lower',interpolation='nearest',cmap='gray')
    fig,ax=plt.subplots(1,2) #,sharey=True,sharex=True)
    plt.subplots_adjust(wspace=0.4) #,hspace=0.2)
    #draw full image + stamp + yellow outline
    ax[0].imshow(img,**kwargs)
    p= patches.Rectangle((sx[0],sy[0]), sx[1]-sx[0], sy[1]-sy[0],
                                  fc = 'none', ec = 'yellow')
    ax[0].add_patch(p)
    #draw just stamp
    new_img=np.zeros(img.shape)
    new_img[sy[0]:sy[1],sx[0]:sx[1]]= img[sy[0]:sy[1],sx[0]:sx[1]]
    ax[1].imshow(new_img,**kwargs)
    #finish plot
    for i in range(2):
        ax[i].tick_params(direction='out')
        ax[i].set_xlim(0,img.shape[0])
        ax[i].set_ylim(0,img.shape[1])
    plt.savefig('test.png', bbox_inches='tight',dpi=150) # bbox_extra_artists=[xlab,ylab], 
