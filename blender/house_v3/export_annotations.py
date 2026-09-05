"""Project explanatory labels through the exact saved Blender cameras."""
import json
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'src/config/house-v3-manifest.json').read_text(encoding='utf-8'))
if str(manifest.get('revision', '')).startswith('r3'):
    raise SystemExit('R3 is active. Project its labels with blender/house_r3/web_preview.py -- --annotations.')
items={
    'planning':[],
    'installation': [('Elektroverteilung',(.64,-1,1.68),(.44,.92)),('Netzwerk',(-.32,-1.04,1.4),(.20,.70))],
    'lighting': [('Wohnraumlicht',(3.15,-1.5,2.3),(.82,.90))],
    'smarthome': [('Beschattung',(-2.8,-3.43,5.4),(.19,.35)),('KNX-Taster',(-.9,-3.64,1.75),(.40,.92))],
    'security': [('Videosprechanlage',(1.77,-3.62,1.7),(.70,.92)),('Alarmkontakt',(4.76,-3.5,2.55),(.84,.53))],
    'energy': [('PV-Module',(0,-1,6.95),(.28,.14)),('Wechselrichter',(4.22,.12,1.85),(.74,.92))],
}
scene=bpy.context.scene
output={}
for profile,config in manifest['profiles'].items():
    scene.render.resolution_x=config['width'];scene.render.resolution_y=config['height']
    camera=bpy.data.objects['V3 '+profile.capitalize()]
    output[profile]={}
    for chapter in manifest['chapters']:
        scene.frame_set(round(chapter['rest']*(manifest['frameCount']-1))+1)
        labels=[]
        for text,point,position in items[chapter['id']]:
            projected=world_to_camera_view(scene,camera,Vector(point))
            labels.append({'text':text,'x':round(projected.x*config['width'],2),
                           'y':round((1-projected.y)*config['height'],2),
                           'labelX':round(position[0]*config['width'],2),
                           'labelY':round(position[1]*config['height'],2)})
        output[profile][chapter['id']]=labels
(ROOT/'src/config/house-v3-annotations.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
print('V3 projected annotations exported for both cameras')
