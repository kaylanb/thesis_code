from astrometry.util.fits import fits_table, merge_tables
from glob import glob

from theValidator.catalogues import CatalogueFuncs

fns=glob('/global/cscratch1/sd/rthomas/kaylan/celeste-*.fits')
a= CatalogueFuncs().stack(fns,textfile=False)
print("Number of unique thingids=%d" % (len(set(a.thingid)),) )
