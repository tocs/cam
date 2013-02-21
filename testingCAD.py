import sys
from simpleDXFlib import *

filename = "NONAME_0.dxf"

dxf = DXF()
dxf.open(filename) 

print "filename:", dxf.filename
print

print "ENTITIES:"
for e in dxf.ENTITIES.data:
    ent = e.get()
    print ent["type"]
    print "\t", ent
    print

