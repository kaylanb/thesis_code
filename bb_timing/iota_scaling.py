'''
pulls out ipm profiling info from stdout and *.xml files
'''


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

def grep_wall_nodes(args):
    mydir='/project/projectdirs/desi/users/burleigh/bb_timing/'
    d={}
    for machine in ['bb','lstr']:
        if machine == 'bb':
            fns=glob.glob(os.path.join(mydir,'node_scaling/bb_200cap_32cores_*nodes'))
        else:
            fns= glob.glob(os.path.join(mydir,'node_scaling/lstr_32cores_*nodes'))
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
            stdout=glob.glob(os.path.join(fn,'output*.*'))
            assert(len(stdout) == 1)
            wall= str(bash_result("grep 'TIME RUNBRICK' %s" % stdout[0]) )
            d[machine]['wall'][cnt]= float( wall.split()[-1] )
        # Sort
        isort= np.argsort(d[machine]['nodes']) 
        for key in d[machine].keys():
            d[machine][key]= d[machine][key][isort]
        print "mach=%s:" % machine
        for key in d[machine].keys(): print "%s: " % key,d[machine][key]
    #for key in ['bb','lstr']: 
    #    d[key]={}
    #    d[key]['fn']=os.path.join(args.outdir,'iota_timings_%s.txt' % key)
    #    d[key]['cores'],d[key]['wall'],d[key]['machine']= np.loadtxt(d[key]['fn'],dtype=str,unpack=True,usecols=[0,1,2])
    #    for nm in ['cores','wall']:
    #        d[key][nm]= d[key][nm].astype(float)
    #    isort= np.argsort(d[key]['cores'])
    #    for nm in d[key].keys():
    #        if nm == 'fn': 
    #            continue
    #        else:
    #            d[key][nm]= d[key][nm][isort]
    #    # Plot
    #    fig,ax=plt.subplots()
    #    for key,col,mark,lab in zip(['lstr','bb'],['b','g'],['o']*2,['lustre','bb']):
    #        add_scatter(ax,d[key]['cores'], d[key]['wall']/60., c=col,m=mark,lab=lab,drawln=True)
    #    ax.legend(loc='upper right',scatterpoints=1)
    #    ax.set_xticks(d[key]['cores'])
    #    xlab=ax.set_xlabel('Cores')
    #    ylab=ax.set_ylabel('Wall Time (min)')
    #    plt.savefig('strong_scaling_cores.png', bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
    #    plt.close()
    #elif args.which == 'wall_vs_nodes':
    #    a= np.loadtxt(args.data_fn,dtype=float,usecols=range(11))
    #    d={}
    #    for ikey,key in enumerate(['nodes','cores','tims_min','tims_max','tims_mean','fit_min','fit_max','fit_mean','tot_min','tot_max','tot_mean']):
    #        d[key]= a[:,ikey]
    #    plot_wall_node(d)

    #print "done"
    ##machine='bb'
    #if args.lstr: machine='lstr'
    #appendfn= 'iota_timings_nodes_%s.txt' % machine
    #ncores= str(bash_result("grep 'Command-line args:' %s|cut -d ',' -f 11" % args.stdout) )
    #ncores= int( ncores.replace('"','').replace("'",'') )
    #wall= str( bash_result("grep 'Grand total Wall' %s| tail -n 1" % args.stdout) )
    #wall= float(wall.split(' ')[-2])
    #fout=open(appendfn,'a')
    #fout.write("#cores wallt[s] stdout\n")
    #fout.write("%d %.2f %s %s\n" % (ncores,wall, machine,args.stdout))
    #fout.close()
    #print "appended to %s" % appendfn



if __name__ == '__main__':
    # Tractor stdout file, parse profiling info
    parser = ArgumentParser(description="test")
    parser.add_argument("--stdout",action="store",required=True)
    parser.add_argument("--lstr",action="store_true",help='set to store as lustre, assumes burst buffer',required=False)
    args = parser.parse_args()
    # 
    #grep_wall_cores(args)
    grep_wall_nodes(args)
    print "done"
