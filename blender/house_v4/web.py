"""Bake the native V4 scroll animation into a separate .blend and render it.

blender -b assets/3d/elektro-hubmann-house-v4.blend --python-exit-code 1 --python blender/house_v4/web.py -- --prepare
blender -b assets/3d/elektro-hubmann-house-v4-web.blend --python-exit-code 1 --python blender/house_v4/web.py -- --all --resume
"""
import argparse
import json
import sys
import time
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'blender'))
from house_v4.motion import FRAME_COUNT, MANIFEST, STEP, state, schedule

SOURCE = ROOT/'assets/3d/elektro-hubmann-house-v4.blend'
WEB = ROOT/'assets/3d/elektro-hubmann-house-v4-web.blend'
OUT = ROOT/'docs/version-g-qa/blender-v4/web'


def key(obj, path, frame, value):
    setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame)


def fade_group(name):
    group = bpy.data.node_groups.new('V4 web visibility | '+name, 'ShaderNodeTree')
    group.interface.new_socket(name='Visibility', in_out='OUTPUT', socket_type='NodeSocketFloat')
    value = group.nodes.new('ShaderNodeValue')
    output = group.nodes.new('NodeGroupOutput')
    group.links.new(value.outputs[0], output.inputs[0])
    return group, value.outputs[0]


def white_camera_world(scene):
    # Film alpha is sampled stochastically and bypasses Cycles' colour denoiser.
    # During facade dissolution, render the same white studio inside Cycles so
    # the denoiser sees the complete image. Lighting rays keep the original world.
    tree = scene.world.node_tree
    output = next(n for n in tree.nodes if n.type == 'OUTPUT_WORLD')
    original = output.inputs['Surface'].links[0].from_socket
    path = tree.nodes.new('ShaderNodeLightPath')
    white = tree.nodes.new('ShaderNodeBackground')
    white.inputs['Color'].default_value = (16, 16, 16, 1)
    mix = tree.nodes.new('ShaderNodeMixShader')
    tree.links.new(path.outputs['Is Camera Ray'], mix.inputs[0])
    tree.links.new(original, mix.inputs[1])
    tree.links.new(white.outputs[0], mix.inputs[2])
    tree.links.new(mix.outputs[0], output.inputs['Surface'])


def prepare():
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError('Load the architectural V4 source explicitly; it is never overwritten.')
    import build_house_v4
    build_house_v4.set_view('plan')
    scene = bpy.context.scene
    white_camera_world(scene)
    # Reference-bound markers would otherwise replace the animated camera.
    for marker in scene.timeline_markers:
        marker.camera = None
    col = bpy.data.collections.new('V4 | 92 Web motion')
    scene.collection.children.link(col)
    data = bpy.data.cameras.new('V4 | Continuous scroll camera')
    data.type, data.clip_end = 'PERSP', 250
    cam = bpy.data.objects.new(data.name, data)
    col.objects.link(cam)
    cam.rotation_mode = 'QUATERNION'
    target = bpy.data.objects.new('V4 | Continuous look target', None)
    col.objects.link(target)
    scene.camera = cam
    for collection in bpy.data.collections:
        if collection.name.startswith('V4 | EG '):
            collection.hide_render = collection.hide_viewport = False
    groups = {name: fade_group(name) for name in ['cut', 'eg', 'eg_cut', 'route', 'context', 'blind']}
    copies, objects, lights, blinds = {}, [], [], []
    for obj in list(scene.objects):
        if obj.get('interior_light'):
            lights.append((obj, obj.get('nominal_watts', 20)))
        if obj.get('smart_blind'):
            blinds.append((obj, obj.location.z))
        eg = any(c.name.startswith('V4 | EG ') and c.name != 'V4 | EG 04 U stair' for c in obj.users_collection)
        group = ('context' if obj.get('og_stairwell_context') else
                 'route' if obj.get('installation_route') else
                 'blind' if obj.get('smart_blind') else
                 'eg_cut' if eg and obj.get('cutaway_upper') else
                 'cut' if obj.get('cutaway_upper') else 'eg' if eg else None)
        if not group or obj.type not in ['MESH', 'CURVE']:
            continue
        obj.hide_set(False)
        obj.hide_render = False
        objects.append((obj, group))
        # Object-linked slots preserve shared native mesh data safely.
        for slot in obj.material_slots:
            original = slot.material
            if not original:
                continue
            identity = (original.name, group)
            if identity not in copies:
                material = original.copy()
                material.name = original.name+' | web '+group
                tree = material.node_tree
                output = next(n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL')
                shader = output.inputs['Surface'].links[0].from_socket
                transparent = tree.nodes.new('ShaderNodeBsdfTransparent')
                fade_shader = transparent.outputs[0]
                if group in ['eg', 'context']:
                    # Fade the isolated lower storey to the white studio in camera
                    # rays. Stochastic film alpha otherwise produces bright pixel
                    # holes that Cycles' colour denoiser cannot remove. Other rays
                    # retain physical transparency, so illumination fades as well.
                    path = tree.nodes.new('ShaderNodeLightPath')
                    white = tree.nodes.new('ShaderNodeEmission')
                    white.inputs['Color'].default_value = (16, 16, 16, 1)
                    background = tree.nodes.new('ShaderNodeMixShader')
                    tree.links.new(path.outputs['Is Camera Ray'], background.inputs[0])
                    tree.links.new(transparent.outputs[0], background.inputs[1])
                    tree.links.new(white.outputs[0], background.inputs[2])
                    fade_shader = background.outputs[0]
                mix = tree.nodes.new('ShaderNodeMixShader')
                control = tree.nodes.new('ShaderNodeGroup')
                control.node_tree = groups[group][0]
                tree.links.new(control.outputs[0], mix.inputs[0])
                tree.links.new(fade_shader, mix.inputs[1])
                tree.links.new(shader, mix.inputs[2])
                tree.links.new(mix.outputs[0], output.inputs['Surface'])
                copies[identity] = material
            slot.link = 'OBJECT'
            slot.material = copies[identity]
    roots = {name: bpy.data.objects['V4 | '+name+' assembly'] for name in ['OG', 'Roof']}
    records = []
    hidden = {}
    print('V4_WEB_BAKE_START', len(objects), 'animated objects', flush=True)
    for frame in range(1, FRAME_COUNT+1, STEP):
        s = state((frame-1)/(FRAME_COUNT-1))
        key(scene.render, 'film_transparent', frame, not 0 < s['cut'] < 1)
        key(cam, 'location', frame, s['camera'])
        key(target, 'location', frame, s['target'])
        key(cam, 'rotation_quaternion', frame, (Vector(s['target'])-Vector(s['camera'])).to_track_quat('-Z', 'Y'))
        key(data, 'lens', frame, s['lens'])
        for name, property_name in [('OG', 'og'), ('Roof', 'roof')]:
            key(roots[name], 'location', frame, (0, 0, s[property_name]))
        visibility = {'cut': s['cut'], 'eg': s['eg'], 'eg_cut': s['eg']*s['cut'],
                      'route': s['route'], 'context': 1-s['eg'], 'blind': s['blind']}
        for name, (_, socket) in groups.items():
            key(socket, 'default_value', frame, visibility[name])
        for obj, group in objects:
            invisible = visibility[group] < .002
            if hidden.get(obj.name) != invisible:
                key(obj, 'hide_render', frame, invisible)
                key(obj, 'hide_viewport', frame, invisible)
                hidden[obj.name] = invisible
        for obj, nominal in lights:
            key(obj.data, 'energy', frame, nominal*s['light'])
        for obj, height in blinds:
            key(obj, 'location', frame, (obj.location.x, obj.location.y, 2.48+(height-2.48)*s['blind']))
        records.append({'frame': frame, **s})
        if (frame-1) % 240 == 0:
            print('V4_WEB_BAKED', frame, flush=True)
    # Dense native bakes use linear interpolation, preventing overshoot on reversal.
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag = strip.channelbag(slot)
                    if bag:
                        for curve in bag.fcurves:
                            for point in curve.keyframe_points:
                                point.interpolation = 'CONSTANT' if curve.data_path in ['hide_render', 'hide_viewport', 'render.film_transparent'] else 'LINEAR'
    scene.frame_start, scene.frame_end = 1, FRAME_COUNT
    scene.render.fps = 60
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.cycles.adaptive_threshold = .06
    scene.cycles.use_animated_seed = False
    scene.cycles.transparent_max_bounces = 128
    scene.render.use_persistent_data = True
    scene.render.threads_mode, scene.render.threads = 'FIXED', 12
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene['web_revision'] = MANIFEST['revision']
    scene['web_source'] = str(SOURCE)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(WEB), compress=True)
    unique, aliases = schedule()
    (OUT/'manifest.json').write_text(json.dumps(MANIFEST, indent=2)+'\n', encoding='utf-8')
    (OUT/'frame-schedule.json').write_text(json.dumps({'unique': unique, 'aliases': aliases}, indent=2)+'\n', encoding='utf-8')
    (OUT/'motion-samples.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
    print('V4_WEB_PREPARED', len(unique), 'unique frames', flush=True)


def render(args):
    scene = bpy.context.scene
    scene.camera = bpy.data.objects['V4 | Continuous scroll camera']
    scene.render.resolution_x = scene.render.resolution_y = args.size
    scene.cycles.samples = args.samples
    scene.render.use_persistent_data = True
    if scene.get('web_revision') != MANIFEST['revision']:
        raise RuntimeError('Rebuild the native animation before rendering this revision.')
    folder = OUT/('preview' if args.preview else 'renders')/MANIFEST['revision']
    folder.mkdir(parents=True, exist_ok=True)
    frames = schedule()[0] if args.all else [int(v) for v in args.frames.split(',') if v]
    for frame in frames:
        destination = folder/f'frame-{frame:04d}.png'
        if args.resume and destination.exists():
            continue
        scene.frame_set(frame)
        scene.render.filepath = str(destination)
        start = time.perf_counter()
        bpy.ops.render.render(write_still=True)
        print('V4_WEB_FRAME', frame, round(time.perf_counter()-start, 2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--frames', default='')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--size', type=int, default=1000)
    parser.add_argument('--samples', type=int, default=12)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    OUT.mkdir(parents=True, exist_ok=True)
    if args.prepare:
        prepare()
    if args.all or args.frames:
        render(args)
