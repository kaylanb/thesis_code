import numpy as np
import matplotlib.pyplot as plt
import pickle
import os


from astrometry.util.fits import fits_table

class Translator(object):
    def __init__(self,j,a,verbose=True):
        self.j=j
        self.a=a
        self.verbose=verbose
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
        if self.verbose:
            print '----\nmissing from Johns\n----'
            for key in j.get_columns():
                if key not in self.j2a.keys():
                    print '%s' % key
            vals=[v for k,v in self.j2a.items()]
            print '----\nmissing from Arjuns\n----'
            for key in a.get_columns():
                if key not in vals:
                    print '%s' % key
                
    def compare(self):
        # Comparisons
        self.compare_strings()
        self.compare_floats_ints()
            
        
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
        if self.verbose:
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
            
    def compare_floats_ints(self):
        panels=len(self.typ['floats'])+len(self.typ['ints'])
        cols=3
        if panels % cols == 0:
            rows=panels/cols
        else:
            rows=panels/cols+1
        # print cols,rows
        fig,axes= plt.subplots(rows,cols,figsize=(20,30))
        ax=axes.flatten()
        plt.subplots_adjust(hspace=0.4,wspace=0.3)
        cnt=-1
        for key in self.typ['floats']+self.typ['ints']:
            cnt+=1
            arjun= self.a.get( self.j2a[key] )
            john= self.j.get(key)
            #if key in ['transp','raoff','decoff','rarms','decrms',\
            #           'phrms','phoff','skyrms','skycounts',\
            #           'nstar','nmatch','width','height','mdncol']:
            ax[cnt].scatter(john,arjun) 
            ylab=ax[cnt].set_ylabel('Arjun',fontsize='small')
            #y= (arjun-john)/john
            #ax[cnt].scatter(john,y) 
            #ylab=ax[cnt].set_ylabel('(Arjun-John)/John',fontsize='small')
            #ax[cnt].set_ylim([-0.1,0.1])
            xlab=ax[cnt].set_xlabel('%s (John)' % key,fontsize='small')
        # plt.savefig("test.png",\
        #             bbox_extra_artists=[xlab,ylab], bbox_inches='tight',dpi=150)
         
    def save(self,savefn='translate.pickle'):
        if hasattr(self,'j2a'):
            self.savefn= savefn
            fout=open(self.savefn,'w')
            pickle.dump(self.j2a,fout)
            fout.close()
            print('Wrote %s' % self.savefn)
        else: 
            raise ValueError('not translation dictionary: self.j2a')
    
    def restore(self):
        if hasattr(self,'savefn'):
            fin=open(fn,'r')
            my_dict= pickle.load(fin)
            fin.close()
            return my_dict
        else: 
            raise ValueError('file has not been written to be restored')
    

class Converter(object):
    def __init__(self):
        self.indir='/global/homes/k/kaylanb/repos/thesis_code/zeropoints/data/original'
        # Build translation with existing data
        j= fits_table(os.path.join(self.indir,'zeropoint-k4m_160203_015632_ooi_zd_v2.fits'))
        a= fits_table(os.path.join(self.indir,'arjun_zeropoint-k4m_160203_015632_ooi_zd_v2.fits'))
        self.trans=Translator(j,a,verbose=False)
        # Apply translation to a big zpt file from John
        # Convert it to something that matches Arjuns
        
    def convert_j2a(self,j,key):
        if key in ['skycounts','skyrms']:
            return j.get(key)/j.get('exptime')
        elif key in ['skymag']:
            return j.get(key)-2.5*np.log10(j.get('gain'))
        else:
            return j.get(key)

    def rename_john_zptfile(self,fn=None):
        assert(fn is not None)
#         mydir='/global/homes/k/kaylanb/repos/thesis_code/zeropoints/data'
#         fn= os.path.join(mydir,'zeropoint-k4m_160203_015632_ooi_zd_v2.fits')
        j= fits_table(fn)
        jcopy= fits_table(fn)
        # Remove johns keys
        for key in self.trans.j2a.keys():
            j.delete_column(key)
        # Replace with arjun's keys, but John's data for that key
        for key in self.trans.j2a.keys():
            j.set(self.trans.j2a[key], jcopy.get(key))
        # Convert quantities to Arjuns based on empirical corrections 
        for key in ['skycounts','skyrms','skymag']:
            print('BEFORE: key=%s,j.get(key)[:4]=' % self.trans.j2a[key],j.get(self.trans.j2a[key])[:4])
            j.set(self.trans.j2a[key], self.convert_j2a(jcopy,key))
            print('AFTERE: key=%s,j.get(key)[:4]=' % self.trans.j2a[key],j.get(self.trans.j2a[key])[:4])
        # Save
        name= fn.replace('.fits','_renamed.fits')
        if os.path.exists(name):
            os.remove(name)
        j.writeto(name)
        print('Wrote renamed file: %s' % name)
    
    def compare_problematic(self):
        # Assumes j results from self.rename_john_zptfile() 
        j=fits_table('/project/projectdirs/desi/users/burleigh/test_data/old/john_combined_renamed.fits')
        a=fits_table('/project/projectdirs/desi/users/burleigh/test_data/old/arjun_combined.fits')
        # Compare
        discrep_keys=['zpt','zptavg',\
                  'skycounts','skyrms','skymag',\
                  'transp','phoff','rarms','decrms','raoff','decoff']
               
        panels=len(discrep_keys)
        cols=3
        if panels % cols == 0:
            rows=panels/cols
        else:
            rows=panels/cols+1
        fig,axes= plt.subplots(rows,cols,figsize=(20,10))
        ax=axes.flatten()
        plt.subplots_adjust(hspace=0.4,wspace=0.3)
        cnt=-1
        for key in discrep_keys:
            cnt+=1
            arjun= a.get( self.trans.j2a[key] )
            john= j.get( self.trans.j2a[key] )
            if key == 'skymag':
                arjun=arjun[ j.get('exptime') > 50]
                john=john[ j.get('exptime') > 50]
            ax[cnt].scatter(john,arjun)
            ylab=ax[cnt].set_ylabel('Arjun',fontsize='large')
            xlab=ax[cnt].set_xlabel('%s (John)' % key,fontsize='large')
       
        
if __name__ == '__main__':
    c= TRANS.Converter()
    c.trans.compare()
    c.rename_john_zptfile(fn='/project/projectdirs/desi/users/burleigh/test_data/old/john_combined.fits')
    # python translate.py johns_ccds_file.fits 
#     import sys
#     fn_torename= sys.argv[1]
#     mydir='/global/homes/k/kaylanb/repos/thesis_code/zeropoints/data'
#     john= fits_table(os.path.join(mydir,'zeropoint-k4m_160203_015632_ooi_zd_v2.fits'))
#     arjun= fits_table(os.path.join(mydir,'arjun_zeropoint-k4m_160203_015632_ooi_zd_v2.fits'))
#     t=Translator(john,arjun)
#     t.save(savefn='translate.pickle')
#     t.rename_john_zptfile(fn= sys.argv[1])
