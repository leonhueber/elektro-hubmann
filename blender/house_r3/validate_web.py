"""Check reversible web camera states and the fixed poses used by annotations."""
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'docs/version-g-qa/blender-v3-r3/web-preview'
if '--detail' in sys.argv:
    QA = ROOT / 'docs/version-g-qa/blender-v3-r3/web-detail'
manifest = json.loads((QA/'manifest.json').read_text(encoding='utf-8'))
scene = bpy.context.scene
checks = []


def signature(frame):
    scene.frame_set(frame)
    values = []
    for name in ['Camera | Web desktop', 'Camera | Web mobile', 'RIG | Roof lift', 'RIG | Bedroom blind']:
        obj = bpy.data.objects[name]
        values.extend(round(v, 6) for row in obj.matrix_world for v in row)
        if obj.type == 'CAMERA':
            values.append(round(obj.data.ortho_scale, 6))
    for material in bpy.data.materials:
        if material.use_nodes and material.node_tree.nodes.get('Visibility'):
            values.append(round(material.node_tree.nodes['Visibility'].inputs[0].default_value, 6))
    return values


forward = {frame: signature(frame) for frame in range(1, 182)}
reverse_mismatches = [frame for frame in range(181, 0, -1) if signature(frame) != forward[frame]]
checks.append({'name': 'All 181 frames reproduce when evaluated backwards', 'pass': not reverse_mismatches, 'detail': reverse_mismatches})
for profile in manifest['profiles']:
    camera = bpy.data.objects['Camera | Web '+profile]
    config = manifest['profiles'][profile]
    scene.render.resolution_x, scene.render.resolution_y = config['width'], config['height']
    clipped = []
    roof_parts = [o for o in bpy.data.objects['RIG | Roof lift'].children_recursive
                  if o.type == 'MESH' and (o.name == 'Roof insulated slab' or 'metal coping' in o.name or o.name.startswith('PV aluminium frame'))]
    visibility = bpy.data.materials['plaster | roof'].node_tree.nodes['Visibility'].inputs[0]
    for frame in range(1, 44):
        scene.frame_set(frame)
        if visibility.default_value < .1:
            continue
        points = [world_to_camera_view(scene, camera, o.matrix_world @ Vector(corner))
                  for o in roof_parts for corner in o.bound_box]
        if any(p.x < 0 or p.x > 1 or p.y < 0 or p.y > 1 for p in points):
            clipped.append(frame)
    checks.append({'name': profile+' lifted roof stays in frame until faded', 'pass': not clipped, 'detail': clipped})
    for chapter in manifest['chapters'][1:]:
        start, end = chapter['annotationFrames']
        poses = []
        for frame in range(start, end+1):
            scene.frame_set(frame)
            poses.append(tuple(round(v, 5) for row in camera.matrix_world for v in row) + (round(camera.data.ortho_scale, 5),))
        checks.append({'name': profile+' stable annotation pose: '+chapter['id'], 'pass': len(set(poses)) == 1})
scene.frame_set(61)
roof = bpy.data.objects['RIG | Roof lift']
checks.append({'name': 'Roof above house during interior chapters', 'pass': roof.location.z > 2})
scene.frame_set(181)
checks.append({'name': 'Roof returns to its seat', 'pass': abs(roof.location.z) < .00001})
report = {'passed': all(c['pass'] for c in checks), 'scene': bpy.data.filepath, 'checks': checks}
(QA/'animation-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
print(json.dumps(report, indent=2))
if not report['passed']:
    raise RuntimeError('R3 web animation validation failed')
