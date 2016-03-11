import matplotlib.pyplot as plt
import numpy as np

import psql
import targets
import plots

#columns for dr2 and ptf data in psql db txt file
dr2_cols= range(10)
ptf_cols= range(10,17)
#loop over ptf50 to ptf200 dr2 matched files
a={}
for i in [50,100,150,200]:
    fn= '../truth_table_results/dr2_match_ptf%d.txt' % i
    dr2= psql.load_ofile(fn,dr2_cols) #data dictionary
    ptf= psql.load_ofile(fn,ptf_cols)
    a['p'+str(i)]={}
    a['p'+str(i)]['DR2']= targets.DECaLS(dr2, wise=False) #computes mags etc
    a['p'+str(i)]['PTF']= targets.PTF(ptf)
#plot
colors= plots.get_seaborn_colors()
#PTF r,g - DR2 r,g, all points same plot
fig,axes=plt.subplots(1,2,figsize=(12,8))
ax=axes.flatten()
plt.subplots_adjust(hspace=0.1,wspace=0.25)
#add pts
for cnt,key in enumerate(['p200','p150','p100','p50']):
    diff= a[key]['PTF'].data['rmag']- a[key]['DR2'].data['rmag']
    ax[0].scatter(a[key]['DR2'].data['rmag'], diff,c=colors[cnt],label=key[1:])
    diff= a[key]['PTF'].data['gmag']- a[key]['DR2'].data['gmag']
    ax[1].scatter(a[key]['DR2'].data['gmag'], diff,c=colors[cnt])
#
ax[0].legend(loc=2,fontsize='xx-large',markerscale=3,frameon=True)
for cnt,band in enumerate(['r','g']):
    ax[cnt].set_ylabel('%s (PTF) - %s (DR2)' % (band,band))
    ax[cnt].set_xlabel('%s (DR2)' %(band,))
plt.savefig('./dr2_v_ptf.png',dpi=200)
plt.close()

#PTF r,g - DR2 r,g, ptf50 gets its own panel, same for 100-200
for cnt,key in enumerate(['p200','p150','p100','p50']):
	fig,axes=plt.subplots(1,2,figsize=(12,8))
	ax=axes.flatten()
	plt.subplots_adjust(hspace=0.1,wspace=0.25)
	#add pts
	diff= a[key]['PTF'].data['rmag']- a[key]['DR2'].data['rmag']
	ax[0].scatter(a[key]['DR2'].data['rmag'], diff,c=colors[cnt],label=key[1:])
	diff= a[key]['PTF'].data['gmag']- a[key]['DR2'].data['gmag']
	ax[1].scatter(a[key]['DR2'].data['gmag'], diff,c=colors[cnt])
	#
	ax[0].legend(loc=2,fontsize='xx-large',markerscale=3,frameon=True)
	for cnt,band in enumerate(['r','g']):
		ax[cnt].set_ylabel('%s (PTF) - %s (DR2)' % (band,band))
		ax[cnt].set_xlabel('%s (DR2)' %(band,))
		#ax[cnt].set_xlim(14,27)
		#ax[cnt].set_ylim(-27,-19)
	plt.savefig('./dr2_v_ptf_%s.png' % key[1:],dpi=200)
	plt.close()
