import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess

import psql 
import targets
import plots

#load from \o psql dump
m_gal= psql.load_ofile('../truth_table_results/deep2_f2_matched_galaxy.txt',str_kws=['type'])
m_star= psql.load_ofile('../truth_table_results/deep2_f2_matched_star.txt',str_kws=['type'])
un_gal= psql.load_ofile('../truth_table_results/deep2_f2_unmatched_galaxy.txt')
un_star= psql.load_ofile('../truth_table_results/deep2_f2_unmatched_star.txt')
#matched have dr2 tractor catalog data, color cut 
targets.get_targets(m_gal)
targets.get_targets(m_star)

#base name for pngs
base= 'truth_v_dr2_'
#locations of matched, unmatched objects
kwargs=dict(s=50,facecolors='none',linewidths=2.)
plt.scatter(m_gal['dr2_ra'],m_gal['dr2_dec'],edgecolors='b',label='m_gal',marker='o',**kwargs)
plt.scatter(m_star['dr2_ra'],m_star['dr2_dec'],edgecolors='m',label='m_star',marker='*',**kwargs)
plt.scatter(un_gal['ra'],un_gal['dec'],edgecolors='g',label='un_gal',marker='o',**kwargs)
plt.scatter(un_star['ra'],un_star['dec'],edgecolors='y',label='un_star',marker='*',**kwargs)
plt.legend(loc=(1.01,0),scatterpoints=1)
plt.savefig('./'+base+'radec.png')
plt.close()

#r-z vs. g-r plot
x=m_gal['rmag']-m_gal['zmag']
y=m_gal['gmag']-m_gal['rmag']
# ['bgs','lrg','elg','qso']
plt.scatter(x,y,s=50,marker='o',facecolors='none',edgecolors='r',label='other')
ind= m_gal['elg']
plt.scatter(x[ind],y[ind],s=50,marker='o',facecolors='none',edgecolors='b',label='elg')
#cut lines
x2=np.linspace(x.min(),x.max())
plt.plot(x2,1.0*x2-0.2,'k--')
plt.plot(x2,-1.0*x2+1.2,'k--')
plt.plot([0.3]*len(x2),x2,'k--')
#
plt.ylabel('r-z')
plt.xlabel('g-r')
plt.xlim(x.min(),x.max())
plt.ylim(y.min(),y.max())
plt.legend(loc=(1.01,0),scatterpoints=1)
plt.savefig('./'+base+'rz_gr.png')
plt.close()

#completeness
#same magnitude bins for detections
lo=int(min(m_gal['bestr'].min(),un_gal['bestr'].min(),m_star['bestr'].min(),un_star['bestr'].min()))-1
hi=int(max(m_gal['bestr'].max(),un_gal['bestr'].max(),m_star['bestr'].max(),un_star['bestr'].max()))+1
bins=np.linspace(lo,hi,20)
h={}
h['m_gal']= plt.hist(m_gal['bestr'],bins=bins)
h['un_gal']= plt.hist(un_gal['bestr'],bins=bins)
h['m_star']= plt.hist(m_star['bestr'],bins=bins)
h['un_star']= plt.hist(un_star['bestr'],bins=bins)
plt.close()
#plot normalizing by total counts
fig,ax=plt.subplots(2,1,figsize=(10,10))
plt.subplots_adjust(wspace=0.5,hspace=0.2)
kwargs=dict(bar=dict(color='b'), text=dict(fontsize=20)) #,edgecolor='b',linewidth=2.,fill=False)
mpl.rcParams['xtick.labelsize'] = kwargs['text']['fontsize']-10
mpl.rcParams['ytick.labelsize'] = kwargs['text']['fontsize']-10
#panel 1
width= h['m_gal'][1][1:]-h['m_gal'][1][:-1]
ax[0].bar(h['m_gal'][1][:-1],h['m_gal'][0]/(h['m_gal'][0]+h['un_gal'][0]),width=width,**kwargs['bar'])
ax[0].set_ylabel("Completeness",**kwargs['text'])
ax[0].set_title("Galaxies",**kwargs['text'])
#panel 2
ax[1].bar(h['m_star'][1][:-1],h['m_star'][0]/(h['m_star'][0]+h['un_star'][0]),width=width,**kwargs['bar'])
ax[1].set_ylabel("Completeness",**kwargs['text'])
ax[1].set_title("Stars",**kwargs['text'])
ax[1].set_xlabel("R (AB)",**kwargs['text'])
for i in range(2):
    ax[i].set_ylim(0,1.1)
plt.savefig("completeness.png")

#FPs based on color cuts
#this looks bad, only 7% of the DEEP2 galaxies are the types of galaxies we are looking for (ELG,LRG,QSO,BGS), 
#but it is okay because DEEP2 targetted galaxies based on cuts in B-R vs. R-I color space only
pred_psf= m_gal['ptsrc']
pred_gal= m_gal['non_ptsrc']
h1=[m_gal['bestr'][pred_gal],m_gal['bestr'][pred_psf]]
print 'True=Galaxy, FP/(TP+FP)= ',m_gal['bestr'][pred_psf].shape[0]/float(m_gal['bestr'].shape[0])
pred_psf= m_star['ptsrc']
pred_gal= m_star['non_ptsrc'] 
h2=[m_star['bestr'][pred_psf],m_star['bestr'][pred_gal]]
lab1=['TP','FP']
titles=['True=Galaxy','True=Star']
plots.hist_2yaxis(h1,h2,lab1=lab1,lab2=lab1,titles=titles,fname='./'+base+'FP_colorcuts.png')
print 'True=Star, FP/(TP+FP)= ',m_star['bestr'][pred_gal].shape[0]/float(m_star['bestr'].shape[0])

#FPs based on tractor cat 'TYPE'
#This is encouraging, if galaxies are defined as "not PSF" we only mis classify 45% of them. 
#At our magnitude limit of r < 24, we would only expect to correctly classify galaxies ~ 50% of the time
#in addition, higher redshift galaxies are small so would be correctly labeled as "PSF" by Tractor
pred_psf= m_gal['type'] == ' PSF'
pred_gal= m_gal['type'] != ' PSF'
h1=[m_gal['bestr'][pred_gal],m_gal['bestr'][pred_psf]]
print 'True=Galaxy, FP/(TP+FP)= ',m_gal['bestr'][pred_psf].shape[0]/float(m_gal['bestr'].shape[0])
pred_psf= m_star['type'] == ' PSF'
pred_gal= m_star['type'] != ' PSF'
h2=[m_star['bestr'][pred_psf],m_star['bestr'][pred_gal]]
lab1=['TP','FP']
titles=['True=Galaxy','True=Star']
plots.hist_2yaxis(h1,h2,lab1=lab1,lab2=lab1,titles=titles,fname='./'+base+'FP_type.png')
print 'True=Star, FP/(TP+FP)= ',m_star['bestr'][pred_gal].shape[0]/float(m_star['bestr'].shape[0])


