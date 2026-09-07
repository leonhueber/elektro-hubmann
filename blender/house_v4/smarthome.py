"""Build selected Smart Home A directly into sibling native Blender files.

Load the exterior-r1 .blend (architectural or web) and run with --apply.
The existing native slats gain real tilt and travel; all lamps stay on.
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'blender'))
from house_v4 import core as c
from house_v4.motion import FRAME_COUNT, STEP, schedule as base_schedule
from house_v4.smarthome_motion import REVISION, details, state, schedule, changed
from house_v4.web import key, fade_group

OUT = ROOT/'docs/version-g-qa/blender-v4-smarthome-r1'
MOCKUP = ROOT/'docs/mockups/house-v4-smarthome-r1/01-a-schlafzimmer-balkon.png'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def original_signature(scene, slats):
    cam = bpy.data.objects['V4 | Continuous scroll camera']
    values = [*cam.location, *cam.rotation_quaternion, cam.data.lens]
    for obj in slats:
        values.extend([*obj.location, *obj.rotation_euler, float(obj.hide_render)])
    values.extend(obj.data.energy for obj in scene.objects if obj.get('interior_light'))
    return tuple(round(float(v), 5) for v in values)


def create_devices():
    c.M.clear()
    for mat in sorted(bpy.data.materials, key=lambda m: m.users, reverse=True):
        if mat.name.startswith('V4 | ') and ' | web ' not in mat.name and ' | exterior web ' not in mat.name:
            c.M.setdefault(re.sub(r'\.\d{3}$', '', mat.name[5:]), mat)
    parent = bpy.data.objects['V4 | OG assembly']
    c.collection('V4 | OG 14 Smart Home A', parent, 'OG | Parents')
    before = set(bpy.context.scene.objects)
    body = c.box('Smart A | room controller', (4.17, 5.074, 1.22), (.17, .036, .17), 'charcoal', .009)
    body['mounting_height_m'] = 1.22
    body['function'] = 'Room scene, temperature and balcony shading'
    c.box('Smart A | controller glass', (4.17, 5.054, 1.22), (.148, .004, .148), 'black', .006)
    ink = c.material('smart display', (.82, .80, .74), .42)
    shader = ink.node_tree.nodes['Principled BSDF']
    shader.inputs['Emission Color'].default_value = (.82, .80, .74, 1)
    shader.inputs['Emission Strength'].default_value = .3
    font = bpy.data.curves.new('Smart A | 21 degree display', 'FONT')
    font.body, font.size, font.align_x = '21°', .038, 'CENTER'
    obj = c.register(bpy.data.objects.new(font.name, font), ink)
    obj.location = (4.17, 5.050, 1.215)
    obj.rotation_euler = (math.pi/2, 0, 0)
    for x in [4.132, 4.208]:
        c.box('Smart A | scene touch point', (x, 5.049, 1.174), (.014, .001, .002), ink, .0005)
    c.box('Smart A | blind headrail', (2.25, -.026, 2.49), (2.54, .12, .075), 'charcoal', .006)
    for x in [.99, 3.51]:
        c.box('Smart A | blind guide', (x, .007, 1.86), (.022, .024, 1.23), 'charcoal', .003)
    added = [obj for obj in bpy.context.scene.objects if obj not in before]
    for obj in added:
        obj['smarthome_revision'] = REVISION
    return added


def fade_devices(objects):
    group, socket = fade_group('smarthome A devices')
    copies = {}
    for obj in objects:
        for slot in obj.material_slots:
            original = slot.material
            if original.name not in copies:
                mat = original.copy()
                mat.name = original.name+' | smart A visibility'
                tree = mat.node_tree
                output = next(n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL')
                surface = output.inputs['Surface'].links[0].from_socket
                transparent = tree.nodes.new('ShaderNodeBsdfTransparent')
                control = tree.nodes.new('ShaderNodeGroup')
                control.node_tree = group
                mix = tree.nodes.new('ShaderNodeMixShader')
                tree.links.new(control.outputs[0], mix.inputs[0])
                tree.links.new(transparent.outputs[0], mix.inputs[1])
                tree.links.new(surface, mix.inputs[2])
                tree.links.new(mix.outputs[0], output.inputs['Surface'])
                copies[original.name] = mat
            slot.link = 'OBJECT'
            slot.material = copies[original.name]
    return socket


def apply():
    scene = bpy.context.scene
    if scene.get('smarthome_revision'):
        raise RuntimeError('Load the unchanged exterior-r1 source, not a previously patched file.')
    source = Path(bpy.data.filepath).resolve()
    web = bool(scene.get('web_revision'))
    expected = ROOT/'assets/3d'/('elektro-hubmann-house-v4-exterior-r1'+('-web' if web else '')+'.blend')
    if source != expected.resolve() or scene.get('exterior_variant') != 'B':
        raise RuntimeError('Expected the approved native B exterior source.')
    if web and scene['web_revision'] != 'v4-scroll-02-exterior-01':
        raise RuntimeError('Unexpected base camera revision.')
    slats = sorted((o for o in scene.objects if o.get('smart_blind')), key=lambda o: o.name)
    assert len(slats) == 15
    outside = [f for f in range(1, FRAME_COUNT+1, STEP) if not changed(f)]
    before = {}
    if web:
        for frame in outside:
            scene.frame_set(frame)
            before[frame] = original_signature(scene, slats)
    scene.frame_set(1)
    added = create_devices()
    socket = fade_devices(added) if web else None
    samples = []
    if web:
        cam = bpy.data.objects['V4 | Continuous scroll camera']
        target = bpy.data.objects['V4 | Continuous look target']
        # Change only the OG close-up interval. Every other native key remains intact.
        for frame in range(1, FRAME_COUNT+1, STEP):
            p = (frame-1)/(FRAME_COUNT-1)
            d = details(p)
            key(socket, 'default_value', frame, d['controller'])
            for obj in added:
                key(obj, 'hide_render', frame, d['controller'] == 0)
                key(obj, 'hide_viewport', frame, d['controller'] == 0)
            if changed(frame):
                s = state(p)
                key(cam, 'location', frame, s['camera'])
                key(cam, 'rotation_quaternion', frame, (Vector(s['target'])-Vector(s['camera'])).to_track_quat('-Z', 'Y'))
                key(target, 'location', frame, s['target'])
                key(cam.data, 'lens', frame, s['lens'])
            # The original slat translations outside the interval remain untouched.
            keyframes = changed(frame) or (frame > 1 and changed(frame-STEP)) or (frame < FRAME_COUNT and changed(frame+STEP))
            if keyframes:
                scene.frame_set(frame)
                for index, slat in enumerate(slats):
                    if changed(frame):
                        slat.location.z -= index*.035*d['focus']
                        key(slat, 'location', frame, tuple(slat.location))
                    key(slat, 'rotation_euler', frame, (d['tilt'], 0, 0))
            if frame in [823, 865, 899, 909, 931, 965]:
                samples.append({'frame': frame, **state(p)})
        # Quaternion/camera and slat keyframes remain dense and reversible.
        for action in bpy.data.actions:
            for layer in action.layers:
                for strip in layer.strips:
                    for slot in action.slots:
                        bag = strip.channelbag(slot)
                        if bag:
                            for curve in bag.fcurves:
                                for point in curve.keyframe_points:
                                    point.interpolation = 'CONSTANT' if curve.data_path in ['hide_render', 'hide_viewport', 'render.film_transparent'] else 'LINEAR'
        mismatches = []
        for frame in outside:
            scene.frame_set(frame)
            if before[frame] != original_signature(scene, slats) or any(not o.hide_render for o in added):
                mismatches.append(frame)
        if mismatches:
            raise RuntimeError('Unexpected change outside Smart Home: '+str(mismatches))
    else:
        for index, slat in enumerate(slats):
            slat.location.z = 2.40-index*.073
            slat.rotation_euler.x = math.radians(-35)
    scene['smarthome_revision'] = REVISION
    scene['smarthome_variant'] = 'A: parents bedroom and balcony'
    scene['smarthome_source_sha256'] = sha(source)
    if web:
        scene['web_revision'] = REVISION
    image = bpy.data.images.load(str(MOCKUP), check_existing=True)
    image.pack()
    note = bpy.data.texts.new('V4_SMART_HOME_A_README')
    note.write('Selected Smart Home A. Native camera push-in at 57–60.5%, return at 64.5–67%.\n'
               'Room controller on the existing parents back wall, at 1.22 m. Display is an illustrative 21°.\n'
               'Fifteen existing blind slats travel and tilt. All interior lamps retain their original energy.\n'
               'Web-only detail visibility follows the close-up; architectural devices are always present.\n'
               'Unchanged native B sources are preserved. Reproduce with blender/house_v4/smarthome.py --apply.\n')
    destination = ROOT/'assets/3d'/('elektro-hubmann-house-v4-smarthome-r1'+('-web' if web else '')+'.blend')
    scene.frame_set(909 if web else 1)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
    unique, aliases = schedule()
    base_unique, base_aliases = base_schedule()
    reuse = {str(f): base_aliases.get(str(f), f) for f in unique if not changed(f)}
    report = {'revision': REVISION, 'nativeFile': str(destination.relative_to(ROOT)), 'sha256': sha(destination),
              'baseFile': str(source.relative_to(ROOT)), 'baseSha256': sha(source), 'variant': 'A',
              'controllerHeightM': 1.22, 'slats': len(slats), 'addedObjects': len(added),
              'outsideFramesVerified': len(outside) if web else 0, 'outsideChanges': [],
              'nativeFrames': len(unique), 'newFrames': [f for f in unique if changed(f)],
              'reuse': reuse, 'samples': samples, 'allPassed': True}
    write_json(OUT/('web-validation.json' if web else 'model-validation.json'), report)
    if web:
        write_json(OUT/'frame-schedule.json', {'unique': unique, 'aliases': aliases})
    print('SMART_HOME_NATIVE_SAVED', json.dumps(report), flush=True)


def render(frames, size, samples):
    scene = bpy.context.scene
    if scene.get('web_revision') != REVISION:
        raise RuntimeError('Load the saved Smart Home animation.')
    from house_v4.exterior_delivery import SETTINGS
    scene.camera = bpy.data.objects['V4 | Continuous scroll camera']
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = SETTINGS['adaptiveThreshold']
    scene.cycles.adaptive_min_samples = SETTINGS['minimumSamples']
    scene.cycles.use_animated_seed = False
    scene.cycles.seed = 0
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.threads_mode, scene.render.threads = 'FIXED', 4
    scene.render.use_persistent_data = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag = strip.channelbag(slot)
                    if bag:
                        for curve in bag.fcurves:
                            if curve.data_path == 'render.film_transparent':
                                curve.mute = True
    scene.render.film_transparent = False
    OUT.mkdir(parents=True, exist_ok=True)
    for frame in frames:
        scene.frame_set(frame)
        scene.render.filepath = str(OUT/f'proof-{frame:04d}.png')
        bpy.ops.render.render(write_still=True)
        print('SMART_HOME_PROOF_RENDERED', frame, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--frames', default='')
    parser.add_argument('--size', type=int, default=1200)
    parser.add_argument('--samples', type=int, default=64)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.apply:
        apply()
    if args.frames:
        render([int(f) for f in args.frames.split(',')], args.size, args.samples)
