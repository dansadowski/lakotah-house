"""Read back both GLB exports and compare their geometry bounds to the native scene."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model'/'LAKOTAH_HOUSE.blend'))
def bounds(obs):
    pts=[o.matrix_world@Vector(v) for o in obs if o.type=='MESH' for v in o.bound_box]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
groups=['01 Architecture','02 Roofs','03 Glass and doors','04 Furniture']
expected={}
for name,gs in [('LAKOTAH_HOUSE',groups),('LAKOTAH_cutaway',[g for g in groups if g!='02 Roofs'])]:
    expected[name]=bounds([o for g in gs for o in bpy.data.collections[g].objects])
results={}
for name in expected:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'model'/(name+'.glb')))
    b=bounds(bpy.context.scene.objects)
    err=max(abs(a-c) for ab,cb in zip(expected[name],b) for a,c in zip(ab,cb))
    assert err<.025,(name,err)
    assert all(math.isfinite(v) for row in b for v in row)
    results[name]={'readback_success':True,'world_bounds_m':b,'native_bounds_max_difference_m':err,'mesh_objects':sum(o.type=='MESH' for o in bpy.context.scene.objects)}
(ROOT/'checks'/'export_checks.json').write_text(json.dumps(results,indent=2))
print('Both GLB files re-imported successfully and matched native scene bounds.',results)
