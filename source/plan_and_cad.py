"""Generate the measured plan, area checks and a FreeCAD architectural shell."""
import sys,math,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from house_spec import *
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch, Rectangle, Arc, Circle

for sub in ['drawings','model','checks']:(ROOT/sub).mkdir(exist_ok=True)
fp=Polygon(FOOTPRINT);slabs=unary_union([Polygon([(a,b),(c,b),(c,d),(a,d)]) for a,b,c,d in SLABS])
assert abs(fp.area-325.4)<.0001 and fp.symmetric_difference(slabs).area<.0001
assert len([r for r in ROOMS if r['kind']=='bedroom'])==3
assert len([r for r in ROOMS if r['kind']=='bath'])==3
for w in WALLS:
    length=math.dist(w['a'],w['b']);previous=-1
    for a,b,s,h,k in sorted(w['openings']):
        assert a>=0 and b<=length and b>a and a>=previous and h>s
        previous=b
roomareas=[]
for r in ROOMS:
    poly=Polygon(r['poly']);assert poly.difference(fp).area<.0001
    roomareas.append({'name':r['name'],'clear_zone_m2':poly.area,'clear_zone_sqft':poly.area*FT2_PER_M2})
for i,r in enumerate(ROOMS):
    for other in ROOMS[i+1:]:assert Polygon(r['poly']).intersection(Polygon(other['poly'])).area<.0001,(r['name'],other['name'])

# Check the room connectivity through physical door openings and open-plan links.
graph={r['name']:set() for r in ROOMS}
def room_at(x,y):
    for r in ROOMS:
        if Polygon(r['poly']).buffer(.015).contains(Point(x,y)):return r['name']
for w in WALLS:
    ax,ay=w['a'];bx,by=w['b'];le=math.dist(w['a'],w['b']);ux,uy=(bx-ax)/le,(by-ay)/le
    for a,b,s,h,kind in w['openings']:
        if kind not in ['door','entry']:continue
        x=ax+ux*(a+b)/2;y=ay+uy*(a+b)/2
        r1=room_at(x-uy*.4,y+ux*.4);r2=room_at(x+uy*.4,y-ux*.4)
        if r1 and r2:graph[r1].add(r2);graph[r2].add(r1)
for a,b in [('ENTRY GALLERY','LIVING'),('LIVING','DINING'),('DINING','KITCHEN'),('DINING','FAMILY GALLERY'),('KITCHEN','FAMILY GALLERY')]:graph[a].add(b);graph[b].add(a)
seen=set();todo=['ENTRY GALLERY']
while todo:
    n=todo.pop()
    if n in seen:continue
    seen.add(n);todo.extend(graph[n]-seen)
assert len(seen)==len(ROOMS),set(graph)-seen
checks={'gross_enclosed_m2':fp.area,'gross_enclosed_sqft':fp.area*FT2_PER_M2,'area_basis':'Outside face of nominal exterior wall envelope. Courtyard, patios, landscape and roof overhangs excluded. Decorative stone relief excluded.',
        'bedroom_count':3,'bathroom_count':3,'office_count':1,'room_zones_nonoverlapping':True,'all_room_zones_inside_envelope':True,'all_room_zones_reachable_from_entry':True,
        'room_access_graph':{k:sorted(v) for k,v in graph.items()},'rooms':roomareas,'status':'Concept geometry only; circulation graph is not a building-code or accessibility review.'}
(ROOT/'checks'/'plan_checks.json').write_text(json.dumps(checks,indent=2))

fig,ax=plt.subplots(figsize=(17,11),facecolor='#f7f4ed');ax.set_facecolor('#f7f4ed');ax.set_aspect('equal');ax.set_xlim(-3.3,32);ax.set_ylim(-6.0,18.5);ax.axis('off')
ax.add_patch(Patch(FOOTPRINT,facecolor='#eee9dc',edgecolor='#514b40',lw=1.0))
palette={'bedroom':'#e4ddcd','bath':'#dae5e2','office':'#e4e0d2','living':'#eee4d2','kitchen':'#e7dcc7','service':'#e1e0d8','closet':'#e1ddd2','circulation':'#f0ece3'}
for r in ROOMS:ax.add_patch(Patch(r['poly'],facecolor=palette[r['kind']],edgecolor='none'))
ax.add_patch(Patch([(7.85,-1.5),(12,-2),(20,-1.22),(20,1),(21.2,1),(21.2,8),(7.85,8)],facecolor='#e4d7c0',edgecolor='#b9aa91',lw=.7))
ax.add_patch(Patch([(20,-2),(29.7,-2.8),(30.1,1),(20,1)],facecolor='#e4d7c0',edgecolor='#b9aa91',lw=.7))
for i in range(7):ax.add_patch(Rectangle((13.35,-2.19-i*.36),3.3,.38,facecolor='#e4d7c0',edgecolor='#b9aa91',lw=.5))
for r in ROOFS:ax.add_patch(Patch(r['poly'],fill=False,edgecolor='#aa9276',lw=.7,ls=(0,(6,4))))

def rect(x,y,w,d,fc='#b9aa91',ec='#786b58',lw=.5,angle=0):
    p=Rectangle((x-w/2,y-d/2),w,d,facecolor=fc,edgecolor=ec,lw=lw)
    if angle:
        import matplotlib.transforms as transforms
        p.set_transform(transforms.Affine2D().rotate_deg_around(x,y,angle)+ax.transData)
    ax.add_patch(p)
for w in WALLS:
    a=w['a'];b=w['b'];le=math.dist(a,b);ux,uy=(b[0]-a[0])/le,(b[1]-a[1])/le;angle=math.degrees(math.atan2(uy,ux));width=w['thick']
    for s,e,lo,hi in wall_solids(w):
        # Cut at 1.15 m so door and tall window openings remain legible.
        if not lo<=1.15<=hi:continue
        rect(a[0]+ux*(s+e)/2,a[1]+uy*(s+e)/2,e-s,width,'#605848' if w['mat']=='stone' else '#837b6b','#514b40',.35,angle)
    for s,e,lo,hi,kind in w['openings']:
        p=(a[0]+ux*s,a[1]+uy*s);q=(a[0]+ux*e,a[1]+uy*e)
        if kind in ['window','slider']:
            ax.plot([p[0],q[0]],[p[1],q[1]],color='#5b959a',lw=1.2)
            for offset in [-.035,.035]:ax.plot([p[0]-uy*offset,q[0]-uy*offset],[p[1]+ux*offset,q[1]+ux*offset],color='#5b959a',lw=.35)
        else:
            swing=-68 if kind=='entry' else 68;endang=math.radians(angle+swing)
            ax.plot([p[0],p[0]+math.cos(endang)*(e-s)],[p[1],p[1]+math.sin(endang)*(e-s)],color='#876b47',lw=.7)
            ax.add_patch(Arc(p,2*(e-s),2*(e-s),theta1=min(angle,angle+swing),theta2=max(angle,angle+swing),color='#ad9778',lw=.5))

# Furniture is schematic in the plan, but positions match the 3D model.
for x,y,w,d,sign in [(23.05,4.6,1.95,2.15,1),(2.1,2.55,1.55,2.05,-1),(6.15,4.8,1.65,2.05,1)]:
    rect(x,y,w+.18,d+.18);rect(x,y,w,d,'#f9f5ec');rect(x,y-sign*.4,w,d*.4,'#a6aa8a')
    for dx in [-w*.25,w*.25]:rect(x+dx,y+sign*d*.31,w*.42,.4,'#fffdf7')
    for dx in [-w/2-.42,w/2+.42]:rect(x+dx,y+sign*(d/2-.12),.54,.55)
rect(11.2,12.05,4.4,4.6,'#e2d6bf','#ccbfa8',.4)
rect(13.0,12.1,1.0,3.25,'#d3c6ad');rect(11.2,12.1,1.15,1.85)
rect(9.0,12.8,.95,3.1,'#b7aa94');rect(8.73,12.8,.22,1.8,'#393832')
for x,y in [(10.3,10.5),(10.25,14)]:rect(x,y,.60,.65,'#b18b5f')
rect(16,9.85,3.05,1.05)
for x in [15,16,17]:rect(x,8.98,.48,.48,'#e9e1cf');rect(x,10.72,.48,.48,'#e9e1cf')
for x in [14.1,17.9]:rect(x,9.85,.48,.48,'#e9e1cf')
rect(18.2,14.3,6.8,.64);rect(20.05,11.9,3.94,1.26,'#ddd9cc')
rect(19.12,11.97,.73,.47,'#95ada9');rect(17.5,14.24,.9,.5,'#383a36')
for x in [22.2,23.05]:rect(x,14.21,.82,.75,'#a38c6b')
for x in [18.65,19.58,20.51,21.44]:ax.add_patch(Circle((x,10.96),.22,facecolor='#b1a083',edgecolor='#756950',lw=.5))
rect(2.55,12.05,2.30,.86);rect(2.55,12.82,.5,.5,'#9aa07b');rect(2.6,14.38,4.2,.45)
for x,y,w in [(27.2,5.04,1.8),(1.05,7.52,1.2),(6.55,14.32,2.15)]:
    rect(x,y,w,.52);ax.add_patch(Circle((x,y),.20,facecolor='#f6f5ed',edgecolor='#8e9b96',lw=.6))
for x,y,w,d in [(27.85,2,1.35,1.45),(1.06,5.87,1.3,1.27),(7.33,11.31,1.35,1.25)]:
    rect(x,y,w,d,'#cadbd6','#648f91');ax.plot([x-w/2,x+w/2],[y-d/2,y+d/2],color='#99b7b4',lw=.45)
for x,y in [(26.45,2),(2.27,7.16),(5.68,13.65)]:
    rect(x,y+.18,.38,.18,'#fffdf6');ax.add_patch(Circle((x,y-.08),.22,facecolor='#fffdf6',edgecolor='#89998f',lw=.5))
rect(27.25,3.30,1.75,.80,'#f6f5ed','#819994',.7)
for x in [26.28,28.2]:rect(x,6.7,.60,2.0)
rect(1.6,4.64,2.2,.55);rect(5.05,7.45,1.35,.6)
rect(25.18,14.28,1.95,.6);rect(27.5,14.27,1.95,.65)
rect(11.5,2.6,3.1,2.25,'#c8bfae');rect(11.5,2.6,2.8,1.97,'#82aaa9')
rect(17.4,4.6,2.7,.88,'#d1c2a5');rect(17.4,3.25,1.3,.72);rect(16.3,2.5,.6,.6,'#e9e1cf');rect(18.4,2.5,.6,.6,'#e9e1cf')

for r in ROOMS:
    label=r['name'].replace('PRIMARY BEDROOM','PRIMARY\nBEDROOM').replace('PRIMARY BATH','PRIMARY\nBATH').replace('WALK-IN CLOSET','WALK-IN\nCLOSET').replace('BATH 2 / ENSUITE','BATH 2\nENSUITE')
    ax.text(*r['label'],label,ha='center',va='center',fontsize=7.0 if r['kind'] in ['bath','closet','service'] else 8.5,color='#373d36',fontweight='medium',bbox=dict(boxstyle='round,pad=.19',facecolor=palette[r['kind']],edgecolor='none',alpha=.94))
ax.text(15,6.3,'SHADED COURTYARD',ha='center',fontsize=9,color='#776345')
ax.text(11.5,2.6,'REFLECTING\nPOOL',ha='center',va='center',fontsize=6.5,color='#315756')
ax.text(24.9,-1.05,'PRIMARY TERRACE',ha='center',fontsize=8,color='#776345')
ax.annotate('ENTRY',xy=(.1,9.4),xytext=(-2,9.8),fontsize=8,color='#795b35',arrowprops=dict(arrowstyle='->',lw=.8,color='#795b35'))

# Overall dimension lines and north arrow.
ax.annotate('',xy=(0,16.65),xytext=(29,16.65),arrowprops=dict(arrowstyle='|-|',lw=.65,color='#84765f'))
ax.text(14.5,16.78,"29.00 m  /  95′ 2″",ha='center',fontsize=8,color='#655c4c')
ax.annotate('',xy=(30.7,.8),xytext=(30.7,15),arrowprops=dict(arrowstyle='|-|',lw=.65,color='#84765f'))
ax.text(31.04,7.9,"14.20 m  /  46′ 7″",ha='center',va='center',rotation=90,fontsize=8,color='#655c4c')
ax.annotate('N*',xy=(30.6,15.9),xytext=(29.8,16.7),ha='center',fontsize=10,color='#314b4b',arrowprops=dict(arrowstyle='-|>',lw=1,color='#314b4b'))
ax.text(-.1,18.0,'LAKOTAH HOUSE',fontsize=23,fontweight='light',color='#343d36')
ax.text(14.6,18.08,'3 BED  /  3 BATH  /  OFFICE',fontsize=10,color='#826b4a')
ax.text(14.6,17.60,'3,503 SQ FT  ·  325.4 M² ENCLOSED',fontsize=9,color='#826b4a')
ax.text(0,-5.05,'CONCEPT FLOOR PLAN',fontsize=10,color='#343d36')
ax.text(0,-5.55,'Area measured to nominal exterior faces. Dashed line = roof overhang. Terraces and courtyard excluded.',fontsize=8,color='#766d5d')
ax.text(29,-5.55,'* Orientation proposed · no site survey supplied',fontsize=8,ha='right',color='#766d5d')
plt.subplots_adjust(left=.02,right=.98,top=.98,bottom=.02)
fig.savefig(ROOT/'drawings'/'LAKOTAH_floor_plan.png',dpi=180,facecolor=fig.get_facecolor())
fig.savefig(ROOT/'drawings'/'LAKOTAH_floor_plan.svg',facecolor=fig.get_facecolor())
plt.close(fig)

# FreeCAD shell: simple named solids, measured in millimeters.
sys.path.insert(0,'/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App,Part
V=App.Vector
doc=App.newDocument('Lakotah_Architectural_Shell');shell=[];roofs=[]
def add(name,shape,roof=False):
    ob=doc.addObject('PartDesign::Feature',name.replace(' ','_'));ob.Label=name;ob.Shape=shape
    ob.addProperty('App::PropertyString','Scope');ob.Scope='Architectural concept shell; dimensions in mm.'
    assert shape.isValid()
    (roofs if roof else shell).append(ob);return ob
for i,(x0,y0,x1,y1) in enumerate(SLABS):
    add('Schematic stone plinth '+str(i),Part.makeBox((x1-x0)*1000,(y1-y0)*1000,2180,V(x0*1000,y0*1000,-2300)))
for i,(x0,y0,x1,y1) in enumerate(SLABS):add('Floor slab '+str(i+1),Part.makeBox((x1-x0)*1000,(y1-y0)*1000,300,V(x0*1000,y0*1000,-120)))
for w in WALLS:
    ax,ay=w['a'];bx,by=w['b'];le=math.dist(w['a'],w['b']);ang=math.degrees(math.atan2(by-ay,bx-ax));shapes=[]
    for s,e,b,t in wall_solids(w):
        shape=Part.makeBox((e-s)*1000,w['thick']*1000,(t-b)*1000,V(s*1000,-w['thick']*500,(FLOOR+b)*1000))
        shape.rotate(V(),V(0,0,1),ang);shape.translate(V(ax*1000,ay*1000,0));shapes.append(shape)
    add(w['name'],Part.makeCompound(shapes))
for r in ROOFS:
    pts=[V(x*1000,y*1000,(r['z0']+r['slope']*(y-r['basey']))*1000) for x,y in r['poly']];pts.append(pts[0])
    sh=Part.Face(Part.makePolygon(pts)).extrude(V(0,0,160));add(r['name'],sh,True)
sheet=doc.addObject('Spreadsheet::Sheet','Concept_Dimensions')
for i,(k,v) in enumerate([('Gross enclosed area m2',325.4),('Gross enclosed area sqft',325.4*FT2_PER_M2),('Envelope width mm',29000),('Envelope depth mm',14200),('Bedrooms',3),('Baths',3),('Office',1)],1):sheet.set('A'+str(i),k);sheet.set('B'+str(i),str(v))
sheet.setColumnWidth('A',210);doc.recompute();doc.saveAs(str(ROOT/'model'/'LAKOTAH_shell.FCStd'))
Part.export(shell+roofs,str(ROOT/'model'/'LAKOTAH_shell.step'))
cut=App.newDocument('Lakotah_Shell_Cutaway')
for src in shell:
    ob=cut.addObject('PartDesign::Feature',src.Name);ob.Label=src.Label;ob.Shape=src.Shape.copy()
cut.recompute();cut.saveAs(str(ROOT/'model'/'LAKOTAH_shell_cutaway.FCStd'))
print('Plan, SVG, FreeCAD shell, STEP and checks complete.')
print(json.dumps({k:v for k,v in checks.items() if k not in ['rooms','room_access_graph']},indent=2))
