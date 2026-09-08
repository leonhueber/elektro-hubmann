"""Inspect the saved continuous animation without rendering or saving Blender.

blender -b assets/3d/elektro-hubmann-house-v4-continuous-r1-web.blend \
  --python-exit-code 1 --python blender/house_v4/validate_continuous.py

Passing these technical checks is not visual approval of any rendered frame.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'blender'))
from house_v4.continuous_motion import FRAME_COUNT, REVISION, STEP, state

SOURCE = ROOT / 'assets/3d/elektro-hubmann-house-v4-smarthome-r1-web.blend'
ANIMATION = ROOT / 'assets/3d/elektro-hubmann-house-v4-continuous-r1-web.blend'
OUT = ROOT / 'docs/version-g-qa/blender-v4-continuous-r1/native-validation.json'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def connected_visibility_groups(material):
    """Ignore orphaned nodes; examine only shaders feeding Material Output."""
    if not material or not material.node_tree:
        return []
    outputs = [node for node in material.node_tree.nodes if node.type == 'OUTPUT_MATERIAL' and node.is_active_output]
    pending, visited, found = list(outputs), set(), []
    while pending:
        node = pending.pop()
        if node.as_pointer() in visited:
            continue
        visited.add(node.as_pointer())
        if node.type == 'GROUP' and node.node_tree and node.node_tree.name.startswith('V4 web visibility | '):
            found.append(node.node_tree.name)
        pending.extend(link.from_node for socket in node.inputs for link in socket.links)
    return found


def emission_socket(obj):
    material = obj.active_material if obj else None
    shader = material.node_tree.nodes.get('Principled BSDF') if material and material.node_tree else None
    return shader.inputs['Emission Strength'] if shader else None


def run():
    if Path(bpy.data.filepath).resolve() != ANIMATION.resolve():
        raise RuntimeError('Load the saved continuous-r1-web.blend explicitly.')
    scene = bpy.context.scene
    initial_frame = scene.frame_current
    source_hash, animation_hash = sha(SOURCE), sha(ANIMATION)
    checks = []

    def check(name, passed, **evidence):
        checks.append({'check': name, 'passed': bool(passed), **evidence})

    def span(values):
        return max(values) - min(values) if values else 0.

    roots = {name: bpy.data.objects.get('V4 | ' + name + ' assembly') for name in ['EG', 'OG', 'Roof']}
    camera = scene.camera
    slats = sorted((obj for obj in scene.objects if obj.get('smart_blind')),
                   key=lambda obj: obj.get('continuous_blind_index', -1))
    lights = [obj for obj in scene.objects if obj.type == 'LIGHT' and obj.get('interior_light')]
    paths = [obj for obj in scene.objects if obj.get('energy_path')]
    lamps = sorted((obj for obj in scene.objects if 'charge_segment' in obj), key=lambda obj: obj['charge_segment'])
    retained = [obj for obj in scene.objects if obj.type in ['MESH', 'CURVE'] and
                (obj.name.startswith('OG | balcony door') or obj.name.startswith('Exterior | balcony door')
                 or obj.name.startswith('Smart A | blind headrail'))]
    lower = bpy.data.objects.get('Tour | blind weighted lower rail')
    controller = emission_socket(bpy.data.objects.get('Tour | controller scene indicator'))
    camera_led = emission_socket(bpy.data.objects.get('Tour | camera activity LED'))
    wallbox = bpy.data.objects.get('Tour | wallbox')
    cable = bpy.data.objects.get('Tour | stowed charging cable')
    connector = bpy.data.objects.get('Tour | docked connector')
    sun = bpy.data.objects.get('Tour | directional daylight')

    check('Saved revision and frame range', scene.get('web_revision') == REVISION and
          scene.frame_start == 1 and scene.frame_end == FRAME_COUNT)
    check('Source hash matches saved provenance', scene.get('continuous_source_sha256') == source_hash)
    baseline_path = ROOT / 'docs/version-g-qa/blender-v4-smarthome-r1/web-validation.json'
    baseline = json.loads(baseline_path.read_text(encoding='utf-8')) if baseline_path.exists() else {}
    check('Original source still matches its earlier native validation', baseline.get('sha256') == source_hash,
          expected=baseline.get('sha256'), actual=source_hash)
    build_path = OUT.parent / 'native-build.json'
    build = json.loads(build_path.read_text(encoding='utf-8')) if build_path.exists() else {}
    check('Build report identifies these exact native files', build.get('sourceSha256') == source_hash and
          build.get('nativeSha256') == animation_hash)
    check('Three separate architectural assemblies', all(roots.values()) and
          len({obj.as_pointer() for obj in roots.values() if obj}) == 3)
    check('Active native camera', camera is not None and camera.type == 'CAMERA')
    check('Thirty individually indexed slats on the upper floor', len(slats) == 30 and
          [obj.get('continuous_blind_index') for obj in slats] == list(range(30)) and
          all(obj.parent == roots['OG'] for obj in slats))
    check('Interior lights and weighted blind rail exist', bool(lights) and lower is not None,
          interiorLightCount=len(lights))
    check('Both native energy curves exist', len(paths) == 2 and
          {obj.get('energy_path') for obj in paths} == {'solar route', 'solar pulse'} and
          all(obj.type == 'CURVE' for obj in paths))
    check('Eight individually controlled charge LEDs', len(lamps) == 8 and
          [obj['charge_segment'] for obj in lamps] == list(range(8)))
    check('Controller and camera feedback use actual material sockets', controller is not None and camera_led is not None)
    check('Vehicle geometry is removed', not any(
        obj.get('vehicle_length_m') or obj.name.startswith(
            ('Tour | formed silver body', 'Tour | rounded tyre', 'Tour | electric hatchback'))
        for obj in scene.objects))
    check('Wallbox connector and stowed cable are physically attached',
          wallbox is not None and cable is not None and connector is not None and
          cable.parent == wallbox and connector.parent == wallbox and
          math.dist(tuple(cable.data.splines[0].bezier_points[-1].co),
                    tuple(connector.location - Vector((0, 0, .078)))) < 1e-5)
    check('Directional sunlight uses a 0.8 degree source', sun is not None and sun.type == 'LIGHT' and
          sun.data.type == 'SUN' and abs(sun.data.angle - math.radians(.8)) < 1e-6 and sun.data.energy > 0)
    check('Retained timber access is connected to unfaded shaders', bool(retained) and
          all(obj.get('continuous_group') == 'always' and obj.material_slots and
              all(slot.material and not connected_visibility_groups(slot.material) for slot in obj.material_slots)
              for obj in retained), objects=len(retained))

    ring = bpy.data.objects.get('Tour | camera status ring')
    button = bpy.data.objects.get('Entrance | bell button')
    ring_points = list(ring.data.splines[0].points) if ring and ring.type == 'CURVE' else []
    center = sum((Vector(point.co[:3]) for point in ring_points), Vector()) / len(ring_points) if ring_points else None
    check('Bell status ring is concentric with the existing button', center is not None and button is not None and
          abs(center.x - button.location.x) < 1e-4 and abs(center.z - button.location.z) < 1e-4,
          ringCenter=list(center) if center is not None else None)

    sampled = []
    errors = {'light': 0., 'camera': 0., 'lens': 0., 'assembly': 0.}
    positions, light_ranges = [], {obj.name: [] for obj in lights}
    slat_z, slat_angle = {obj.name: [] for obj in slats}, {obj.name: [] for obj in slats}
    assemblies = {name: [] for name in roots}
    path_ends, path_starts = {obj.name: [] for obj in paths}, {obj.name: [] for obj in paths}
    counts, lower_heights, controller_values, camera_values = [], [], [], []
    retained_hidden, maximum_visible_slats = [], 0
    can_sample = camera is not None and all(roots.values()) and all(obj.type == 'CURVE' for obj in paths)
    try:
        if can_sample:
            for frame in range(1, FRAME_COUNT + 1, STEP):
                scene.frame_set(frame)
                expected = state((frame - 1) / (FRAME_COUNT - 1))
                position = tuple(camera.matrix_world.translation)
                positions.append(position)
                errors['camera'] = max(errors['camera'], math.dist(position, expected['camera']))
                errors['lens'] = max(errors['lens'], abs(camera.data.lens - expected['lens']))
                for name, obj in roots.items():
                    height = obj.location.z
                    assemblies[name].append(height)
                    wanted = 0 if name == 'EG' else expected['og' if name == 'OG' else 'roof']
                    errors['assembly'] = max(errors['assembly'], abs(height - wanted))
                for light in lights:
                    value = light.data.energy
                    light_ranges[light.name].append(value)
                    errors['light'] = max(errors['light'], abs(value - light.get('nominal_watts', 20)))
                for slat in slats:
                    slat_z[slat.name].append(slat.location.z)
                    slat_angle[slat.name].append(slat.rotation_euler.x)
                maximum_visible_slats = max(maximum_visible_slats, sum(not obj.hide_render for obj in slats))
                for path in paths:
                    path_ends[path.name].append(path.data.bevel_factor_end)
                    path_starts[path.name].append(path.data.bevel_factor_start)
                counts.append(sum(not obj.hide_render for obj in lamps))
                if lower:
                    lower_heights.append(lower.location.z)
                if controller is not None:
                    controller_values.append(controller.default_value)
                if camera_led is not None:
                    camera_values.append(camera_led.default_value)
                if any(obj.hide_render for obj in retained):
                    retained_hidden.append(frame)
                if frame in [1, 397, 627, 771, 793, 1089, 1225, 1369, FRAME_COUNT]:
                    sampled.append({'frame': frame, 'camera': position, 'assemblies':
                                    {name: obj.location.z for name, obj in roots.items()},
                                    'chargeLEDs': counts[-1], 'energyEnds':
                                    {obj.name: obj.data.bevel_factor_end for obj in paths}})
                if (frame - 1) % 240 == 0:
                    print('CONTINUOUS_VALIDATE_SAMPLE', frame, flush=True)
    finally:
        scene.frame_set(initial_frame)

    distances = [math.dist(a, b) for a, b in zip(positions, positions[1:])]
    check('All 721 saved native samples were inspected', len(positions) == len(range(1, FRAME_COUNT + 1, STEP)),
          inspected=len(positions))
    check('Camera moves at every adjacent sampled position', bool(distances) and min(distances) > 1e-5 and
          all(math.isfinite(value) for position in positions for value in position),
          minimumTravelMetres=min(distances) if distances else None)
    check('Saved camera and floors match the continuous tour', max(errors['camera'], errors['lens'], errors['assembly']) < 1e-4,
          maximumErrors=errors)
    check('All interior lights stay at nominal power', bool(lights) and errors['light'] < 1e-4 and
          all(values and min(values) > 0 for values in light_ranges.values()))
    check('Ground floor stays while OG and roof lift independently', span(assemblies['EG']) < 1e-5 and
          span(assemblies['OG']) > 3.9 and span(assemblies['Roof']) > 7.9 and
          all(roof - og >= 2.9999 for roof, og in zip(assemblies['Roof'], assemblies['OG'])))
    check('All 30 slats actually move or rotate', len(slats) == 30 and
          all(span(slat_z[obj.name]) > .01 or span(slat_angle[obj.name]) > .1 for obj in slats) and
          maximum_visible_slats == 30, bottomRailTravelMetres=span(lower_heights))
    check('Blind lowering has at least 1.8 metres of native travel', span(lower_heights) >= 1.8)
    check('Energy curves grow from short beginnings to full length', len(paths) == 2 and
          all(values and values[0] <= .002 and values[-1] >= .999 and
              all(b >= a - 1e-6 for a, b in zip(values, values[1:])) for values in path_ends.values()))
    pulse = next((obj for obj in paths if obj.get('energy_path') == 'solar pulse'), None)
    check('A short solar pulse moves along the growing route', pulse is not None and
          bool(path_starts[pulse.name]) and span(path_starts[pulse.name]) > .8 and
          abs(path_ends[pulse.name][-1] - path_starts[pulse.name][-1] - .14) < 1e-5)
    check('Native charging display progresses from zero through eight LEDs', bool(counts) and
          counts[0] == 0 and counts[-1] == 8 and set(counts) == set(range(9)) and
          all(b >= a for a, b in zip(counts, counts[1:])), observedCounts=sorted(set(counts)))
    check('Controller and camera LEDs respond through emission changes',
          span(controller_values) > 2 and span(camera_values) > 2)
    check('Retained balcony door stays visible throughout the tour', bool(retained) and not retained_hidden,
          hiddenFrames=retained_hidden[:10])
    check('Both energy routes terminate on the wallbox status face', len(paths) == 2 and
          all(math.dist(tuple(path.data.splines[0].bezier_points[-1].co),
                        (9.87, 2.405, 1.428)) < 1e-5 for path in paths))
    check('Validation leaves both native files unchanged', sha(SOURCE) == source_hash and sha(ANIMATION) == animation_hash)

    report = {'revision': REVISION, 'nativeAnimation': str(ANIMATION), 'nativeAnimationSha256': animation_hash,
              'nativeSourceSha256': source_hash, 'objects': len(scene.objects), 'sampleCount': len(positions),
              'allPassed': all(item['passed'] for item in checks), 'visualApproval': False,
              'scope': 'Saved native states only; no renders and no Blender saves. Render quality requires visual review.',
              'checks': checks, 'samples': sampled,
              'interiorLights': {name: {'minimumWatts': min(values), 'maximumWatts': max(values)}
                                 for name, values in light_ranges.items() if values}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUT.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    temporary.replace(OUT)
    failed = [item['check'] for item in checks if not item['passed']]
    print('CONTINUOUS_NATIVE_VALIDATION', json.dumps({'allPassed': report['allPassed'], 'checks': len(checks),
          'failed': failed, 'report': str(OUT), 'visualApproval': False}), flush=True)
    if failed:
        raise RuntimeError('Native validation failed: ' + '; '.join(failed))
    return report


if __name__ == '__main__':
    run()
