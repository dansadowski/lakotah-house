"""Validate expected deliverables, hash them and build a clean concept archive."""
from pathlib import Path
import json,struct,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]
views=['01_Courtyard_hero','02_Approach','03_Kitchen','04_Living','05_Dollhouse','06_Primary_suite','07_Courtyard_eye_level']
image_checks={}
for name in views:
    p=ROOT/'renders'/(name+'.png');data=p.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n'
    dims=struct.unpack('>II',data[16:24]);assert dims==((2100,1450) if 'Dollhouse' in name else (1800,1125))
    image_checks[name]={'dimensions':dims,'bytes':len(data)}
for name in ['LAKOTAH_shell.FCStd','LAKOTAH_shell_cutaway.FCStd']:
    with zipfile.ZipFile(ROOT/'model'/name) as z:
        assert z.testzip() is None and 'Document.xml' in z.namelist()
for name in ['plan_checks','site_checks','export_checks']:
    assert json.loads((ROOT/'checks'/(name+'.json')).read_text())
(ROOT/'checks'/'delivery_checks.json').write_text(json.dumps({'render_files':image_checks,'freecad_archives_readable':True,'visual_review':'Seven camera views plus floor plan and site study inspected. Interior exposure adjusted for visibility.','scope':'Architectural concept, not construction documentation.'},indent=2))
files=[ROOT/'START_HERE.md']
for folder,extensions in [('source',{'.py'}),('model',{'.blend','.glb','.FCStd','.step'}),('drawings',{'.png','.svg'}),('checks',{'.json'})]:
    files.extend(p for p in (ROOT/folder).iterdir() if p.is_file() and p.suffix in extensions)
files.extend(ROOT/'renders'/(name+'.png') for name in views)
files=sorted(files)
manifest=ROOT/'MANIFEST.sha256';manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT))+'\n' for p in files))
files.append(manifest)
archive=ROOT.parent/'LAKOTAH_HOUSE_Concept.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in files:z.write(p,p.relative_to(ROOT.parent))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'archive':str(archive),'size_mb':round(archive.stat().st_size/1e6,1),'files':len(files),'archive_integrity':'passed'},indent=2))
