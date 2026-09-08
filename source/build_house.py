"""LAKOTAH HOUSE — original architectural concept modeled in Blender.
All positions in meters. Run with Blender --background --python this_file.
"""
import bpy,bmesh,math,random,json,sys,contextlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from house_spec import *
random.seed(41)
for folder in ['model','renders','drawings','checks','print_model']:(ROOT/folder).mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC'
COL={}
for name in ['01 Architecture','02 Roofs','03 Glass and doors','04 Furniture','05 Landscape','06 Lights','07 Cameras']:
    c=bpy.data.collections.new(name);scene.collection.children.link(c);COL[name]=c
def move(ob,group):
    for c in list(ob.users_collection):c.objects.unlink(ob)
    COL[group].objects.link(ob)
    return ob
def mat(name,col,rough=.6,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    return m
def texture(m,scale,strength=.08,wood=False):
    nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');geo=nt.nodes.new('ShaderNodeNewGeometry');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3
    if wood:
        v=nt.nodes.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=(.32,12,2.5);nt.links.new(geo.outputs['Position'],v.inputs[0]);nt.links.new(v.outputs[0],noise.inputs['Vector'])
    else:nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
    ramp=nt.nodes.new('ShaderNodeValToRGB');c=m.diffuse_color[:3]
    ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*[v*.55 for v in c],1)
    ramp.color_ramp.elements[1].position=.82;ramp.color_ramp.elements[1].color=(*[min(1,v*1.22) for v in c],1)
    nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=.03 if not wood else .006
    nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
    return m
M={}
M['stonebase']=texture(mat('Foothill stone | mineral binder',(.19,.18,.15)),5,.2)
M['stone']=[texture(mat('Local angular stone '+str(i),c),7,.23) for i,c in enumerate([(.20,.19,.16),(.28,.25,.19),(.13,.14,.13),(.32,.29,.22),(.21,.18,.14),(.27,.20,.14),(.34,.32,.27)])]
M['plaster']=texture(mat('Lime plaster | warm ivory',(.72,.69,.61)),4,.025)
M['concrete']=texture(mat('Honed warm concrete',(.50,.46,.39)),3,.05)
M['paving']=texture(mat('Foothill stone terrace',(.55,.47,.37)),2,.08)
M['wood']=texture(mat('Walnut cabinetry',(.24,.105,.042),.38),2,.08,True)
M['cedar']=texture(mat('Redwood roof structure',(.29,.095,.037),.5),1.5,.08,True)
M['roof']=texture(mat('Warm gray standing-seam roof',(.18,.20,.19)),4,.02)
M['bronze']=mat('Dark bronze metal',(.065,.048,.032),.3,.72)
M['red']=mat('Earth red accents',(.24,.048,.022),.5)
M['stonecounter']=texture(mat('Honed pale limestone countertop',(.73,.72,.66),.24),1.7,.015)
M['black']=mat('Appliance graphite',(.022,.025,.026),.27,.55)
M['chrome']=mat('Brushed nickel',(.48,.50,.51),.22,.88)
M['linen']=texture(mat('Natural linen upholstery',(.70,.64,.52),.87),75,.07)
M['olive']=texture(mat('Olive upholstery',(.17,.20,.12),.8),60,.06)
M['leather']=mat('Cognac leather',(.32,.115,.044),.43)
M['white']=mat('Porcelain',(.84,.85,.81),.21)
M['rug']=texture(mat('Flatweave sand rug',(.48,.39,.27),.95),65,.12)
M['soil']=texture(mat('Dry oak woodland ground',(.28,.255,.145),.95),1.5,.2)
M['leaf']=mat('Oak foliage',(.10,.17,.045),.95)
M['agave']=mat('Meadow grass',(.33,.32,.13),.75)
M['trunk']=texture(mat('Oak bark',(.12,.09,.058),.8),4,.2)
M['glass']=mat('Clear architectural glazing',(.91,.96,.95),.035)
M['glass'].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=1
M['glass'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.46
M['water']=mat('Reflecting water',(.055,.16,.16),.055,.12)
M['water'].node_tree.nodes.get('Principled BSDF').inputs['Transmission Weight'].default_value=.6
M['water'].node_tree.nodes.get('Principled BSDF').inputs['IOR'].default_value=1.333
M['glow']=mat('Warm luminous diffuser',(.95,.70,.36),.45)
bs=M['glow'].node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=(1,.63,.28,1);bs.inputs['Emission Strength'].default_value=2.2

def finish(ob,name,material,group='01 Architecture',bevel=0):
    ob.name=name;move(ob,group)
    if material:ob.data.materials.append(material)
    if bevel:
        mod=ob.modifiers.new('Edge softness','BEVEL');mod.width=bevel;mod.segments=2
        mod=ob.modifiers.new('Face normals','WEIGHTED_NORMAL');mod.keep_sharp=True
    return ob
def box(name,loc,dims,material,group='01 Architecture',bevel=0,rot=0):
    x,y,z=[v/2 for v in dims]
    me=bpy.data.meshes.new(name);me.from_pydata([(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)],[],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]);me.update()
    ob=bpy.data.objects.new(name,me);COL[group].objects.link(ob);ob.location=loc;ob.rotation_euler.z=rot
    return finish(ob,name,material,group,bevel)
def cyl(name,loc,r,depth,material,group='04 Furniture',vertices=32):
    n=vertices;verts=[(r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for z in [-depth/2,depth/2] for i in range(n)]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);COL[group].objects.link(ob);ob.location=loc
    ob=finish(ob,name,material,group,.007)
    for p in ob.data.polygons:p.use_smooth=True
    return ob
SPHERES={}
def sphere(name,loc,scale,material,group='04 Furniture',sub=2):
    if sub not in SPHERES:
        bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=1);me=bpy.data.meshes.new('Icosphere');bm.to_mesh(me);bm.free();SPHERES[sub]=me
    ob=bpy.data.objects.new(name,SPHERES[sub].copy());COL[group].objects.link(ob);ob.location=loc;ob.scale=scale
    for p in ob.data.polygons:p.use_smooth=True
    return finish(ob,name,material,group)
def beam(name,a,b,width,depth,material,group='02 Roofs'):
    a,b=Vector(a),Vector(b);ob=box(name,(a+b)/2,(width,depth,(b-a).length),material,group,.008)
    ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return ob
def prism(name,poly,low,high,material,group='01 Architecture'):
    n=len(poly);verts=[(x,y,low(x,y) if callable(low) else low) for x,y in poly]+[(x,y,high(x,y) if callable(high) else high) for x,y in poly]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(name,mesh);COL[group].objects.link(ob);ob.data.materials.append(material);return ob

# Main enclosed floor plates and shaded outdoor courtyard.
for i,(x0,y0,x1,y1) in enumerate(SLABS):
    box('Stone hillside plinth '+str(i),((x0+x1)/2,(y0+y1)/2,-1.21),(x1-x0,y1-y0,2.18),M['stonebase'])
    box('Enclosed slab '+str(i+1),((x0+x1)/2,(y0+y1)/2,.03),(x1-x0,y1-y0,.30),M['concrete'])
    box('Honed interior floor '+str(i+1),((x0+x1)/2,(y0+y1)/2,.191),(x1-x0-.04,y1-y0-.04,.022),M['concrete'])
terracepoly=[(7.85,-1.5),(12,-2.0),(20.0,-1.22),(20.0,1.0),(21.2,1.0),(21.2,8.0),(7.85,8.0)]
prism('Courtyard stone terrace',terracepoly,-2.3,.14,M['paving'])
prism('Primary private terrace',[(20.0,-2.0),(29.7,-2.8),(30.1,1.0),(20.0,1.0)],-2.3,.14,M['paving'])
prism('Entry approach', [(-8.0,7.4),(.4,8.8),(.4,10.5),(-8.0,9.1)],-.16,.14,M['paving'])
# Subtle paving joints.
for x in [9.5,11.5,13.5,15.5,17.5,19.5]:box('Terrace control joint',(x,3.5,.141),(.016,8.9,.003),M['stonebase'])
for y in [0,2,4,6]:box('Terrace control joint',(14.65,y,.142),(13.0,.016,.003),M['stonebase'])

# Masonry front faces are actual angular stones, with individually varied colors.
stone_verts=[];stone_faces=[];stone_mats=[]
def add_stones(center,length,thick,height,angle):
    cx,cy,cz=center;ca,sa=math.cos(angle),math.sin(angle)
    rows=max(1,round(height/.34));rh=height/rows
    for side in [-1,1]:
        for row in range(rows):
            z0=cz-height/2+row*rh+.016;z1=cz-height/2+(row+1)*rh-.016
            count=max(1,round(length/random.uniform(.52,.78)));width=length/count
            for col in range(count):
                u0=-length/2+col*width+.018;u1=u0+width-.036
                if u1<=u0 or z1<=z0:continue
                jitter=min(.11,width*.14,rh*.28)
                poly=[(u0+random.uniform(0,jitter),z0),(u1-jitter*.2,z0+random.uniform(0,jitter)),(u1,z0+(z1-z0)*.54),(u1-random.uniform(0,jitter),z1),(u0+random.uniform(0,jitter),z1-random.uniform(0,jitter)),(u0,z0+(z1-z0)*.44)]
                depth=random.uniform(.018,.048);start=len(stone_verts)
                for offset in [side*(thick/2-.008),side*(thick/2+depth)]:
                    for u,z in poly:stone_verts.append((cx+ca*u-sa*offset,cy+sa*u+ca*offset,z))
                n=len(poly);faces=[tuple(start+i for i in reversed(range(n))),tuple(start+n+i for i in range(n))]+[(start+i,start+(i+1)%n,start+(i+1)%n+n,start+i+n) for i in range(n)]
                stone_faces.extend(faces);stone_mats.extend([random.randrange(len(M['stone']))]*len(faces))

for w in WALLS:
    ax,ay=w['a'];bx,by=w['b'];length=math.dist(w['a'],w['b']);ux,uy=(bx-ax)/length,(by-ay)/length;ang=math.atan2(uy,ux)
    def xy(d):return ax+ux*d,ay+uy*d
    for j,(s,e,b,t) in enumerate(wall_solids(w)):
        cx,cy=xy((s+e)/2);h=t-b
        box(w['name']+' solid '+str(j),(cx,cy,FLOOR+(b+t)/2),(e-s,w['thick'],h),M['stonebase'] if w['mat']=='stone' else M['plaster'],rot=ang)
        if w['mat']=='stone':add_stones((cx,cy,FLOOR+(b+t)/2),e-s,w['thick'],h,ang)
    for k,(s,e,sill,head,kind) in enumerate(w['openings']):
        cx,cy=xy((s+e)/2);width=e-s
        if kind in ['window','slider']:
            n=max(1,round(width/1.35))
            box(w['name']+' glazing '+str(k),(cx,cy,FLOOR+(sill+head)/2),(width-.07,.018,head-sill-.07),M['glass'],'03 Glass and doors',rot=ang)
            for j in range(n+1):
                px,py=xy(s+j*width/n)
                box('Bronze mullion',(px,py,FLOOR+(sill+head)/2),(.048,.078,head-sill+.05),M['bronze'],'03 Glass and doors',rot=ang)
            for z in [sill,head]:box('Bronze window rail',(cx,cy,FLOOR+z),(width+.05,.078,.055),M['bronze'],'03 Glass and doors',rot=ang)
        else:
            for d in [s,e]:
                px,py=xy(d);box('Walnut door jamb',(px,py,FLOOR+head/2),(.055,w['thick']+.025,head),M['wood'],'03 Glass and doors',rot=ang)
            box('Walnut door head',(cx,cy,FLOOR+head),(width,w['thick']+.025,.06),M['wood'],'03 Glass and doors',rot=ang)
            a=ang+math.radians(-68 if kind=='entry' else 68);hinge=xy(s+.02)
            ob=box(w['name']+' open door',(hinge[0]+math.cos(a)*(width-.05)/2,hinge[1]+math.sin(a)*(width-.05)/2,FLOOR+head/2),(width-.05,.045,head-.06),M['cedar'] if kind=='entry' else M['wood'],'03 Glass and doors',.012,a)
            pos=Vector(ob.location)+Vector((math.cos(a),math.sin(a),0))*(width/2-.15)
            cyl('Door pull',(pos.x,pos.y,FLOOR+1.05),.021,.15,M['bronze'],'03 Glass and doors')

# Stone veneer continues down the exposed hillside base.
for a,b in zip(FOOTPRINT,FOOTPRINT[1:]+FOOTPRINT[:1]):
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2);ang=math.atan2(b[1]-a[1],b[0]-a[0])
    add_stones((*mid,-1.02),math.dist(a,b),.025,1.8,ang)
for i in range(7):
    box('Garden stair '+str(i+1),(15,-2.0-i*.36,-1.9+(2.04-i*.18)/2),(3.3,.38,2.04-i*.18),M['paving'])

# Faced stone on downhill terrace retaining edges.
for a,b in [((7.85,-1.5),(12,-2)),((12,-2),(20,-1.22)),((20,-2),(29.7,-2.8)),((29.7,-2.8),(30.1,1))]:
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2);ang=math.atan2(b[1]-a[1],b[0]-a[0])
    add_stones((*mid,-1.08),math.dist(a,b),.02,2.36,ang)

# Low walls extend the building into its site, as at the inspiration campus.
for name,a,b,h in [('Arrival wall',(-7.0,10.0),(-.2,11.3),.85),('Courtyard low wall',(8.0,-1.5),(12.2,-2.0),.52),('Primary garden wall',(30.0,-2.8),(30.0,4.4),.75)]:
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2);le=math.dist(a,b);ang=math.atan2(b[1]-a[1],b[0]-a[0])
    box(name,(*mid,h/2-.1),(le,.38,h),M['stonebase'],rot=ang);add_stones((*mid,h/2-.1),le,.38,h,ang)
mesh=bpy.data.meshes.new('Foothill masonry individual stones');mesh.from_pydata(stone_verts,[],stone_faces);mesh.update()
ob=bpy.data.objects.new('Angular foothill stone / actual geometry',mesh);COL['01 Architecture'].objects.link(ob)
for m in M['stone']:ob.data.materials.append(m)
for p,i in zip(ob.data.polygons,stone_mats):p.material_index=i

# Independent pavilion roofs, redwood fascia and beams.
def roof_height(x,y):
    candidates=[]
    for r in ROOFS:
        inside=False;poly=r['poly'];j=len(poly)-1
        for i,(xi,yi) in enumerate(poly):
            xj,yj=poly[j]
            if ((yi>y)!=(yj>y)) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:inside=not inside
            j=i
        if inside:candidates.append(r['z0']+r['slope']*(y-r['basey']))
    return min(candidates) if candidates else 3.30
for w in WALLS:
    if w.get('exterior'):continue
    ax,ay=w['a'];bx,by=w['b'];le=math.dist(w['a'],w['b']);nx=-(by-ay)/le*w['thick']/2;ny=(bx-ax)/le*w['thick']/2
    poly=[(ax+nx,ay+ny),(bx+nx,by+ny),(bx-nx,by-ny),(ax-nx,ay-ny)]
    prism('Partition closure to roof',poly,WALL_TOP,roof_height,M['plaster'])
for r in ROOFS:
    z=lambda x,y,r=r:r['z0']+r['slope']*(y-r['basey'])
    prism(r['name'],r['poly'],z,lambda x,y:z(x,y)+.16,M['roof'],'02 Roofs')
    for i,p in enumerate(r['poly']):
        q=r['poly'][(i+1)%len(r['poly'])]
        beam('Redwood fascia',(*p,z(*p)+.025),(*q,z(*q)+.025),.15,.20,M['cedar'])
    xmin=min(x for x,y in r['poly']);xmax=max(x for x,y in r['poly']);ymin=min(y for x,y in r['poly']);ymax=max(y for x,y in r['poly'])
    n=math.ceil((xmax-xmin)/1.7)
    for i in range(1,n):
        x=xmin+(xmax-xmin)*i/n
        # The south edge on the great room roof is deliberately oblique.
        ys=r['poly'][0][1]+(r['poly'][1][1]-r['poly'][0][1])*(x-xmin)/(xmax-xmin)
        beam('Exposed redwood roof rib',(x,ys,z(x,ys)-.11),(x,ymax,z(x,ymax)-.11),.105,.25,M['cedar'])
    for i in range(1,math.ceil((xmax-xmin)/.52)):
        x=xmin+i*.52
        if x>=xmax:continue
        ys=r['poly'][0][1]+(r['poly'][1][1]-r['poly'][0][1])*(x-xmin)/(xmax-xmin)
        beam('Raised roof seam',(x,ys,z(x,ys)+.18),(x,ymax,z(x,ymax)+.18),.017,.026,M['roof'])
    # Ceiling boards on underside keep interiors warm; roofs hide for dollhouse.
    prism('Redwood ceiling plane',r['poly'],lambda x,y:z(x,y)-.035,z,M['wood'],'02 Roofs')

# Upper clear glazing closes the roof-to-wall gap, including angled clerestories.
for w in WALLS:
    if not w.get('exterior'):continue
    ax,ay=w['a'];bx,by=w['b'];length=math.dist(w['a'],w['b']);n=math.ceil(length/1.5)
    for j in range(n):
        a=Vector((ax+(bx-ax)*j/n,ay+(by-ay)*j/n,0));b=Vector((ax+(bx-ax)*(j+1)/n,ay+(by-ay)*(j+1)/n,0))
        za=roof_height(a.x,a.y);zb=roof_height(b.x,b.y)
        vs=[(a.x,a.y,WALL_TOP),(b.x,b.y,WALL_TOP),(b.x,b.y,zb),(a.x,a.y,za)]
        me=bpy.data.meshes.new('Clerestory');me.from_pydata(vs,[],[(0,1,2,3)]);me.update();ob=bpy.data.objects.new('Clerestory light ribbon',me);COL['03 Glass and doors'].objects.link(ob);ob.data.materials.append(M['glass'])
        beam('Clerestory frame',(a.x,a.y,WALL_TOP),(a.x,a.y,za),.045,.065,M['bronze'],'03 Glass and doors')
        beam('Clerestory cap',(a.x,a.y,za),(b.x,b.y,zb),.045,.065,M['bronze'],'03 Glass and doors')

# Furnishing helpers. Functional pieces have real dimensions and visible detail.
F='04 Furniture'
def legs(name,x,y,w,d,z=.21,h=.42,material=None):
    for dx in [-w/2+.09,w/2-.09]:
        for dy in [-d/2+.09,d/2-.09]:beam(name,(x+dx,y+dy,z),(x+dx*.94,y+dy*.94,z+h),.038,.038,material or M['wood'],F)
def chair(x,y,angle=0,material=None):
    root=bpy.data.objects.new('Mid-century chair',None);COL[F].objects.link(root)
    obs=[]
    obs.append(box('Chair upholstered seat',(0,0,.66),(.48,.48,.13),material or M['linen'],F,.055))
    obs.append(box('Chair curved back',(0,.20,.95),(.5,.09,.42),material or M['linen'],F,.035))
    for dx in [-.18,.18]:
        for dy in [-.18,.18]:obs.append(beam('Tapered chair leg',(dx*1.12,dy*1.12,.205),(dx,dy,.60),.035,.035,M['wood'],F))
    for ob in obs:ob.parent=root
    root.location=(x,y,0);root.rotation_euler.z=angle
def bed(name,x,y,w=1.8,d=2.1,flip=False):
    before=set(bpy.data.objects) if flip else None
    box(name+' walnut platform',(x,y,.43),(w+.18,d+.18,.32),M['wood'],F,.045)
    box(name+' linen mattress',(x,y,.66),(w,d,.28),M['linen'],F,.09)
    box(name+' low headboard',(x,y+d/2+.08,.83),(w+.44,.12,1.06),M['wood'],F,.025)
    box(name+' folded olive cover',(x,y-.38,.815),(w+.01,d*.46,.06),M['olive'],F,.025)
    for dx in [-w*.25,w*.25]:box(name+' pillow',(x+dx,y+d*.31,.86),(w*.44,.43,.17),M['white'],F,.075)
    for dx in [-w/2-.42,w/2+.42]:
        box('Floating bedside table',(x+dx,y+d/2-.12,.65),(.54,.55,.18),M['wood'],F,.025)
        cyl('Bedside lamp base',(x+dx,y+d/2-.12,.80),.075,.12,M['bronze'])
        sphere('Bedside opal lamp',(x+dx,y+d/2-.12,.96),(.13,.13,.14),M['glow'])
    if flip:
        for ob in set(bpy.data.objects)-before:
            ob.location.x=2*x-ob.location.x;ob.location.y=2*y-ob.location.y;ob.rotation_euler.z+=math.pi
def cabinet(name,x,y,w,d,h,front='south',base=.205,material=None):
    material=material or M['wood'];box(name+' cabinet',(x,y,base+h/2),(w,d,h),material,F,.01)
    n=max(1,round(w/.6))
    for i in range(n):
        xx=x-w/2+w*(i+.5)/n
        box(name+' door',(xx,y-d/2-.012,base+h/2),(w/n-.025,.024,h-.055),material,F,.006)
        box('Shadow-line handle',(xx,y-d/2-.029,base+h-.075),(w/n*.6,.022,.016),M['bronze'],F,.003)
def tap(x,y,z):
    beam('Faucet stem',(x,y,z),(x,y,z+.28),.027,.027,M['chrome'],F)
    beam('Faucet spout',(x,y,z+.28),(x,y-.18,z+.28),.028,.028,M['chrome'],F)
def vanity(name,x,y,w=1.4):
    cabinet(name,x,y,w,.52,.58,base=.42)
    box(name+' counter',(x,y,1.035),(w+.035,.56,.055),M['stonecounter'],F,.018)
    sphere(name+' basin',(x,y-.025,1.075),(.26,.19,.055),M['white'])
    tap(x,y+.17,1.065)
    box(name+' bronze framed mirror',(x,y+.29,1.70),(w-.08,.035,.80),M['bronze'],F,.02)
    box(name+' mirror',(x,y+.268,1.70),(w-.14,.009,.74),M['chrome'],F)
def toilet(x,y,rot=0):
    sphere('Toilet porcelain pedestal',(x,y,.41),(.18,.25,.21),M['white'])
    sphere('Toilet bowl',(x,y-.08,.62),(.22,.33,.115),M['white'])
    box('Toilet cistern',(x,y+.20,.76),(.38,.18,.62),M['white'],F,.055)
    cyl('Flush button',(x,y+.20,1.08),.023,.012,M['chrome'])
def shower(x,y,w=1.2,d=1.25):
    box('Shower tray',(x,y,.23),(w,d,.07),M['stonecounter'],F,.015)
    box('Shower fixed glass',(x-w/2,y,1.22),(.014,d,1.99),M['glass'],F)
    box('Shower glass door',(x,y-d/2,1.22),(w,.014,1.99),M['glass'],F)
    beam('Rain shower riser',(x,y+d/2-.08,1.10),(x,y+d/2-.08,2.30),.025,.025,M['chrome'],F)
    beam('Rain shower arm',(x,y+d/2-.08,2.30),(x,y+.05,2.30),.025,.025,M['chrome'],F)
    cyl('Rain shower head',(x,y+.05,2.28),.13,.018,M['chrome'])
def tub(x,y,angle=0):
    ob=box('Freestanding stone bath',(x,y,.50),(1.75,.80,.61),M['white'],F,.19,angle)
    box('Bath inner water',(x,y,.802),(1.44,.55,.015),M['water'],F,.15,angle)
    tap(x,y+.47,.70)

bed('Primary king bed',23.05,4.6,1.95,2.15)
bed('Bedroom two queen',2.1,2.55,1.55,2.05,flip=True)
bed('Bedroom three queen',6.15,4.8,1.65,2.05)
cabinet('Bedroom two wardrobe',1.6,4.64,2.2,.55,2.35)
cabinet('Bedroom three wardrobe',5.05,7.45,1.35,.60,2.35)
for x in [26.28,28.2]:box('Primary closet storage',(x,6.7,1.39),(.60,2.0,2.37),M['wood'],F,.012)
for x in [26.5,28.0]:beam('Closet hanging rail',(x,5.95,1.9),(x,7.4,1.9),.022,.022,M['bronze'],F)

# Three complete bathrooms, each with a toilet, basin, and shower.
vanity('Primary floating vanity',27.20,5.04,1.8);shower(27.85,2.0,1.35,1.45);toilet(26.45,2.0);tub(27.25,3.30)
vanity('Guest ensuite vanity',1.05,7.52,1.2);shower(1.06,5.87,1.30,1.27);toilet(2.27,7.16)
vanity('Hall bath double vanity',6.55,14.32,2.15);shower(7.33,11.31,1.35,1.25);toilet(5.68,13.65)

# Great room: stone hearth, walnut storage, linen sofa and lounge chairs.
box('Living flatweave rug',(11.2,12.05,.222),(4.4,4.6,.025),M['rug'],F,.02)
box('Cantilevered hearth',(9.0,12.8,.38),(.95,3.1,.34),M['stonecounter'],F,.025)
box('Dark recessed fireplace',(8.73,12.8,1.02),(.11,1.80,.65),M['black'],F)
for i in range(4):beam('Fireplace logs',(8.87,12.18+i*.3,.76),(8.93,12.42+i*.3,.81),.08,.10,M['wood'],F)
box('Walnut hearth mantle',(8.85,12.8,1.45),(.55,2.45,.13),M['wood'],F,.015)
box('Sofa low walnut frame',(13.0,12.1,.46),(1.0,3.25,.28),M['wood'],F,.035)
box('Sofa linen seat',(12.85,12.1,.67),(.93,3.12,.25),M['linen'],F,.09)
box('Sofa linen back',(13.34,12.1,1.00),(.24,3.2,.72),M['linen'],F,.08)
for y in [10.55,13.65]:box('Sofa arm',(12.90,y,.88),(1.02,.19,.53),M['linen'],F,.065)
for y in [11.15,12.0,12.85]:box('Linen sofa cushion',(13.07,y,1.04),(.20,.70,.42),M['linen'],F,.065)
box('Walnut coffee table',(11.2,12.1,.58),(1.15,1.85,.10),M['wood'],F,.08);legs('Coffee table leg',11.2,12.1,1.0,1.7,h=.32)
for x,y,a in [(10.3,10.5,-.25),(10.25,14.0,math.pi+.25)]:chair(x,y,a,M['leather'])
cyl('Ceramic coffee table bowl',(11.2,12.1,.68),.19,.07,M['stonecounter'])

# Dining table for eight, with slim walnut joinery.
box('Eight-person dining tabletop',(16.0,9.85,.99),(3.05,1.05,.075),M['wood'],F,.045);legs('Dining table legs',16,9.85,2.8,.85,h=.72)
for x in [15,16,17]:chair(x,8.98,math.pi);chair(x,10.72,0)
chair(14.1,9.85,math.pi/2);chair(17.9,9.85,-math.pi/2)

# Modern kitchen: a 12-foot island, integrated refrigerator, ovens and stone backsplash.
cabinet('Kitchen north run',18.2,14.30,6.8,.64,.86)
box('Kitchen continuous stone counter',(18.2,14.28,1.105),(6.85,.69,.075),M['stonecounter'],F,.012)
box('Kitchen limestone backsplash',(18.2,14.65,1.37),(6.85,.035,.48),M['stonecounter'],F)
cabinet('Island',20.05,11.9,3.8,1.12,.88)
box('Waterfall island top',(20.05,11.9,1.13),(3.94,1.26,.085),M['stonecounter'],F,.018)
for x in [18.12,21.98]:box('Island waterfall end',(x,11.9,.675),(.075,1.26,.84),M['stonecounter'],F,.014)
# Dark inset sink, visible rim, and a slender mixer.
box('Island undermount sink rim',(19.12,11.97,1.178),(.73,.47,.015),M['chrome'],F,.045)
box('Island dark sink basin',(19.12,11.97,1.185),(.65,.39,.015),M['black'],F,.04);tap(19.12,12.27,1.18)
box('Induction hob',(17.5,14.24,1.151),(.90,.50,.024),M['black'],F,.012)
for x in [17.28,17.72]:
    for y in [14.10,14.36]:cyl('Induction ring',(x,y,1.167),.095,.003,M['chrome'])
for x in [22.2,23.05]:
    cabinet('Integrated appliance tower',x,14.21,.82,.75,2.48)
    box('Integrated tall door',(x,13.81,1.43),(.77,.055,2.30),M['wood'],F,.009)
    box('Appliance tall pull',(x-.25,13.765,1.4),(.025,.025,.80),M['bronze'],F,.004)
for z in [1.0,1.64]:
    box('Built-in oven',(22.2,13.75,z),(.70,.075,.51),M['black'],F,.016)
    box('Oven glass',(22.2,13.70,z-.02),(.57,.014,.33),M['bronze'],F,.008)
    box('Oven handle',(22.2,13.66,z+.16),(.55,.04,.025),M['chrome'],F,.008)
for x in [18.65,19.58,20.51,21.44]:
    cyl('Counter stool walnut seat',(x,10.96,.96),.22,.08,M['wood'])
    for dx in [-.14,.14]:
        for dy in [-.14,.14]:beam('Stool leg',(x+dx*1.3,10.96+dy*1.3,.205),(x+dx,10.96+dy,.92),.032,.032,M['bronze'],F)
for x in [18.65,20.05,21.45]:
    beam('Pendant cable',(x,11.9,2.25),(x,11.9,3.62),.009,.009,M['bronze'],F)
    cyl('Kitchen pendant',(x,11.9,2.23),.14,.25,M['bronze']);cyl('Pendant diffuser',(x,11.9,2.10),.12,.012,M['glow'])
cabinet('Pantry shelving',25.18,14.28,1.95,.60,2.35)
for y in [12.0,12.7,13.4]:box('Pantry side shelf',(24.40,y,1.45),(.45,.68,.035),M['wood'],F)
cabinet('Laundry counter',27.5,14.27,1.95,.65,.9)
for x in [27.05,27.85]:
    box('Laundry appliance',(x,14.2,.67),(.67,.68,.88),M['white'],F,.025)
    ob=cyl('Washer circular front',(x,13.846,.65),.23,.025,M['black']);ob.rotation_euler.x=math.pi/2

# Office, books and a small reading nook.
box('Office walnut desk',(2.55,12.05,.985),(2.30,.86,.075),M['wood'],F,.025);legs('Desk legs',2.55,12.05,2.15,.72,h=.74)
chair(2.55,12.82,0,M['olive'])
box('Office monitor',(2.5,12.08,1.37),(.70,.055,.43),M['black'],F,.012)
beam('Monitor stand',(2.5,12.13,1.03),(2.5,12.13,1.22),.06,.05,M['bronze'],F)
box('Office keyboard',(2.5,12.40,1.04),(.42,.14,.012),M['black'],F,.008)
for z in [.43,.89,1.35,1.81,2.27]:
    box('Office library shelf',(2.6,14.38,z),(4.2,.45,.06),M['wood'],F)
    for i in range(20):
        x=.70+i*.193;h=random.uniform(.23,.36)
        box('Library book',(x,14.34,z+.04+h/2),(random.uniform(.05,.10),.23,h),random.choice([M['linen'],M['olive'],M['wood'],M['red']]),F,.002)
chair(21.4,9.4,-.5,M['leather']);cyl('Gallery side table',(22.15,9.35,.67),.32,.07,M['wood']);beam('Side table stem',(22.15,9.35,.2),(22.15,9.35,.64),.06,.06,M['bronze'],F)
chair(21.8,2.15,.3,M['leather'])

# Courtyard water and furniture.
box('Reflecting pool stone rim',(11.5,2.6,.27),(3.1,2.25,.26),M['stonecounter'],F,.045)
box('Reflecting pool dark interior',(11.5,2.6,.407),(2.82,1.97,.02),M['black'],F,.02)
box('Reflecting pool water',(11.5,2.6,.422),(2.77,1.92,.008),M['water'],F)
box('Outdoor sofa base',(17.4,4.6,.42),(2.7,.88,.25),M['wood'],F,.025)
box('Outdoor sofa cushions',(17.4,4.55,.63),(2.6,.79,.22),M['linen'],F,.07)
box('Outdoor sofa back',(17.4,4.94,.91),(2.7,.17,.60),M['linen'],F,.07)
box('Outdoor coffee table',(17.4,3.25,.55),(1.3,.72,.09),M['wood'],F,.03);legs('Outdoor table legs',17.4,3.25,1.15,.59,h=.31)
chair(16.3,2.5,math.pi+.2,M['linen']);chair(18.4,2.5,math.pi-.2,M['linen'])

# Schematic foothill topography: no surveyed elevations are available.
# Local +Y is the proposed uphill side; site_spec maps the building into the parcel sketch.
def terrain_z(x,y):
    natural=.105*(y-12)+.022*(x-14)+.22*math.sin(x*.11)*math.cos(y*.14)
    # Illustrative cut behind the single-level house. Retaining plinth fills the downhill side.
    if -9<x<33 and -3<y<20:natural=min(natural,-.19)
    return natural
verts=[];faces=[];n=101
for j in range(n):
    y=-130+j*3.2
    for i in range(n):
        x=-145+i*3.2;z=terrain_z(x,y)
        if y>35:z+=3*math.sin(x*.024+y*.017)+2*math.sin(y*.037)
        verts.append((x,y,z))
for j in range(n-1):
    for i in range(n-1):
        a=j*n+i;faces.append((a,a+1,a+n+1,a+n))
me=bpy.data.meshes.new('Illustrative hillside');me.from_pydata(verts,[],faces);me.update()
ob=bpy.data.objects.new('Schematic foothill terrain — not survey data',me);COL['05 Landscape'].objects.link(ob);ob.data.materials.append(M['soil'])
for poly in me.polygons:poly.use_smooth=True
leafmats=[M['leaf'],mat('Oak leaf sunlit',(.21,.27,.075)),mat('Oak leaf gray green',(.19,.23,.11)),mat('Oak leaf gold',(.34,.28,.085))]
def tree(x,y,h=7,distant=False):
    z=terrain_z(x,y)
    if y>35:z+=3*math.sin(x*.024+y*.017)+2*math.sin(y*.037)
    def branch(a,b,r):
        a,b=Vector(a),Vector(b);ob=cyl('Oak branch',(a+b)/2,r,(b-a).length,M['trunk'],'05 Landscape',8);ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler()
    branch((x,y,z-.15),(x+.22,y+.1,z+h*.53),h*.035)
    verts=[];faces=[]
    for i in range(11):
        a=i*2.4;rad=h*random.uniform(.18,.40)
        end=(x+math.cos(a)*rad,y+math.sin(a)*rad,z+h*random.uniform(.55,.91))
        branch((x+.18,y,z+h*.35),end,h*.009)
        for j in range(180 if distant else 420):
            px=end[0]+random.gauss(0,h*.105);py=end[1]+random.gauss(0,h*.105);pz=end[2]+random.gauss(0,h*.073)
            az=random.random()*math.tau;l=random.uniform(.09,.20)*(1.7 if distant else 1);w=l*.48;start=len(verts)
            u=Vector((math.cos(az)*l,math.sin(az)*l,random.uniform(-.07,.07)));v=Vector((-math.sin(az)*w,math.cos(az)*w,.045));p=Vector((px,py,pz))
            verts.extend([tuple(p-u),tuple(p+v),tuple(p+u),tuple(p-v)]);faces.append((start,start+1,start+2,start+3))
    me=bpy.data.meshes.new('Individual oak leaf clusters');me.from_pydata(verts,[],faces);ob=bpy.data.objects.new('Foothill oak canopy',me);COL['05 Landscape'].objects.link(ob)
    for m in leafmats:ob.data.materials.append(m)
    for p in me.polygons:p.material_index=random.choices(range(4),[6,2,2,.4])[0]
for x,y,h in [(-9,15,8),(36,17,8.5),(-10,-2,7.5),(5,25,9),(17,27,8),(31,29,10),(-17,24,9),(44,9,8),(36,-10,7)]:tree(x,y,h)
for i in range(150):
    x=random.uniform(-95,115);y=random.uniform(30,135)
    tree(x,y,random.uniform(6,12),True)
for i in range(90):
    x=random.uniform(-25,50);y=random.uniform(-17,31)
    if -10<x<32 and -4<y<20:continue
    sphere('Weathered foothill boulder',(x,y,terrain_z(x,y)),(random.uniform(.18,.65),random.uniform(.18,.6),random.uniform(.2,.45)),random.choice(M['stone']),'05 Landscape',2)
# Low meadow grasses; individual blades joined into one light mesh.
verts=[];faces=[]
for i in range(1600):
    x=random.uniform(-26,53);y=random.uniform(-20,34)
    if -9<x<32 and -5<y<20:continue
    z=terrain_z(x,y)
    for j in range(5):
        a=random.random()*math.tau;h=random.uniform(.12,.37);k=len(verts);w=.016
        verts.extend([(x-w,y,z),(x+w,y,z),(x+math.cos(a)*h*.4,y+math.sin(a)*h*.4,z+h)]);faces.append((k,k+1,k+2))
me=bpy.data.meshes.new('Meadow blades');me.from_pydata(verts,[],faces);ob=bpy.data.objects.new('Dry meadow grasses',me);COL['05 Landscape'].objects.link(ob);ob.data.materials.append(M['agave'])

# Daylight and restrained warm interior lighting.
world=bpy.data.worlds.new('Sierra foothill daylight');scene.world=world;world.use_nodes=True;nt=world.node_tree
sky=nt.nodes.new('ShaderNodeTexSky');sky.sky_type='MULTIPLE_SCATTERING';sky.sun_elevation=math.radians(26);sky.sun_rotation=math.radians(220);sky.air_density=1.15
nt.links.new(sky.outputs['Color'],nt.nodes.get('Background').inputs['Color']);nt.nodes.get('Background').inputs['Strength'].default_value=.35
sun=bpy.data.lights.new('Late afternoon sun','SUN');sun.energy=2.0;sun.angle=math.radians(4)
ob=bpy.data.objects.new('Late afternoon sun',sun);COL['06 Lights'].objects.link(ob);ob.rotation_euler=(math.radians(31),math.radians(-25),math.radians(-35))
def area(name,loc,power,size,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=(1,.84,.63)
    ob=bpy.data.objects.new(name,d);COL['06 Lights'].objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
for x,y in [(11,12),(16,10),(20,12),(23,4),(2,3),(6,4),(2.5,12),(27,3),(6.5,12)]:area('Soft interior illumination',(x,y,2.80),75,1.8,(x,y,.2))

CAMERAS={}
def camera(name,loc,target,lens=40,ortho=None):
    d=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,d);COL['07 Cameras'].objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_end=1000;d.clip_start=.05
    if ortho:d.type='ORTHO';d.ortho_scale=ortho
    CAMERAS[name]=ob;return ob
camera('01 Courtyard hero',(37,-25,10),(14.5,7.0,1.25),36)
camera('02 Approach',(-17,-12,9),(11,7.7,1.3),40)
camera('03 Kitchen',(14.5,8.75,1.82),(20.0,13.4,1.15),23)
camera('04 Living',(14.0,9.5,1.70),(9.0,13.0,1.05),22)
camera('05 Dollhouse',(41,-27,34),(14.5,7.5,0),45,43)
camera('06 Primary suite',(21.0,1.65,1.68),(24.1,5.9,1.0),23)
camera('07 Courtyard eye level',(15,-12,3.2),(14.5,9,1.5),24)
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6
scene.render.resolution_x=1800;scene.render.resolution_y=1125;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-1.7
scene.camera=CAMERAS['01 Courtyard hero']
# Open the native project at a useful camera view.
for screen in bpy.data.screens:
    for ar in screen.areas:
        if ar.type=='VIEW_3D':
            ar.spaces.active.region_3d.view_perspective='CAMERA';ar.spaces.active.clip_end=1000
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'model'/'LAKOTAH_HOUSE.blend'))

summary={'gross_enclosed_m2':325.4,'gross_enclosed_sqft':325.4*FT2_PER_M2,'bedrooms':3,'bathrooms':3,'office':True,'footprint_outer_dimensions_m':[29,14.2],
         'units':'meters','concept_only':True,'modeled_mesh_objects':len([o for o in bpy.data.objects if o.type=='MESH']),
         'stone_vertices':len(stone_verts),'views':list(CAMERAS),'excluded_from_area':['courtyard','terraces','roof overhangs','landscape'],'site':'5725 Lakotah Ln, Placerville CA; oak woodland, downslope 3-acre listing. Terrain, tree positions, grading and placement are schematic; no survey supplied.'}
(ROOT/'checks'/'model_summary.json').write_text(json.dumps(summary,indent=2))
print('HOUSE BUILT',json.dumps(summary),flush=True)

# A GLB of the house, terraces and furnishings for other 3D viewers.
bpy.ops.object.select_all(action='DESELECT')
for g in ['01 Architecture','02 Roofs','03 Glass and doors','04 Furniture']:
    for ob in COL[g].objects:
        if ob.type=='MESH':ob.select_set(True)
with (ROOT/'checks'/'gltf_export.log').open('w') as log,contextlib.redirect_stdout(log):
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'model'/'LAKOTAH_HOUSE.glb'),use_selection=True,export_format='GLB',export_apply=True,export_cameras=False,export_lights=False)
for ob in COL['02 Roofs'].objects:ob.select_set(False)
with (ROOT/'checks'/'gltf_export.log').open('a') as log,contextlib.redirect_stdout(log):
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'model'/'LAKOTAH_cutaway.glb'),use_selection=True,export_format='GLB',export_apply=True,export_cameras=False,export_lights=False)

if '--draft' in sys.argv:
    scene.render.resolution_percentage=55;scene.cycles.samples=20
    scene.render.filepath=str(ROOT/'renders'/'draft_courtyard.png');bpy.ops.render.render(write_still=True)
else:
    for name in CAMERAS:
        scene.camera=CAMERAS[name]
        scene.view_settings.exposure=-.55 if name[:2] in ["03","04","06"] else -1.7
        COL['02 Roofs'].hide_render=('Dollhouse' in name)
        if 'Dollhouse' in name:
            # Lower wall geometry is retained; the open top shows all rooms.
            scene.render.resolution_x=2100;scene.render.resolution_y=1450
        else:scene.render.resolution_x=1800;scene.render.resolution_y=1125
        scene.render.filepath=str(ROOT/'renders'/(name.replace(' ','_')+'.png'));bpy.ops.render.render(write_still=True)
    COL['02 Roofs'].hide_render=False
print('LAKOTAH HOUSE complete.',flush=True)
