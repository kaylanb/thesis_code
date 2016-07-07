import multiprocessing 
import resource
import os
import numpy as np

def current_mem_usage():
	'''return mem usage in MB'''
	return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.**2

def bash(cmd):
	return os.system('%s' % cmd)
	#if ret:
	#	print 'command failed: %s' % cmd
	#	raise ValueError

def work(fits_file):
	name = multiprocessing.current_process().name
	print name
	cmd='python schema.py -fits_file %s' % fits_file
	ret= bash('ls %s' % fits_file)
	#bash(cmd)
	print '%s maximum memory usage: %.2f (mb)' % (name, current_mem_usage())
	return ret
	
if __name__ == '__main__':
	print "CPU has %d cores" % multiprocessing.cpu_count()
	pool = multiprocessing.Pool(4)
	fits_files= np.loadtxt('files.txt',dtype=str)
	results=pool.map(work, fits_files)
	pool.close()
	pool.join()
	del pool
	print 'Global maximum memory usage: %.2f (mb)' % current_mem_usage()
	err=np.array(results).astype(bool)
	print "These inputs failed:"
	print fits_files[err]

