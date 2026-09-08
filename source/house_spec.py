"""Shared measured concept geometry, meters. Local +Y is the proposed uphill side; see site_spec.py for schematic orientation."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FT2_PER_M2=10.76391041671
FOOTPRINT=[(0,.8),(8.5,.8),(8.5,8),(20.5,8),(20.5,.8),(29,.8),(29,15),(0,15)]
SLABS=[(0,8,29,15),(0,.8,8.5,8),(20.5,.8,29,8)]
FLOOR=.18
WALL_TOP=3.02
EXT=.35
INT=.15
# Openings are distances measured along each wall, with sill and head above floor.
# (start, end, sill, head, type)
WALLS=[]
def wall(name,a,b,thick=.35,mat='stone',openings=()):
    WALLS.append(dict(name=name,a=a,b=b,thick=thick,mat=mat,openings=list(openings)))
wall('West facade',(0,.8),(0,15),openings=[(1.2,3.7,.65,2.55,'window'),(7.9,9.3,0,2.55,'entry'),(10.1,13.7,.65,2.55,'window')])
wall('North facade',(0,15),(29,15),openings=[(.8,4.5,.75,2.55,'window'),(5.8,7.7,1.75,2.55,'window'),(9.0,14.0,.8,2.55,'window'),(15.3,23.5,1.25,2.55,'window'),(24.5,25.7,1.65,2.45,'window'),(26.7,28.4,1.3,2.45,'window')])
wall('East facade',(29,.8),(29,15),openings=[(.9,3.7,1.6,2.5,'window'),(7.5,8.7,0,2.5,'door'),(11.1,13.5,1.2,2.5,'window')])
wall('Guest south facade',(0,.8),(8.5,.8),openings=[(.65,3.65,.25,2.65,'window'),(4.8,7.9,0,2.65,'slider')])
wall('Primary south facade',(20.5,.8),(29,.8),openings=[(.65,5.0,0,2.65,'slider'),(5.8,7.85,1.65,2.5,'window')])
wall('Guest courtyard facade',(8.5,.8),(8.5,8),openings=[(.6,6.55,0,2.65,'slider')])
wall('Primary courtyard facade',(20.5,.8),(20.5,8),openings=[(.6,6.55,0,2.65,'slider')])
wall('Great room courtyard',(8.5,8),(20.5,8),openings=[(.55,11.45,0,2.78,'slider')])
# Interior partition and circulation openings.
wall('Guest bedrooms divider',(4.25,.8),(4.25,8),.15,'plaster')
wall('Guest wing to gallery',(0,8),(8.5,8),.15,'plaster',[(3.05,4.05,0,2.4,'door'),(6.85,7.95,0,2.4,'door')])
wall('Bath two south',(0,5.05),(3.0,5.05),.15,'plaster')
wall('Bath two east',(3.0,5.05),(3.0,8),.15,'plaster',[(.2,1.1,0,2.4,'door')])
wall('Office south',(0,10.35),(5.05,10.35),.15,'plaster',[(3.65,4.75,0,2.4,'door')])
wall('Office bathroom divider',(5.05,10.35),(5.05,15),.15,'plaster')
wall('Bathroom three south',(5.05,10.35),(8.5,10.35),.15,'plaster',[(.25,1.3,0,2.4,'door')])
wall('Stone hearth spine',(8.5,10.35),(8.5,15),.35,'stone')
wall('Primary suite north',(20.5,8),(29,8),.15,'plaster',[(1.35,2.55,0,2.4,'door')])
wall('Primary bath bedroom divider',(25.8,.8),(25.8,8),.15,'plaster',[(3.15,4.15,0,2.4,'door'),(5.45,6.45,0,2.4,'door')])
wall('Primary bath closet divider',(25.8,5.45),(29,5.45),.15,'plaster')
wall('Service rooms south',(24,11),(29,11),.15,'plaster',[(.25,1.3,0,2.4,'door'),(2.95,4.05,0,2.4,'door')])
wall('Pantry west',(24,11),(24,15),.15,'plaster')
wall('Laundry pantry divider',(26.4,11),(26.4,15),.15,'plaster')

ROOMS=[
 dict(name='PRIMARY BEDROOM',poly=[(20.85,1.15),(25.7,1.15),(25.7,7.9),(20.85,7.9)],label=(23.2,2.0),kind='bedroom'),
 dict(name='PRIMARY BATH',poly=[(25.9,1.15),(28.65,1.15),(28.65,5.35),(25.9,5.35)],label=(27.2,3.8),kind='bath'),
 dict(name='WALK-IN CLOSET',poly=[(25.9,5.55),(28.65,5.55),(28.65,7.9),(25.9,7.9)],label=(27.2,6.75),kind='closet'),
 dict(name='BEDROOM 2',poly=[(.35,1.15),(4.15,1.15),(4.15,7.9),(3.1,7.9),(3.1,4.95),(.35,4.95)],label=(2.1,3.98),kind='bedroom'),
 dict(name='BATH 2 / ENSUITE',poly=[(.35,5.15),(2.9,5.15),(2.9,7.9),(.35,7.9)],label=(1.55,6.35),kind='bath'),
 dict(name='BEDROOM 3',poly=[(4.35,1.15),(8.15,1.15),(8.15,7.9),(4.35,7.9)],label=(6.25,2.0),kind='bedroom'),
 dict(name='OFFICE',poly=[(.35,10.45),(4.95,10.45),(4.95,14.65),(.35,14.65)],label=(2.6,11.1),kind='office'),
 dict(name='BATH 3',poly=[(5.15,10.45),(8.15,10.45),(8.15,14.65),(5.15,14.65)],label=(6.65,12.0),kind='bath'),
 dict(name='PANTRY',poly=[(24.1,11.1),(26.3,11.1),(26.3,14.65),(24.1,14.65)],label=(25.2,12.1),kind='service'),
 dict(name='LAUNDRY',poly=[(26.5,11.1),(28.65,11.1),(28.65,14.65),(26.5,14.65)],label=(27.55,12.1),kind='service'),
 dict(name='ENTRY GALLERY',poly=[(.35,8.1),(8.325,8.1),(8.325,10.25),(.35,10.25)],label=(4.1,9.1),kind='circulation'),
 dict(name='LIVING',poly=[(8.675,8.2),(14.0,8.2),(14.0,14.65),(8.675,14.65)],label=(11.15,9.0),kind='living'),
 dict(name='DINING',poly=[(14,8.2),(18.0,8.2),(18.0,11.1),(14,11.1)],label=(16.0,8.5),kind='living'),
 dict(name='KITCHEN',poly=[(14,11.1),(23.9,11.1),(23.9,14.65),(14,14.65)],label=(18.8,13.5),kind='kitchen'),
 dict(name='FAMILY GALLERY',poly=[(18.0,8.1),(28.65,8.1),(28.65,10.9),(18.0,10.9)],label=(23.5,9.3),kind='circulation')]

ROOFS=[
 dict(name='Great room floating roof',poly=[(7.7,6.35),(23.95,7.05),(24.0,16.0),(7.7,16.0)],z0=3.40,slope=.072,basey=6.35,main=True),
 dict(name='Office roof',poly=[(-.9,7.0),(8.6,7.0),(8.6,16.0),(-.9,16.0)],z0=3.30,slope=.014,basey=7,main=False),
 dict(name='Service roof',poly=[(23.85,7.2),(29.9,7.2),(29.9,15.9),(23.85,15.9)],z0=3.30,slope=.014,basey=7.2,main=False),
 dict(name='Guest pavilion roof',poly=[(-.8,-.2),(9.15,.15),(9.15,8.25),(-.8,8.25)],z0=3.19,slope=.022,basey=0,main=False),
 dict(name='Primary pavilion roof',poly=[(19.75,.15),(29.9,-.2),(29.9,8.25),(19.75,8.25)],z0=3.19,slope=.022,basey=0,main=False)]

# Exterior dimensions refer to the outside face, not wall centerlines.
for w,(dx,dy) in zip(WALLS[:8],[(.175,0),(0,-.175),(-.175,0),(0,.175),(0,.175),(-.175,0),(.175,0),(0,.175)]):
    w['a']=(w['a'][0]+dx,w['a'][1]+dy);w['b']=(w['b'][0]+dx,w['b'][1]+dy)
    w['exterior']=True

def wall_solids(w):
    """Non-overlapping solid rectangles in wall-local coordinates."""
    import math
    length=math.dist(w['a'],w['b']);segments=[];last=0
    for start,end,sill,head,kind in sorted(w['openings']):
        if start>last:segments.append((last,start,0,WALL_TOP-FLOOR))
        if sill>0:segments.append((start,end,0,sill))
        if head<WALL_TOP-FLOOR:segments.append((start,end,head,WALL_TOP-FLOOR))
        last=end
    if last<length:segments.append((last,length,0,WALL_TOP-FLOOR))
    return segments
