import matplotlib.pyplot as plt
import numpy as np

threads,lstr,bb= np.loadtxt('lstr_bb_timing.txt',dtype=str,unpack=True)

data=dict(threads=np.array(threads).astype(int),lstr=np.zeros((len(lstr),3))+np.nan)
data['bb']= data['lstr'].copy()
for i in range(len(bb)):
	data['lstr'][i,:]= np.array(lstr[i].split(':')).astype(float)
	data['bb'][i,:]= np.array(bb[i].split(':')).astype(float)
for key in ['lstr','bb']:
	data[key]= data[key][:,0]*3600 + data[key][:,1]*60 + data[key][:,2]
	assert(np.all(np.isfinite(data[key])))

fig,ax=plt.subplots()
for key,col,mark,lab in zip(['lstr','bb'],['k','b'],['o']*2,['Luster','BB']):
	#ax.scatter(data['threads'], data[key], s=80, c=col, marker=mark,label=lab)
	ax.scatter(data['threads'], data[key]/60., s=80, lw=2.,facecolors='none',edgecolors=col, marker=mark,label=lab)
#fmt='o',ms=6,mew=2.,mfc='none',mec=c_mark,c=c_mark
ax.set_xticks(data['threads'])
xlab=ax.set_xlabel('Threads')
ylab=ax.set_ylabel('Wall Time (min)')
plt.savefig('strong_scaling.png', bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
plt.close()

print "done"
