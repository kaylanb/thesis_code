'''
pulls out ipm profiling info from stdout and *.xml files
'''


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

def read_lines(fn):
    fobj=open(fn,'r')
    lines=fobj.readlines()
    fobj.close()
    lines=np.char.strip(lines)
    return lines

def get_tractor_staget(stdout,nodes,stage='tims',junk_fn='stage1.txt'):
    '''return numpy array of Grand Total wall times for each code'''
    junk= bash_result("grep 'Resources for stage %s' %s -A 15|grep 'Grand total Wall' > %s" % (stage,stdout,junk_fn))
    wc= int( bash_result("wc -l %s|cut -d ' ' -f 1" % junk_fn))
    if wc != nodes:
        print "WARNING: stage=%s, Multi nodes mixed the print statements" % stage
        step=5
        for extra in range(15+step,50+step,step):
            wc= int( bash_result("grep 'Resources for stage %s' %s -A %d|grep 'Grand total Wall'|wc -l" % (stage,stdout,extra)) )
            if wc == nodes:
                print "Resolved mixed printing with extra=%d" % extra
                break
            elif wc > nodes: 
                print "WARNING: extra=%d yields too many print lines, reverting to previous number=%d" % (extra,extra-step)
                extra-= step
                break
        # Use extra from iterations
        os.remove(junk_fn)
        junk= bash_result("grep 'Resources for stage %s' %s -A %d|grep 'Grand total Wall' > %s" % (stage,stdout,extra,junk_fn))
        wc= int( bash_result("wc -l %s|cut -d ' ' -f 1" % junk_fn))
        if wc != nodes:
            print 'WARNING, stage=%s, after iteration has %d lines < %d nodes' % (wc,nodes)
    lines= read_lines(junk_fn)
    os.remove(junk_fn)
    times=np.zeros(lines.size)+np.nan
    for cnt,line in enumerate(lines):
        times[cnt]= line.split(' ')[-2]
    return times



def get_tractor_wallt(stdout,nodes, junk_fn='time1.txt'):
    '''return numpy array of Grand Total wall times for each code'''
    junk= bash_result("grep 'Grand total Wall' %s > %s" % (stdout,junk_fn))
    # Clean up
    lines= read_lines(junk_fn)
    os.remove(junk_fn)
    fin=open(junk_fn,'w')
    for line in lines:
        index=line.find("Grand total Wall")
        if index != -1:
            fin.write(line[index:]+'\n')
    fin.close()
    # 2d numpy array
    lines= read_lines(junk_fn)
    times=np.zeros(lines.size)+np.nan
    for cnt,line in enumerate(lines):
        times[cnt]= line.split(' ')[-2] 
    os.remove(junk_fn)
    # rank and take 1st nodes times
    return np.sort(times)[::-1][:nodes]

def get_syscall_io(stdout, junk_fn='io1.txt'):
    '''return np array of all syscall input,output MiB lines
    Returns: units of GB'''
    junk= bash_result("grep 'proc' %s| grep 'syscall input'|grep 'MiB' > %s" % (stdout,junk_fn))
    # Clean up
    lines= read_lines(junk_fn)
    os.remove(junk_fn)
    fin=open(junk_fn,'w')
    for line in lines:
        index=line.find("[/proc]: syscall input")
        if index != -1:
            fin.write(line[index:]+'\n')
    fin.close()
    # 2d numpy array
    lines= read_lines(junk_fn)
    tot_Gb=np.zeros( (lines.size,2))+np.nan
    for cnt,line in enumerate(lines):
        tot_Gb[cnt,:]= np.array(line.split(' '))[[4,9]] 
    os.remove(junk_fn)
    return tot_Gb/1024.


def parse_stdout(stdout, appendfn):
	# grep
	ncores= str(bash_result("grep 'Command-line args:' %s|cut -d ',' -f 11" % stdout) )
	ncores= int( ncores.replace('"','').replace("'",'') )
	t_io_kernel= float( bash_result("grep proc %s|grep 'block I/O delays' | cut -d ' ' -f 6|tail -n 1" % stdout) )
	t_io_wrapper= str( bash_result("grep '# I/O' %s | tail -n 1" % stdout) )
	t_io_wrapper= float(t_io_wrapper.split()[-1])
	inGb= str( bash_result("grep 'proc' %s| grep 'syscall input'|tail -n 2|head -n 1|cut -d ' ' -f 5,10" % stdout) )
	inGb,outGb= float(inGb.split()[0])/1024.,float(inGb.split()[-1])/1024.
	wall= float( bash_result("grep '# stop' %s|tail -n 1|cut -d ' ' -f 18" % stdout) )
	percent_io= str( bash_result("grep '# I/O' %s -A 2|tail -n 1" % stdout) )
	percent_io= float(percent_io.split()[-1])
	#print "total I/O (syscall input + output)=%.4f" % (inGb+outGb,)
	#print "achieved I/O bandwidth kernel=%.4f, wrapper=%.4f" % \
	#		((inGb+outGb)/t_io_kernel,(inGb+outGb)/t_io_wrapper)
	#print "wallclock=%.2f [sec], percent time i/o=%.2f" % (wall,percent_io)
	fout=open(appendfn,'a')
	fout.write("#ncores wallt[s] percI/O totalGB Bandwidth_kernel[GB/s] Bandwidth_wrapper[GB/s] stdout\n")
	fout.write("%d %.2f %.2f %.2f %.2f %.2f %s\n" % \
				(ncores,wall,percent_io,inGb+outGb,\
				(inGb+outGb)/t_io_kernel,(inGb+outGb)/t_io_wrapper, stdout))
	fout.close()



def parse_multi_node(stdout, appendfn):
    nodes= int(bash_result("grep 'Command-line args:' %s |wc -l" % stdout) )
    ncores= str(bash_result("grep 'Command-line args:' %s|cut -d ',' -f 11|tail -n 1" % stdout) )
    ncores= int( ncores.replace('"','').replace("'",'') )
    wall_overnodes= float( bash_result("grep '# stop' %s|tail -n 1|cut -d ' ' -f 18" % stdout) )
    if nodes == 2:
        tot_inGb= str( bash_result("grep 'proc' %s| grep 'syscall input'|tail -n 4|head -n 1|cut -d ' ' -f 5,10" % stdout) )
        tot_inGb,tot_outGb= float(tot_inGb.split()[0])/1024.,float(tot_inGb.split()[-1])/1024.
        t_io_kernel= float( bash_result("grep proc %s|grep 'block I/O delays' | cut -d ' ' -f 6|tail -n 2|head -n 1" % stdout) )
        t_io_wrapper= str( bash_result("grep '# I/O' %s | tail -n 1" % stdout) )
        t_io_wrapper= float(t_io_wrapper.split()[-1])
        tot_percent_io= str( bash_result("grep '# I/O' %s -A 2|tail -n 1" % stdout) )
        tot_percent_io= float(tot_percent_io.split()[-1])
    elif nodes == 8:
        tot_inGb= str( bash_result("grep 'proc' %s| grep 'syscall input'|grep 'MiB'|tail -n 1|cut -d ' ' -f 5,10" % stdout) )
        tot_inGb,tot_outGb= float(tot_inGb.split()[0])/1024.,float(tot_inGb.split()[-1])/1024.
        t_io_kernel= float( bash_result("grep proc %s|grep 'block I/O delays' |tail -n 1|cut -d ' ' -f 6" % stdout) )
        t_io_wrapper= str( bash_result("grep '# I/O' %s |tail -n 2|head -n 1" % stdout) )
        t_io_wrapper= float(t_io_wrapper.split()[-1])
        tot_percent_io= str( bash_result("grep '%%wall' %s -A 1|grep 'I/O'|tail -n 1" % stdout) )
        tot_percent_io= float(tot_percent_io.split()[-1])
    elif nodes == 64:
        tot_inGb,tot_outGb= -1.,-1.
        # other stuff
        t_io_kernel= float( bash_result("grep proc %s|grep 'block I/O delays' |tail -n 1|cut -d ' ' -f 6" % stdout) )
        t_io_wrapper= str( bash_result("grep '# I/O' %s |tail -n 2|head -n 1" % stdout) )
        t_io_wrapper= float(t_io_wrapper.split()[-1])
        tot_percent_io= -1.
        #tot_percent_io= str( bash_result("grep '%%wall' %s -A 1|grep 'I/O'|tail -n 1" % stdout) )
        #tot_percent_io= float(tot_percent_io.split()[-1])
    else: raise ValueError('%d nodes not supported' % nodes)
    # Tractor Grand wall times
    times={}
    times['tot']= get_tractor_wallt(stdout,nodes)
    for stage in ['tims','fitblobs']:
        times[stage]= get_tractor_staget(stdout,nodes,stage=stage)
    # all syscall io lines
    tot_Gb= get_syscall_io(stdout)
    sum_in,sum_out= tot_Gb[:,0].sum(),tot_Gb[:,1].sum()
    #index= np.argsort(tot_Gb[:,1])[::-1][0]
    # Print and write out
    print nodes,ncores,wall_overnodes,tot_percent_io,tot_inGb,tot_outGb,t_io_kernel,t_io_wrapper,stdout
    fout=open(appendfn,'a')
    fout.write("#nnodes ncores times:tims.min tims.max fit.min fit.max total.min total.max sum_in sum_out wallt[s] percI/O totalGB Bandwidth_kernel[GB/s] Bandwidth_wrapper[GB/s] stdout\n")
    fout.write("%d %d %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.4f %.4f %.2f %.2f %.2f %.2f %.2f %s\n" % \
                (nodes,ncores,times['tims'].min(),times['tims'].max(),times['tims'].mean(),times['fitblobs'].min(),times['fitblobs'].max(),times['fitblobs'].mean(),times['tot'].min(),times['tot'].max(),times['tot'].mean(),sum_in,sum_out,wall_overnodes,tot_percent_io,tot_inGb+tot_outGb,\
                (tot_inGb+tot_outGb)/t_io_kernel,(tot_inGb+tot_outGb)/t_io_wrapper, stdout))
    fout.close()

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
	parser.add_argument("--stdout",action="store",required=True)
	parser.add_argument("--appendfn",action="store",default='ipm_analysis.txt',required=False)
	args = parser.parse_args()
	# bandwidth
	#parse_stdout(args.stdout, args.appendfn)
	res= parse_multi_node(args.stdout, args.appendfn)
	print "done"
