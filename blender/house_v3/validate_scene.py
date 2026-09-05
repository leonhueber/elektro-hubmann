"""Read-only V3 source-scene checks; run through Blender on the saved scene."""
import json
from pathlib import Path
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
manifest=json.loads((ROOT/'src/config/house-v3-manifest.json').read_text(encoding='utf-8'))
assert scene.frame_end==manifest['frameCount']
roof=bpy.data.objects['V3 Roof lift']
assert len(roof.children)>20
assert bpy.data.collections['V3_ENERGY_OPTIONAL'].hide_render
for obj in bpy.data.objects:
    if obj.name.startswith(('V3 bed base','V3 nightstand')):
        right_edge=max((obj.matrix_world@Vector(corner)).x for corner in obj.bound_box)
        assert right_edge < -2.25, f'Furniture intersects stair opening: {obj.name}'
states={}
for frame in [1,34,58,86,109,129,159,181,58,1]:
    scene.frame_set(frame)
    state=(round(roof.location.z,5),tuple(round(mat.node_tree.nodes['Shell visibility'].inputs[0].default_value,5)
        for mat in bpy.data.materials if mat.node_tree and mat.node_tree.nodes.get('Shell visibility')))
    if frame in states:
        assert state==states[frame],f'Non-deterministic state at {frame}'
    states[frame]=state
assert states[1][0]==states[181][0]
assert states[58][0]>states[1][0]+1
assert all(v==0 for v in states[58][1])
assert all(v==1 for v in states[1][1])
framing=[]
for profile,config in manifest['profiles'].items():
    camera=bpy.data.objects['V3 '+profile.capitalize()]
    scene.render.resolution_x=config['width']; scene.render.resolution_y=config['height']
    for frame in (1,58,181):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        points=[]
        for obj in bpy.data.objects:
            if obj.type!='MESH' or obj.hide_render or any(c.hide_render for c in obj.users_collection):
                continue
            for corner in obj.bound_box:
                points.append(world_to_camera_view(scene,camera,obj.matrix_world@Vector(corner)))
        bounds=[min(p.x for p in points),min(p.y for p in points),max(p.x for p in points),max(p.y for p in points)]
        framing.append({'profile':profile,'frame':frame,'bounds':bounds})
        assert min(bounds[:2])>=.005 and max(bounds[2:])<=.995, f'Camera clips model: {framing[-1]}'
report={'objects':len(bpy.data.objects),'deterministic':True,'roofChildren':len(roof.children),'framing':framing}
out=ROOT/'docs/version-g-qa/blender-v3/scene-validation.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
