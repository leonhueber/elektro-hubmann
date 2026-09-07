"""Render the approved B exterior, then activate a complete frontend delivery.

Blender: --python exterior_delivery.py -- --render --resume
Python:  exterior_delivery.py --export
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'blender'))
from house_v4.motion import MANIFEST as BASE_MANIFEST, FRAME_COUNT, STEP, schedule

REVISION = 'v4-scroll-02-exterior-01'
SOURCE = ROOT/'assets/3d/elektro-hubmann-house-v4-exterior-r1.blend'
ANIMATION = ROOT/'assets/3d/elektro-hubmann-house-v4-exterior-r1-web.blend'
OUT = ROOT/'docs/version-g-qa/blender-v4-exterior-r1/frontend'
RENDERS = OUT/'renders'
SETTINGS = {'engine': 'CYCLES', 'size': 1200, 'samples': 64,
            'adaptiveThreshold': .04, 'minimumSamples': 8, 'denoising': True,
            'animatedSeed': False, 'filmTransparent': False, 'filmAnimationMuted': True, 'threads': 12,
            'webpQuality': 90}
MANIFEST = deepcopy(BASE_MANIFEST)
MANIFEST.update(revision=REVISION, assetPath='images/version-g/house-v4-exterior-r1/')
MANIFEST['profiles']['desktop'].update(width=1200, height=1200)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')
    temporary.replace(path)


def identity():
    return {'revision': REVISION, 'nativeAnimationSha256': sha(ANIMATION),
            'settings': SETTINGS, 'frames': schedule()[0]}


def validate_native():
    from house_v4 import exterior
    exterior.validate()


def render_threads():
    return SETTINGS['threads']


def render(args):
    import bpy
    if Path(bpy.data.filepath).resolve() != ANIMATION.resolve():
        raise RuntimeError('Load the approved exterior web animation explicitly.')
    scene = bpy.context.scene
    if scene.get('web_revision') != REVISION or scene.get('exterior_variant') != 'B':
        raise RuntimeError('The loaded model is not the approved B animation.')
    validate_native()
    scene.camera = bpy.data.objects['V4 | Continuous scroll camera']
    scene.render.engine = SETTINGS['engine']
    scene.cycles.samples = SETTINGS['samples']
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = SETTINGS['adaptiveThreshold']
    scene.cycles.adaptive_min_samples = SETTINGS['minimumSamples']
    scene.cycles.use_denoising = True
    scene.cycles.use_animated_seed = False
    scene.cycles.seed = 0
    scene.render.use_persistent_data = True
    scene.render.threads_mode, scene.render.threads = 'FIXED', render_threads()
    scene.render.resolution_x = scene.render.resolution_y = SETTINGS['size']
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    # Render evaluates the keyed scene settings again. Muting this single curve
    # is necessary; assigning film_transparent after frame_set is overwritten.
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
    RENDERS.mkdir(parents=True, exist_ok=True)
    job = identity()
    progress_path = OUT/'render-progress.json'
    previous = json.loads(progress_path.read_text(encoding='utf-8')) if progress_path.exists() else {}
    if previous and previous.get('identity') != job:
        raise RuntimeError('Existing renders use another model or quality profile; use a new delivery revision.')
    progress = previous or {'identity': job, 'blender': bpy.app.version_string, 'completed': {}}
    frames = [int(v) for v in args.frames.split(',')] if args.frames else job['frames']
    if any(frame not in job['frames'] for frame in frames):
        raise RuntimeError('Render only distinct frames from the native schedule.')
    for frame in frames:
        destination = RENDERS/f'frame-{frame:04d}.png'
        record = progress['completed'].get(str(frame))
        if args.resume and record and destination.exists() and sha(destination) == record['sha256']:
            continue
        scene.frame_set(frame)
        scene.render.threads = render_threads()
        # The native world already separates camera rays from illumination.
        # Render its white background in Cycles for every frame so the denoiser
        # also resolves subpixel railing edges and transparency transitions.
        scene.render.film_transparent = False
        temporary = RENDERS/f'frame-{frame:04d}.pending.png'
        scene.render.filepath = str(temporary)
        start = time.perf_counter()
        print('EXTERIOR_FRONTEND_START', frame, 'opaque background', not scene.render.film_transparent, flush=True)
        bpy.ops.render.render(write_still=True)
        temporary.replace(destination)
        progress['completed'][str(frame)] = {'sha256': sha(destination),
            'seconds': round(time.perf_counter()-start, 2), 'bytes': destination.stat().st_size,
            'threads': scene.render.threads}
        write_json(progress_path, progress)
        print('EXTERIOR_FRONTEND_FRAME', frame, progress['completed'][str(frame)]['seconds'],
              len(progress['completed']), '/', len(job['frames']), flush=True)


def export():
    from PIL import Image
    frames, aliases = schedule()
    progress = json.loads((OUT/'render-progress.json').read_text(encoding='utf-8'))
    if progress['identity'] != identity():
        raise RuntimeError('Render provenance no longer matches the native animation.')
    for frame in frames:
        path = RENDERS/f'frame-{frame:04d}.png'
        record = progress['completed'].get(str(frame))
        if not record or not path.exists() or sha(path) != record['sha256']:
            raise RuntimeError(f'Missing or changed native render: {frame}')
        with Image.open(path) as image:
            if image.size != (SETTINGS['size'], SETTINGS['size']):
                raise RuntimeError(f'Wrong image dimensions: {path}')
            image.verify()
    report = {'revision': REVISION, 'nativeFrames': len(frames),
              'timelinePositions': FRAME_COUNT, 'sampledPositions': len(range(1, FRAME_COUNT+1, STEP)),
              'renderer': 'Cycles', 'settings': SETTINGS,
              'nativeSourceSha256': sha(SOURCE), 'nativeAnimationSha256': sha(ANIMATION),
              'blender': progress['blender'], 'profiles': {}}
    for profile, config in MANIFEST['profiles'].items():
        destination = ROOT/'public'/MANIFEST['assetPath']/profile
        destination.mkdir(parents=True, exist_ok=True)
        hashes = {}
        for frame in frames:
            name = f'frame-{frame:04d}.webp'
            with Image.open(RENDERS/f'frame-{frame:04d}.png') as image:
                image = image.convert('RGB')
                if image.size != (config['width'], config['height']):
                    image = image.resize((config['width'], config['height']), Image.Resampling.LANCZOS)
                image.save(destination/name, 'WEBP', quality=SETTINGS['webpQuality'], method=6)
            with Image.open(destination/name) as check:
                if check.size != (config['width'], config['height']):
                    raise RuntimeError(f'Invalid exported profile: {name}')
                check.verify()
            hashes[name] = sha(destination/name)
        for chapter in MANIFEST['chapters']:
            frame = 1+round(chapter['rest']*(FRAME_COUNT-1)/STEP)*STEP
            source = aliases.get(str(frame), frame)
            name = chapter['id']+'.webp'
            shutil.copyfile(destination/f'frame-{source:04d}.webp', destination/name)
            hashes[name] = sha(destination/name)
        report['profiles'][profile] = {'width': config['width'], 'height': config['height'],
            'sequenceBytes': sum((destination/name).stat().st_size for name in hashes if name.startswith('frame-')),
            'posterBytes': (destination/'planning.webp').stat().st_size,
            'decodedCacheBytes': config['width']*config['height']*4*config['cacheFrames'], 'sha256': hashes}
    # A separate asset directory leaves the active sequence usable throughout
    # rendering and encoding. Switch the manifest only after all assets verify.
    write_json(OUT/'export-report.json', report)
    write_json(ROOT/'src/config/house-v4-frames.json', {p: aliases for p in MANIFEST['profiles']})
    write_json(ROOT/'src/config/house-v4-manifest.json', MANIFEST)
    print('EXTERIOR_FRONTEND_ACTIVATED', REVISION, len(frames), 'native frames', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--render', action='store_true')
    action.add_argument('--export', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--frames', default='')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])
    render(args) if args.render else export()
