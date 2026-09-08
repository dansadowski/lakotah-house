"""Render interior cameras at an exposure suited to the shaded rooms."""
import bpy,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model'/'LAKOTAH_HOUSE.blend'))
s=bpy.context.scene;s.view_settings.exposure=-.55
s.render.resolution_x=1800;s.render.resolution_y=1125
for name in ['03 Kitchen','04 Living','06 Primary suite']:
    path=ROOT/'renders'/(name.replace(' ','_')+'.png')
    if name.startswith('06'):
        deadline=time.time()+300
        while not path.exists() and time.time()<deadline:time.sleep(1)
    s.camera=bpy.data.objects[name];s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
print('Interior exposure renders complete.')
