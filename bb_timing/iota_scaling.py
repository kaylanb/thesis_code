'''
pulls out ipm profiling info from stdout and *.xml files
'''

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import subprocess
import os
from argparse import ArgumentParser
import glob

def bash_result(cmd):
    res= subprocess.check_output(cmd,\
                        stderr=subprocess.STDOUT,\
                        shell=True)
    return res.strip()

def grep_wall_cores(args):
    machine='bb'
    if args.lstr: machine='lstr'
    appendfn= 'iota_timings_%s.txt' % machine
    ncores= str(bash_result("grep 'Command-line args:' %s|cut -d ',' -f 11" % args.stdout) )
    ncores= int( ncores.replace('"','').replace("'",'') )
    wall= str( bash_result("grep 'Grand total Wall' %s| tail -n 1" % args.stdout) )
    wall= float(wall.split(' ')[-2])
    fout=open(appendfn,'a')
    fout.write("#cores wallt[s] stdout\n")
    fout.write("%d %.2f %s %s\n" % (ncores,wall, machine,args.stdout))
    fout.close()
    print "appended to %s" % appendfn

def add_scatter(ax,x,y,c='b',m='o',lab='hello',s=80,drawln=False):
	ax.scatter(x,y, s=s, lw=2.,facecolors='none',edgecolors=c, marker=m,label=lab)
	if drawln: ax.plot(x,y, c=c,ls='-')

def grep_wall_nodes(args,im_size=1600):
    mydir='/project/projectdirs/desi/users/burleigh/bb_timing/'
    d={}
    for machine in ['bb','lstr']:
        if machine == 'bb':
            fns=glob.glob(os.path.join(mydir,'node_scaling/bb_200cap_32cores_*nodes'))
            if im_size == 3200: fns=glob.glob(os.path.join(mydir,'node_scaling/bb_200cap_3200*'))
        else:
            fns= glob.glob(os.path.join(mydir,'node_scaling/lstr_32cores_*nodes'))
            if im_size == 3200: fns= glob.glob(os.path.join(mydir,'node_scaling/lstr_3200*'))
        assert(len(fns) > 0)
        d[machine]=dict(cores=np.zeros(len(fns)).astype(int),\
                        nodes=np.zeros(len(fns)).astype(int),\
                        wall=np.zeros(len(fns)))
        for cnt,fn in enumerate(fns):
            for name in ['cores','nodes']:
                numb= fn[fn.find(name)-3:fn.find(name)]
                for ch in ['_','b','l','s','t','r']: 
                    numb= numb.replace(ch,'')
                d[machine][name][cnt]= int(numb)
            # wall
            print "os.path.join(fn,'output*.*')= ",os.path.join(fn,'output*.*')
            stdout=glob.glob(os.path.join(fn,'output*.*'))
            assert(len(stdout) == 1)
            wall= str(bash_result("grep 'TIME RUNBRICK' %s" % stdout[0]) )
            d[machine]['wall'][cnt]= float( wall.split()[-1] )
        # Sort
        isort= np.argsort(d[machine]['nodes']) 
        for key in d[machine].keys():
            d[machine][key]= d[machine][key][isort]
        #print "mach=%s:" % machine
        #for key in d[machine].keys(): print "%s: " % key,d[machine][key]
    # Plot
    fig,ax=plt.subplots()
    for key,col,mark,lab in zip(['lstr','bb'],['b','g'],['o']*2,['lustre','bb']):
        add_scatter(ax,d[key]['nodes'], d[key]['wall']/60., c=col,m=mark,lab=lab,drawln=True)
    ax.legend(loc='upper right',scatterpoints=1)
    #ax.set_xscale('log')
    ax.set_xticks(d[key]['nodes'])
    xlab=ax.set_xlabel('Nodes (32 cores each)')
    ylab=ax.set_ylabel('Wall Time (min)')
    plt.savefig('strong_scaling_nodes_size%d.png' % im_size, bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
    plt.close()



if __name__ == '__main__':
    # Tractor stdout file, parse profiling info
    parser = ArgumentParser(description="test")
    parser.add_argument("--stdout",action="store",required=True)
    parser.add_argument("--lstr",action="store_true",help='set to store as lustre, assumes burst buffer',required=False)
    args = parser.parse_args()
    # 
    #grep_wall_cores(args)
    grep_wall_nodes(args)
    grep_wall_nodes(args,im_size=3200)
    print "done"
