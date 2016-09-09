import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os
from argparse import ArgumentParser

def bash_result(cmd):
    res= subprocess.check_output(cmd,\
                        stderr=subprocess.STDOUT,\
                        shell=True)
    return res.strip()

def parse_mem(lines,nstages):
    d={}
    for key in ['stage','Wall','CPU','VmPeak','VmSize','VmRSS','VmData','maxrss']:
        d[key]=[]
    for line in lines:
        if 'Resources for stage' in line: d['stage']+= [line.split()[3]]
        elif 'Wall:' in line: 
            line= line.split(',')
			# Avoid extra worker thread columns if exists
            line= line[:len(d.keys())-1]
            for li in line:
                li=li.split()
                key=li[0][:-1]
                num=float(li[1])
#                 unit=li[2]
#                 print "key=-%s-, d.keys=" % key,d.keys()
                d[key]+= [num]
    for key in d.keys(): d[key]= np.array(d[key])
    assert(len(d['stage']) == nstages)
    return d

def parse_time(lines,nstages):
	d={}
	for key in ['stage','serial','parallel','total','util']:
		d[key]=[]
	for line in lines:
		if 'Resources for stage' in line: 
			d['stage']+= [line.split()[3]]
		elif 'serial' in line:
			d['serial']+= [float(line.split()[3])]
		elif 'parallel' in line:
			d['parallel']+= [float(line.split()[3])]
		elif 'total Wall' in line:
			d['total']+= [float(line.split()[3])]
		elif 'CPU util' in line:
			d['util']+= [float(line.split()[4])]
	for key in d.keys(): d[key]= np.array(d[key])
	assert(len(d['stage']) == nstages)
	if d['stage'].size < d['serial'].size:
		# Serial, paralel, etc contains Grand Total vals
		for key in d.keys():
			if key != 'stage': d[key]= d[key][:d['stage'].size]
	return d

def parse_tractor_profile(fn):
    fobj=open(fn,'r')
    lines=fobj.readlines()
    fobj.close()
    lines=np.char.strip(lines)
    # one more item the funcs need
    nstages= int( bash_result("grep 'Resources for stage' %s | wc -l" % fn) )
    if '_mem' in fn:
        return parse_mem(lines,nstages)
    elif '_time' in fn:
        return parse_time(lines,nstages)
    else: raise ValueError

def add_scatter(ax,x,y,c='b',m='o',lab='hello',s=80,drawln=False):
	ax.scatter(x,y, s=s, lw=2.,facecolors='none',edgecolors=c, marker=m,label=lab)
	if drawln: ax.plot(x,y, c=c,ls='-')

def tractor_profile_plots(mem,tm,nthreads=1):
	name='time_v_stage_threads%d.png' % nthreads
	fig,ax=plt.subplots()
	xvals= np.arange(tm['stage'].size)+1
	print tm['parallel']
	add_scatter(ax,xvals, tm['serial']/60., c='b',m='o',lab='serial',drawln=True)
	add_scatter(ax,xvals, tm['parallel']/60., c='g',m='o',lab='parallel',drawln=True)
	plt.legend(loc='lower right',scatterpoints=1)
	#add_scatter(ax,xvals, tm['total']/60., c='b',m='o',lab='total')
	ax.set_xticks(xvals)
	ax.set_xticklabels(tm['stage'],rotation=45, ha='right')
	ax.set_yscale('log')
	ax.set_ylim([1e-3,1e2])
	xlab=ax.set_ylabel('Wall Time (min)')
	ylab=ax.set_xlabel('Tractor Stage')
	plt.savefig(name, bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
	plt.close()



if __name__ == '__main__':
	# Tractor stdout file, parse profiling info
	parser = ArgumentParser(description="test")
	parser.add_argument("--tractor_stdout",action="store",required=True)
	parser.add_argument("--nthreads",type=int,action="store",required=True)
	args = parser.parse_args()
	# parse stdout and read data into numpy arrays
	fmem= os.path.join(os.path.dirname(args.tractor_stdout),\
					   os.path.basename(args.tractor_stdout)+'_mem.txt')
	ftime= os.path.join(os.path.dirname(args.tractor_stdout),\
					    os.path.basename(args.tractor_stdout)+'_time.txt')
	# multi node
	# grep "runbrick.py starting at" bb_multi.o2907746
	# grep "Stage writecat finished:" bb_multi.o2907746
	for fn in [fmem,ftime]:
		if os.path.exists(fn):
			print 'using existing file: %s' % fn
		else:
			print 'creating file: %s' % fn
			junk= bash_result('./profile_info.sh %s' % args.tractor_stdout)
	mem=parse_tractor_profile(fmem)
	tm=parse_tractor_profile(ftime)
	# plots
	tractor_profile_plots(mem,tm,nthreads=args.nthreads)


	# strong scaling data
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
	for key,col,mark,lab in zip(['lstr','bb'],['g','b'],['o']*2,['Lustre','BB']):
		add_scatter(ax,data['threads'], data[key]/60., c=col,m=mark,lab=lab)
	ax.legend(loc='upper right',scatterpoints=1)
	ax.set_xticks(data['threads'])
	xlab=ax.set_xlabel('Threads')
	ylab=ax.set_ylabel('Wall Time (min)')
	plt.savefig('strong_scaling.png', bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
	plt.close()

	print "done"
