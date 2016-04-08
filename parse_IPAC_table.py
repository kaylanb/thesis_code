import argparse
import numpy as np
import os
import glob

parser = argparse.ArgumentParser(description="test")
parser.add_argument("-ipac_table",action="store",help='PtfQuery.tbl',required=True)
args = parser.parse_args()

#parse and output to file
fin=open(args.ipac_table,'r')
lines= fin.readlines()
fin.close()
new_table= args.ipac_table+'.fns'
if os.path.exists(new_table): os.remove(i)
fout=open(new_table,'w')
for cnt,line in enumerate(lines):
    if cnt <=8: continue #header lines
    else:
        try: 
            see,air= float(line.split()[8]),float(line.split()[9])
            if see < 10. and air < 10.: 
				fout.write(line.split()[16]+'\n')
				fout.write(line.split()[17]+'\n')
				#fout.write(line.split()[18]+'\n') #.cat file not needed
        except ValueError: continue #can encounter 'null'
fout.close()
#instruct next step
print 'loggin dtn and execute: ./download_ptf.sh %s' % new_table
print 'done'
