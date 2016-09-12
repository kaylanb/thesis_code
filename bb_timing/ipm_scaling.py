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
		pass
	else: raise ValueError('%d nodes not supported' % nodes)
	print nodes,ncores,wall_overnodes,tot_percent_io,tot_inGb,tot_outGb,t_io_kernel,t_io_wrapper,stdout
	fout=open(appendfn,'a')
	fout.write("#nnodes ncores wallt[s] percI/O totalGB Bandwidth_kernel[GB/s] Bandwidth_wrapper[GB/s] stdout\n")
	fout.write("%d %d %.2f %.2f %.2f %.2f %.2f %s\n" % \
				(nodes,ncores,wall_overnodes,tot_percent_io,tot_inGb+tot_outGb,\
				(tot_inGb+tot_outGb)/t_io_kernel,(tot_inGb+tot_outGb)/t_io_wrapper, stdout))
	fout.close()

def python_read(fn):
	fobj=open(stdout,'r')
	lines=fobj.readlines()
	fobj.close()
	lines=np.char.strip(lines)
	return lines

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
	parse_multi_node(args.stdout, args.appendfn)
	print "done"
