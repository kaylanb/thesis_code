import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import itertools

#seaborn color palettes
def get_seaborn_colors():
	'''returns list of 6 rgb values'''
	sns.set_palette('colorblind')
	return sns.color_palette() #list of 6 colors

#commonly used plotting functions
def hist_2yaxis(h1,h2,lab1=[],lab2=[],titles=[],fname=None):
    '''plots 2 panel histogram, each panel has 2 hists, display both at same heights by using double y axis
	h1,h2 are lists of shape (2,N)
    lab1,lab2 are labels, lists of len 2'''
    assert(len(h1)==2)
    assert(len(h1)==len(h2))
    fig,ax=plt.subplots(2,1,figsize=(10,10))
    plt.subplots_adjust(wspace=0.5,hspace=0.2)
    #formatting
    kwargs=dict(bar=dict(alpha=0.5),text=dict(fontsize=20)) 
    mpl.rcParams['xtick.labelsize'] = kwargs['text']['fontsize']-10
    mpl.rcParams['ytick.labelsize'] = kwargs['text']['fontsize']-10
    #
    ax[0].hist(h1[0],color='b',**kwargs['bar'])
    ax[0].set_title(titles[0],**kwargs['text'])
    ax[0].set_ylabel(lab1[0],color='b',**kwargs['text'])
    for tl in ax[0].get_yticklabels():
        tl.set_color('b')
    #2nd y axis
    ax2 = ax[0].twinx()
    ax2.hist(h1[1],color='r',**kwargs['bar'])
    ax2.set_ylabel(lab1[1], color='r',**kwargs['text'])
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    #2nd panel
    ax[1].hist(h2[0],color='b',**kwargs['bar'])
    ax[1].set_title(titles[1],**kwargs['text'])
    ax[1].set_ylabel(lab2[0],color='b',**kwargs['text'])
    for tl in ax[1].get_yticklabels():
        tl.set_color('b')
    #2nd y axis
    ax2 = ax[1].twinx()
    ax2.hist(h2[1],color='r',**kwargs['bar'])
    ax2.set_ylabel(lab2[1], color='r',**kwargs['text'])
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    #label
    ax[1].set_xlabel('R (AB)',**kwargs['text'])
    if fname is not None: plt.savefig(fname)
    plt.close()

def multi_hist(nrow,ncol,h,titles=[],xlabs=[],ylabs=[],fname=''):
	'''plots single histogram in each panel
	h: shape (nrow*ncol,N points)'''
	assert(h.shape[0] <= nrow*ncol)
	assert(len(h.shape) == 2)
	if nrow == 1 or ncol == 1: raise ValueError
	#formatting
	kwargs=dict(bar=dict(alpha=0.5),text=dict(fontsize=20)) 
	mpl.rcParams['xtick.labelsize'] = kwargs['text']['fontsize']-10
	mpl.rcParams['ytick.labelsize'] = kwargs['text']['fontsize']-10
	#w,h=20,10
	fig,ax=plt.subplots(nrow,ncol) #,figsize=(w,h))
	plt.subplots_adjust(hspace=0.5,wspace=0.5)
	cnt=0
	maxcnt= h.shape[0]-1
	for r in range(nrow):
		for c in range(ncol):
			if cnt <= maxcnt:
				ax[r,c].hist(h[cnt,:],color='b',**kwargs['bar'])
				if len(titles) > 1: ax[r,c].set_title('%s' % titles[cnt],**kwargs['text'])
				if len(xlabs) > 1: ax[r,c].set_xlabel('%s' % xlabs[cnt],**kwargs['text'])
				if len(ylabs) > 1: ax[r,c].set_ylabel('%s' % ylabs[cnt],**kwargs['text'])
			cnt+=1
	plt.savefig('hist_%s.png' % fname)
	plt.close()
