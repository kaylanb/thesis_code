import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os
from argparse import ArgumentParser
import pickle

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

def tractor_profile_plots(mem,tm,nthreads=1,lstr=False):
    '''Time vs. tractor Stage'''
    name='time_v_stage_threads%d_bb.png' % nthreads
    if lstr: name= name.replace('bb','lsrt')
    fig,ax=plt.subplots()
    xvals= np.arange(tm['stage'].size)+1
    print tm['parallel']
    add_scatter(ax,xvals, tm['serial']/60., c='b',m='o',lab='serial',drawln=True)
    add_scatter(ax,xvals, tm['parallel']/60., c='g',m='o',lab='parallel',drawln=True)
    plt.legend(loc='upper right',scatterpoints=1)
    #add_scatter(ax,xvals, tm['total']/60., c='b',m='o',lab='total')
    ax.set_xticks(xvals)
    ax.set_xticklabels(tm['stage'],rotation=45, ha='right')
    ax.set_yscale('log')
    ax.set_ylim([1e-3,1e2])
    xlab=ax.set_ylabel('Wall Time (min)')
    ylab=ax.set_xlabel('Tractor Stage')
    plt.savefig(name, bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
    plt.close()

def tractor_profile_plots_multi(bb_pickle,lstr_pickle,nthreads=1):
    '''same as above:Time vs. tractor Stage
    but multiple lines from pickle data'''
    name='time_v_stage_threads%d_multi.png' % nthreads
    # Get data
    tm={}
    for key,fn in zip(['bb','lustre'],[bb_pickle,lstr_pickle]):
        fobj=open(fn)
        tm[key]=pickle.load(fobj)
        fobj.close()
    # Plot
    fig,ax=plt.subplots()
    for key,col in zip(tm.keys(),['b','g']):
        xvals= np.arange(tm[key]['stage'].size)+1
        add_scatter(ax,xvals, (tm[key]['serial']+tm[key]['parallel'])/60., c=col,m='o',lab=key,drawln=True)
        #add_scatter(ax,xvals, tm['total']/60., c='b',m='o',lab='total')
    plt.legend(loc='upper right',scatterpoints=1)
    ax.set_xticks(xvals)
    ax.set_xticklabels(tm[key]['stage'],rotation=45, ha='right')
    ax.set_yscale('log')
    #ax.set_ylim([1e-2,1e1])
    xlab=ax.set_ylabel('Wall Time (min)')
    ylab=ax.set_xlabel('Tractor Stage')
    plt.savefig(name, bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
    plt.close()


def plot_wall_node(d):
    name='wall_v_nodes.png'
    fig,ax=plt.subplots()
    xvals= np.arange(d['nodes'].size)+1
    add_scatter(ax,xvals, d['tims_mean']/60., c='b',m='o',lab='tims',drawln=True)
    add_scatter(ax,xvals, d['fit_mean']/60., c='g',m='o',lab='fit',drawln=True)
    add_scatter(ax,xvals, d['tot_mean']/60., c='k',m='o',lab='total',drawln=True)
    plt.legend(loc='lower right',scatterpoints=1)
    #add_scatter(ax,xvals, tm['total']/60., c='b',m='o',lab='total')
    ax.set_xticks(xvals)
    names= np.zeros(d['nodes'].size).astype(str)
    for i in range(names.size): 
        names[i]= '%d/%d' % (d['cores'][i],d['nodes'][i])
    ax.set_xticklabels(names,rotation=45, ha='right')
    #ax.set_yscale('log')
    #ax.set_ylim([1e-3,1e3])
    ylab=ax.set_ylabel('Wall Time (min)')
    xlab=ax.set_xlabel('Cores/Nodes')
    plt.savefig(name, bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
    plt.close()



if __name__ == '__main__':
    # Tractor stdout file, parse profiling info
    parser = ArgumentParser(description="test")
    parser.add_argument("--which",choices=['wall_vs_stage','wall_vs_cores','wall_vs_nodes'],action="store",required=True)
    parser.add_argument("--data_fn",action="store",help='wall_vs_stage: stdout file, wall_vs_cores: text file output of ipm_scaling.py, wall_vs_nodes: text file output of ipm_scaling.py',required=True)
    parser.add_argument("--lstr",action="store_true",help='set to interpret file as from LUSTRE, otherwise assumed from BurstBuffer',required=False)
    parser.add_argument("--outdir",action="store",help='where to write outputs',default='.',required=False)
    args = parser.parse_args()

    if args.which == 'wall_vs_stage':
        # parse stdout and read data into numpy arrays
        fmem= os.path.join(os.path.dirname(args.data_fn),\
                           os.path.basename(args.data_fn)+'_mem.txt')
        ftime= os.path.join(os.path.dirname(args.data_fn),\
                            os.path.basename(args.data_fn)+'_time.txt')
        # multi node
        # grep "runbrick.py starting at" bb_multi.o2907746
        # grep "Stage writecat finished:" bb_multi.o2907746
        for fn in [fmem,ftime]:
            if os.path.exists(fn):
                print 'using existing file: %s' % fn
            else:
                bash_result("grep 'Resources for' %s -A 2|grep -e 'Wall:' -e 'Resources' > %s_mem.txt" % (args.data_fn,args.data_fn))
                bash_result("grep -e 'Resources for stage' -e 'Total serial Wall' -e 'Total parallel Wall' -e 'Grand total Wall' -e 'Grand total CPU utilization' %s > %s_time.txt" % (args.data_fn,args.data_fn))
        mem=parse_tractor_profile(fmem)
        tm=parse_tractor_profile(ftime)
        # plots
        ncores= str(bash_result("grep 'Command-line args:' %s|cut -d ',' -f 11|tail -n 1" % args.data_fn) )
        ncores= int( ncores.replace('"','').replace("'",'') )
        # write timing info to text file and create a pickle file
        fout=open('stage_timings.txt','a')
        fout.write('#nodes cores times[sec]:tims fitblobs total\n')
        fout.write('1 %d %.2f %.2f %.2f\n' % (ncores,tm['total'][0],tm['total'][4],tm['total'].sum()))
        fout.close()
        fn='wall_vs_stage_bb.pickle'
        print 'args.lstr= ',args.lstr
        if args.lstr: 
            print 'fn= ',fn
            fn=fn.replace('bb','lstr')
            print 'fn= ',fn
        fout=open(fn,'w')
        pickle.dump(tm,fout)
        fout.close()
        # plot
        tractor_profile_plots(mem,tm,nthreads=ncores,lstr=args.lstr)
        f_bb,f_lstr= os.path.join(args.outdir,'wall_vs_stage_bb.pickle'),\
                     os.path.join(args.outdir,'wall_vs_stage_lstr.pickle')
        if os.path.exists(f_bb) and os.path.exists(f_lstr): 
            tractor_profile_plots_multi(f_bb,f_lstr,nthreads=ncores)
    elif args.which == 'wall_vs_cores':
        # strong scaling data
        threads,lstr,bb= np.loadtxt(args.data_fn,dtype=str,unpack=True)

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
    elif args.which == 'wall_vs_nodes':
        a= np.loadtxt(args.data_fn,dtype=float,usecols=range(11))
        d={}
        for ikey,key in enumerate(['nodes','cores','tims_min','tims_max','tims_mean','fit_min','fit_max','fit_mean','tot_min','tot_max','tot_mean']):
            d[key]= a[:,ikey]
        plot_wall_node(d)

    print "done"
