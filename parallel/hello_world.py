import multiprocessing 
import resource
import os
import numpy as np
from functools import partial

def current_mem_usage():
	'''return mem usage in MB'''
	return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.**2

def bash(cmd):
	return os.system('%s' % cmd)
	#if ret:
	#	print 'command failed: %s' % cmd
	#	raise ValueError

def work(fits_file, di=dict(),data=[]):
	name = multiprocessing.current_process().name
	cmd='python schema.py -fits_file %s' % fits_file
	ret= bash('ls %s' % fits_file)
	#bash(cmd)
	print '%s maximum memory usage: %.2f (mb)' % (name, current_mem_usage())
	return ret
	
if __name__ == '__main__':
	print "CPU has %d cores" % multiprocessing.cpu_count()
	pool = multiprocessing.Pool(4)
	fits_files= np.loadtxt('files.txt',dtype=str)
	di=dict(hello='kaylan')
	data=np.zeros((100,10))
	results=pool.map(partial(work, di=di,data=data),fits_files)
	pool.close()
	pool.join()
	del pool
	print 'Global maximum memory usage: %.2f (mb)' % current_mem_usage()
	err=np.array(results).astype(bool)
	print "These inputs failed:"
	print fits_files[err]

