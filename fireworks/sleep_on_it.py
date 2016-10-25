import time
import sys
time.sleep(2)
num= sys.argv[1]
if num <= 10:
    raise ValueError('try num+100')
fin=open('fire_%d.txt' % num,'w')
fin.write('hello there\n')
fin.close()
