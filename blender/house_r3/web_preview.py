"""Prepare a separate native R3 web scene and render exact sampled scroll frames.

The architectural source remains untouched. Run inside Blender with --prepare,
then load the saved web .blend for --profile desktop/mobile and --frames or --all.
"""
import argparse
import json
from pathlib import Path

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/version-g-qa/blender-v3-r3/web-preview'
SOURCE = ROOT / 'assets/3d/elektro-hubmann-house-v3-r3.blend'
WEB = ROOT / 'assets/3d/elektro-hubmann-house-v3-r3-web.blend'
MANIFEST = {
    'version': 3, 'revision': 'r3-preview', 'frameCount': 181,
    'assetPath': 'images/version-g/house-r3/',
    'profiles': {
        'desktop': {'width': 960, 'height': 860, 'step': 2},
        'mobile': {'width': 640, 'height': 640, 'step': 3},
    },
    'chapters': [
        {'id': 'planning', 'start': 0, 'rest': 6/180, 'annotationFrames': [0, 0]},
        {'id': 'installation', 'start': .1, 'rest': 60/180, 'annotationFrames': [59, 67]},
        {'id': 'lighting', 'start': .37, 'rest': 84/180, 'annotationFrames': [83, 93]},
        {'id': 'smarthome', 'start': .51, 'rest': 108/180, 'annotationFrames': [105, 117]},
        {'id': 'security', 'start': .64, 'rest': 132/180, 'annotationFrames': [125, 135]},
        {'id': 'energy', 'start': .76, 'rest': 162/180, 'annotationFrames': [159, 167]},
    ],
}

EXTERIOR = ((20, -24, 13), (5.7, 4.6, 1.2), 18.8)
REVEAL = ((19, -25, 16), (5.7, 4.6, 1.9), 21.3)
REVEAL_HIGH = ((13, -22, 26), (5.7, 4.65, 2.0), 23.0)
OPEN = ((7.25, -14.4, 32), (5.7, 4.65, 0), 16.3)
TECH = ((5.0, -5.3, 8.6), (9.25, .7, .8), 6.4)
SMART = ((.2, -8, 19), (3.6, 7.0, .6), 10.6)
ENTRY = ((10, -10, 6), (6.4, -.2, 1.10), 5.7)
PV = ((17, -15, 19), (5.7, 5.1, 1.7), 16.8)
SHOTS = [(1, EXTERIOR), (13, EXTERIOR), (31, REVEAL), (39, REVEAL_HIGH), (49, OPEN), (51, OPEN),
         (59, TECH), (67, TECH), (81, OPEN), (93, OPEN),
         (103, SMART), (117, SMART), (125, ENTRY), (135, ENTRY),
         (157, PV), (167, PV), (179, EXTERIOR), (181, EXTERIOR)]

# Labels use actual assembly coordinates, projected through the rendered camera.
LABELS = {
    'planning': [],
    'installation': [('Elektroverteilung', (10.14, 1.42, 1.30), (.27, .16)),
                     ('Netzwerk', (11.03, .40, .95), (.79, .84))],
    'lighting': [('Wohnraumlicht', (1.55, 3.19, 1.45), (.23, .85))],
    'smarthome': [('Beschattung', (2.67, 10.86, 1.65), (.26, .16)),
                 ('KNX-Steuerung', (5.416, 4.15, 1.17), (.73, .86))],
    'security': [('Videosprechanlage', (7.05, -.447, 1.42), (.73, .20))],
    'energy': [('Photovoltaik', (5.57, 4.0, 3.27), (.28, .13))],
}


def key(obj, prop, frame, value):
    setattr(obj, prop, value)
    obj.keyframe_insert(data_path=prop, frame=frame)


def camera_for(profile):
    scene = bpy.context.scene
    config = MANIFEST['profiles'][profile]
    scene.render.resolution_x = config['width']
    scene.render.resolution_y = config['height']
    scene.render.resolution_percentage = 100
    scene.camera = bpy.data.objects['Camera | Web ' + profile]
    return scene.camera


def prepare():
    if Path(bpy.data.filepath).resolve() != SOURCE.resolve():
        raise RuntimeError('Prepare must load the architectural R3 source explicitly.')
    scene = bpy.context.scene
    collection = bpy.data.collections.new('16 Web animation cameras')
    scene.collection.children.link(collection)
    for profile in MANIFEST['profiles']:
        data = bpy.data.cameras.new('Camera | Web ' + profile)
        data.type = 'ORTHO'
        data.clip_end = 250
        cam = bpy.data.objects.new(data.name, data)
        collection.objects.link(cam)
        cam.rotation_mode = 'QUATERNION'
        for frame, (position, target, scale) in SHOTS:
            # Slightly tighter full-house framing on small screens; details retain space for labels.
            if profile == 'mobile' and scale >= 16:
                scale *= .98
            key(cam, 'location', frame, position)
            key(cam, 'rotation_quaternion', frame,
                (Vector(target) - Vector(position)).to_track_quat('-Z', 'Y'))
            key(data, 'ortho_scale', frame, scale)
    # Complete the blind action before the Smart Home chapter's reading position.
    blind = bpy.data.objects['RIG | Bedroom blind']
    blind.animation_data_clear()
    for frame, value in [(1, .015), (97, .015), (107, 1), (133, 1), (149, .015), (181, .015)]:
        key(blind, 'scale', frame, (1, 1, value))
    # Preserve room legibility in the web preview while the local warm lights remain visible.
    scene.frame_set(1)
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.name.startswith('Studio '):
            power = obj.data.energy
            obj.data.animation_data_clear()
            for frame, strength in [(1, 1), (68, 1), (85, .43), (117, .43), (139, 1), (163, 1), (181, .60)]:
                key(obj.data, 'energy', frame, power*strength)
    scene['R3 web source'] = str(SOURCE)
    scene['R3 web revision'] = 'preview: sampled frames, chapter closeups, two viewport profiles'
    scene.frame_set(61)
    camera_for('desktop')
    scene.render.fps = 30
    bpy.ops.wm.save_as_mainfile(filepath=str(WEB), compress=True)
    (OUT / 'manifest.json').write_text(json.dumps(MANIFEST, indent=2) + '\n', encoding='utf-8')
    print('R3_WEB_PREPARED', str(WEB), flush=True)


def export_annotations():
    scene = bpy.context.scene
    result = {}
    for profile, config in MANIFEST['profiles'].items():
        cam = camera_for(profile)
        result[profile] = {}
        for chapter in MANIFEST['chapters']:
            scene.frame_set(1 + round(chapter['rest'] * 180))
            labels = []
            selected = LABELS[chapter['id']][:1] if profile == 'mobile' else LABELS[chapter['id']]
            for text, point, (lx, ly) in selected:
                projected = world_to_camera_view(scene, cam, Vector(point))
                if not (0 <= projected.x <= 1 and 0 <= projected.y <= 1 and projected.z > 0):
                    raise RuntimeError(f'Label outside {profile} frame: {text} {tuple(projected)}')
                labels.append({'text': text, 'x': round(projected.x * config['width'], 2),
                               'y': round((1-projected.y)*config['height'], 2),
                               'labelX': round(lx*config['width'], 2),
                               'labelY': round(ly*config['height'], 2)})
            result[profile][chapter['id']] = labels
    (OUT / 'annotations.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


def render(args):
    scene = bpy.context.scene
    profile = args.profile
    camera_for(profile)
    scene.render.engine = 'CYCLES' if args.cycles else 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    if args.cycles:
        scene.cycles.samples = args.samples
        scene.cycles.use_denoising = True
        scene.render.use_persistent_data = True
    else:
        scene.eevee.taa_render_samples = args.samples
        scene.eevee.use_raytracing = True
        if args.detail:
            scene.eevee.fast_gi_quality = .75
            scene.eevee.fast_gi_step_count = 16
            scene.eevee.fast_gi_ray_count = 4
            scene.eevee.shadow_ray_count = 3
            scene.eevee.ray_tracing_options.screen_trace_quality = .75
        # Dithered alpha produces visible speckles on almost vanished walls.
        for material in bpy.data.materials:
            if material.use_nodes and material.node_tree.nodes.get('Visibility'):
                # The many layered PV meshes need depth-tested transparency;
                # alpha blending sorts them incorrectly behind the roof surface.
                material.surface_render_method = 'DITHERED' if material.name.endswith(' | roof') else 'BLENDED'
            if args.detail and material.name.split(' | ')[0] == 'glass':
                # Thin tinted glazing keeps both animated halves consistent in Eevee.
                # The saved native source retains physical Cycles transmission.
                material.surface_render_method = 'BLENDED'
                material.use_raytrace_refraction = False
                material.use_transparency_overlap = False
                shader = material.node_tree.nodes.get('Principled BSDF')
                shader.inputs['Transmission Weight'].default_value = 0
                shader.inputs['Alpha'].default_value = .22
                shader.inputs['Base Color'].default_value = (.18, .23, .25, 1)
                shader.inputs['Roughness'].default_value = .08
                shader.inputs['Coat Weight'].default_value = .45
        # Shadow catchers are a Cycles feature: keep the floor out of Eevee alpha output.
        bpy.data.objects['White studio floor'].hide_render = True
    frames = range(1, 182, MANIFEST['profiles'][profile]['step']) if args.all else [int(f) for f in args.frames.split(',') if f]
    folder = OUT / 'renders' / profile
    folder.mkdir(parents=True, exist_ok=True)
    for frame in frames:
        target = folder / f'frame-{frame:04d}.png'
        if args.resume and target.exists():
            continue
        scene.frame_set(frame)
        scene.render.filepath = str(target)
        bpy.ops.render.render(write_still=True)
        print('R3_WEB_FRAME', profile, frame, flush=True)


def main():
    global OUT, SOURCE, WEB
    parser = argparse.ArgumentParser()
    parser.add_argument('--detail', action='store_true', help='Use the detailed native source and a separate export directory.')
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--annotations', action='store_true')
    parser.add_argument('--profile', choices=['desktop', 'mobile', 'both'], default='desktop')
    parser.add_argument('--frames', default='')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--cycles', action='store_true')
    parser.add_argument('--samples', type=int, default=16)
    import sys
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.detail:
        OUT = ROOT / 'docs/version-g-qa/blender-v3-r3/web-detail'
        SOURCE = ROOT / 'assets/3d/elektro-hubmann-house-v3-r3-detail.blend'
        WEB = ROOT / 'assets/3d/elektro-hubmann-house-v3-r3-detail-web.blend'
        MANIFEST['revision'] = 'r3-detail-01'
        MANIFEST['assetPath'] = 'images/version-g/house-r3-detail/'
        MANIFEST['profiles']['desktop'].update(width=1200, height=1075)
        MANIFEST['profiles']['mobile'].update(width=720, height=720)
    OUT.mkdir(parents=True, exist_ok=True)
    if args.prepare:
        prepare()
    if args.annotations:
        export_annotations()
    if args.all or args.frames:
        profiles = ['desktop', 'mobile'] if args.profile == 'both' else [args.profile]
        for profile in profiles:
            args.profile = profile
            render(args)


if __name__ == '__main__':
    main()
