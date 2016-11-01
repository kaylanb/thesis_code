import numpy as np

class Translator(object):
    def __init__(self,j,a):
        self.j=j
        self.a=a
        #
        sj,sa= set(self.j.get_columns()),set(self.a.get_columns())
        self.both=list(sj.intersection(sa))
        self.a_only=list(sa.difference(sj))
        self.j_only=list(sj.difference(sa))
#         self.print_set('both',self.both)
#         self.print_set('a_only',self.a_only)
#         self.print_set('j_only',self.j_only)
        #
        self.translate()
        # numeric vs. str keys
        self.float_or_str()
        # What did we miss?
        print '----\nmissing from Johns\n----'
        for key in j.get_columns():
            if key not in self.j2a.keys():
                print '%s' % key
        vals=[v for k,v in self.j2a.items()]
        print '----\nmissing from Arjuns\n----'
        for key in a.get_columns():
            if key not in vals:
                print '%s' % key
        # Comparisons
        self.compare_strings()
            
        
    def map_a2j(self,key):
        d= dict(ra='ra_bore',dec='dec_bore',\
                arawgain='gain',\
                ccdhdunum='image_hdu',\
                zpt='zptavg',\
                filename='image_filename',\
                naxis1='width',\
                naxis2='height')
        return d[key]
        
    def translate(self):
        j2a={}
        skip=[]
        for key in self.both:
            if key in ['zpt','ra','dec']:
                skip+= [key]
            else:
                j2a[key]=key
        for key in self.a_only:
            if np.any((key.startswith('ccdhdu'),\
                       key.startswith('ccdnmatcha'),\
                       key.startswith('ccdnmatchb'),\
                       key.startswith('ccdnmatchc'),\
                       key.startswith('ccdnmatchd'),\
                       key.startswith('ccdzpta'),\
                       key.startswith('ccdzptb'),\
                       key.startswith('ccdzptc'),\
                       key.startswith('ccdzptd'),\
                       key.startswith('ccdnum')),axis=0):
                skip+= [key]
            elif key.startswith('ccd'):
                j2a[key.replace('ccd','')]=key
            else:
                skip+= [key]
        for key in skip:
            try: 
                j2a[ self.map_a2j(key) ]= key
            except KeyError:
                pass # Missing this key, will find these later
        self.j2a=j2a
        print 'John --> Arjun'
        for key in self.j2a.keys():
            print '%s --> %s' % (key,self.j2a[key])
    
    def float_or_str(self):
        self.typ=dict(floats=[],ints=[],strs=[])
        for key in self.j2a.keys():
            typ= type(self.j.get(key)[0])
            if np.any((typ == np.float32,\
                       typ == np.float64),axis=0):
                self.typ['floats']+= [key]
            elif np.any((typ == np.int16,\
                         typ == np.int32),axis=0):
                self.typ['ints']+= [key]
            elif typ == np.string_:
                self.typ['strs']+= [key]
            else:
                print 'WARNING: unknown type for key=%s, ' % key,typ
    
    def print_set(self,text,s):
        print '%s\n' % text,np.sort(list(s))
        
    def compare_strings(self):
        print '----\nString comparison, John --> Arjun\n----'
        for s_key in self.typ['strs']:
            print '%s:%s --> %s:%s' % (s_key, self.j.get(s_key)[0],\
                                       self.j2a[s_key], self.a.get( self.j2a[s_key] )[0])
            

