"""Verified, resumable delivery of the continuous native house animation.

Blender: continuous_delivery.py -- --render --resume
Blender: continuous_delivery.py -- --render --preview --frames 1,397,771,1089,1369
Python:  continuous_delivery.py --verify
Python:  continuous_delivery.py --export --resume [--orientation path/to/source.json]

Preview files can never activate the website. No command commits or pushes Git.
"""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'blender'))
from house_v4.continuous_motion import CHAPTERS, FRAME_COUNT, REVISION, STEP, schedule

ANIMATION = ROOT / 'assets/3d/elektro-hubmann-house-v4-continuous-r1-web.blend'
OUT = ROOT / 'docs/version-g-qa/blender-v4-continuous-r1/frontend'
RENDERS = OUT / 'renders'
SETTINGS = {
    'engine': 'CYCLES', 'size': 1200, 'samples': 48,
    'adaptiveThreshold': .035, 'minimumSamples': 8, 'denoising': True,
    'seed': 0, 'animatedSeed': False, 'threads': 12,
    'persistentData': True, 'filmTransparent': False, 'filmAnimationMuted': True,
}
PREVIEW_SETTINGS = {**SETTINGS, 'size': 640, 'samples': 16}
ENCODING = {'desktop': 92, 'mobile': 90}
MANIFEST = {
    'version': 4, 'revision': REVISION, 'frameCount': FRAME_COUNT,
    'assetPath': 'images/version-g/house-v4-continuous-r1/',
    'profiles': {
        'desktop': {'width': 1200, 'height': 1200, 'step': STEP, 'cacheFrames': 12},
        'mobile': {'width': 720, 'height': 720, 'step': STEP, 'cacheFrames': 18},
    },
    'chapters': deepcopy(CHAPTERS),
}


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')
    temporary.replace(path)


@contextmanager
def delivery_lock(folder):
    """OS-held lock is released even if Blender crashes; no stale PID lock."""
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / '.delivery.lock').open('a+b') as handle:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        if sys.platform == 'win32':
            import msvcrt
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RuntimeError('Another delivery process already uses ' + str(folder)) from exc
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise RuntimeError('Another delivery process already uses ' + str(folder)) from exc
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)


def identity(preview=False):
    return {
        'revision': REVISION, 'mode': 'preview' if preview else 'production',
        'nativeAnimationSha256': sha(ANIMATION),
        'settings': deepcopy(PREVIEW_SETTINGS if preview else SETTINGS),
        'frameCount': FRAME_COUNT, 'step': STEP, 'frames': schedule()[0],
    }


def preview_folder(job):
    digest = hashlib.sha256(json.dumps(job, sort_keys=True).encode()).hexdigest()[:16]
    return OUT / 'preview' / digest


def load_progress(path, job):
    if not path.exists():
        return {'identity': job, 'startedAt': now(), 'completed': {}}
    progress = json.loads(path.read_text(encoding='utf-8'))
    if progress.get('identity') != job:
        raise RuntimeError('Render identity changed: use a new delivery revision; existing frames are preserved.')
    return progress


def status(path, phase, job, completed=0, total_frames=None, **extra):
    total = total_frames if total_frames is not None else len(job['frames'])
    write_json(path, {
        'revision': REVISION, 'mode': job['mode'], 'phase': phase,
        'updatedAt': now(), 'completedFrames': completed, 'totalFrames': total,
        'progressPercent': round(100 * completed / total, 2),
        'nativeAnimationSha256': job['nativeAnimationSha256'], **extra,
    })


def pixel_metrics(values):
    """Reject black, white and uniform empty output, including dithered black."""
    values = list(values)
    if not values or any(not math.isfinite(value) for value in values):
        raise RuntimeError('Invalid or missing image pixels.')
    low, high = min(values), max(values)
    mean = sum(values) / len(values)
    deviation = math.sqrt(sum((value - mean) ** 2 for value in values) / len(values))
    if high <= .012 or low >= .985 or high - low < .01 or deviation < .003:
        raise RuntimeError('Black or empty render: insufficient visible image content.')
    return {'minimum': round(low, 6), 'maximum': round(high, 6),
            'mean': round(mean, 6), 'standardDeviation': round(deviation, 6)}


def png_dimensions(path):
    with path.open('rb') as source:
        header = source.read(33)
    if len(header) != 33 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise RuntimeError('Invalid PNG header: ' + str(path))
    width, height = struct.unpack('>II', header[16:24])
    if header[24] != 8 or header[25] != 2:
        raise RuntimeError('Expected an 8-bit RGB native PNG: ' + str(path))
    return width, height


def inspect_blender_png(path, size):
    """Blender has no Pillow dependency; inspect a sampled loaded PNG buffer."""
    from array import array
    import bpy
    if png_dimensions(path) != (size, size):
        raise RuntimeError('Wrong native frame dimensions: ' + str(path))
    image = bpy.data.images.load(str(path), check_existing=False)
    try:
        if tuple(image.size) != (size, size) or image.channels < 3:
            raise RuntimeError('Blender could not decode the complete frame: ' + str(path))
        stride = max(1, size // 64)
        channels = image.channels
        pixels = array('f', [0.0]) * len(image.pixels)
        image.pixels.foreach_get(pixels)
        values = []
        for y in range(stride // 2, size, stride):
            for x in range(stride // 2, size, stride):
                offset = (y * size + x) * channels
                red, green, blue = pixels[offset:offset + 3]
                values.append(.2126 * red + .7152 * green + .0722 * blue)
        return pixel_metrics(values)
    finally:
        bpy.data.images.remove(image)


def inspect_image(path, dimensions, image_format='PNG'):
    from PIL import Image
    with Image.open(path) as image:
        if image.format != image_format or image.size != tuple(dimensions):
            raise RuntimeError('Wrong format or dimensions: ' + str(path))
        image.verify()
    with Image.open(path) as image:
        image.load()
        sample = image.convert('L')
        sample.thumbnail((64, 64), Image.Resampling.BOX)
        return pixel_metrics(value / 255 for value in sample.tobytes())


def requested_frames(value, available, preview=False):
    if preview and not value:
        raise RuntimeError('Preview requires an explicit --frames list.')
    try:
        frames = list(dict.fromkeys(int(item.strip()) for item in value.split(','))) if value else available
    except ValueError as exc:
        raise RuntimeError('Frames must be comma-separated native frame numbers.') from exc
    if not frames or any(frame not in available for frame in frames):
        raise RuntimeError('Choose sampled native frames from 1 to ' + str(FRAME_COUNT) + ' at step ' + str(STEP))
    return frames


def configure_scene(scene, settings):
    import bpy
    scene.render.engine = settings['engine']
    scene.cycles.device = 'CPU'
    scene.cycles.samples = settings['samples']
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = settings['adaptiveThreshold']
    scene.cycles.adaptive_min_samples = settings['minimumSamples']
    scene.cycles.use_denoising = settings['denoising']
    scene.cycles.use_animated_seed = settings['animatedSeed']
    scene.cycles.seed = settings['seed']
    scene.render.use_persistent_data = settings['persistentData']
    scene.render.threads_mode, scene.render.threads = 'FIXED', settings['threads']
    scene.render.resolution_x = scene.render.resolution_y = settings['size']
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag = strip.channelbag(slot)
                    if bag:
                        for curve in bag.fcurves:
                            if curve.data_path == 'render.film_transparent':
                                curve.mute = True
    scene.render.film_transparent = settings['filmTransparent']


def render(args):
    import bpy
    if Path(bpy.data.filepath).resolve() != ANIMATION.resolve():
        raise RuntimeError('Load the continuous native animation explicitly.')
    scene = bpy.context.scene
    if scene.get('web_revision') != REVISION or not scene.camera:
        raise RuntimeError('The saved scene is not the expected continuous animation with an active camera.')
    job = identity(args.preview)
    selected = requested_frames(args.frames, job['frames'], args.preview)
    if not args.frames and not args.preview:
        # Render the actual navigation views first for early visual inspection.
        # This changes processing order only; every motion frame is still required.
        posters = [1] + [1 + round(chapter['rest'] * (FRAME_COUNT-1) / STEP) * STEP
                         for chapter in CHAPTERS]
        selected = list(dict.fromkeys([frame for frame in posters if frame in selected] + selected))
    folder = preview_folder(job) if args.preview else OUT
    renders = folder / 'renders' if args.preview else RENDERS
    status_path = folder / 'pipeline-status.json'
    settings = job['settings']
    with delivery_lock(folder):
        progress_path = folder / 'render-progress.json'
        progress = load_progress(progress_path, job)
        if progress['completed'] and not args.resume:
            raise RuntimeError('Verified frames already exist. Pass --resume to continue safely.')
        progress['blender'] = bpy.app.version_string
        renders.mkdir(parents=True, exist_ok=True)
        configure_scene(scene, settings)
        total = len(selected) if args.preview else len(job['frames'])

        def completed_count():
            return (sum(str(frame) in progress['completed'] for frame in selected)
                    if args.preview else len(progress['completed']))

        try:
            for frame in selected:
                destination = renders / f'frame-{frame:04d}.png'
                record = progress['completed'].get(str(frame))
                if args.resume and record and destination.is_file() and sha(destination) == record['sha256']:
                    inspect_blender_png(destination, settings['size'])
                    continue
                status(status_path, 'rendering', job, completed_count(), total_frames=total,
                       currentFrame=frame, selectedFrames=len(selected), outputDirectory=str(renders))
                scene.frame_set(frame)
                scene.render.film_transparent = settings['filmTransparent']
                temporary = renders / f'frame-{frame:04d}.pending.png'
                scene.render.filepath = str(temporary)
                started = time.perf_counter()
                print('CONTINUOUS_RENDER_START', frame, flush=True)
                bpy.ops.render.render(write_still=True)
                pixels = inspect_blender_png(temporary, settings['size'])
                if sha(ANIMATION) != job['nativeAnimationSha256']:
                    raise RuntimeError('Native source changed during rendering; rendered output was not accepted.')
                temporary.replace(destination)
                progress['completed'][str(frame)] = {
                    'sha256': sha(destination), 'seconds': round(time.perf_counter() - started, 2),
                    'bytes': destination.stat().st_size, 'pixels': pixels,
                }
                write_json(progress_path, progress)
                print('CONTINUOUS_RENDER_VERIFIED', frame, len(progress['completed']), '/', len(job['frames']), flush=True)
            expected = selected if args.preview else job['frames']
            present = set(progress['completed'])
            finished = all(str(frame) in present for frame in expected)
            if finished:
                for frame in expected:
                    image = renders / f'frame-{frame:04d}.png'
                    if not image.is_file() or sha(image) != progress['completed'][str(frame)]['sha256']:
                        raise RuntimeError('Completed frame is missing or changed: ' + str(frame))
                    inspect_blender_png(image, settings['size'])
            phase = 'preview_complete' if args.preview else 'rendered' if finished else 'partial'
            status(status_path, phase, job, completed_count(), total_frames=total, selectedFrames=len(selected),
                   outputDirectory=str(renders), activated=False)
        except Exception as exc:
            status(status_path, 'failed', job, completed_count(), total_frames=total, error=str(exc), activated=False)
            raise


def verified_production(job=None):
    job = job or identity()
    progress = load_progress(OUT / 'render-progress.json', job)
    for frame in job['frames']:
        image = RENDERS / f'frame-{frame:04d}.png'
        record = progress['completed'].get(str(frame))
        if not record or not image.is_file() or sha(image) != record['sha256']:
            raise RuntimeError('Missing or changed production frame: ' + str(frame))
        inspect_image(image, (SETTINGS['size'], SETTINGS['size']))
    return progress


def orientation_source(path):
    if not path:
        return None
    path = Path(path).resolve()
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, (dict, list)):
        raise RuntimeError('Orientation source must contain a JSON object or array.')
    return {'path': str(path), 'sha256': sha(path)}


def activate(manifest, aliases, expected_config):
    """Prepare both files, guard concurrent edits and restore on replace failure."""
    config = ROOT / 'src/config'
    values = {'house-v4-frames.json': {profile: aliases for profile in manifest['profiles']},
              'house-v4-manifest.json': manifest}
    config.mkdir(parents=True, exist_ok=True)
    for name, previous in expected_config.items():
        path = config / name
        if (path.read_bytes() if path.exists() else None) != previous:
            raise RuntimeError('Website configuration changed during export; verified assets remain unactivated.')
    prepared = {}
    for name, value in values.items():
        path = config / (name + '.pending')
        path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')
        prepared[name] = path
    replaced = []
    try:
        for name, path in prepared.items():
            path.replace(config / name)
            replaced.append(name)
    except Exception:
        for name in replaced:
            old = expected_config[name]
            path = config / name
            if old is None:
                path.unlink()
            else:
                temporary = config / (name + '.rollback')
                temporary.write_bytes(old)
                temporary.replace(path)
        raise


def export(resume=False, orientation=None):
    from PIL import Image
    if orientation is None:
        candidate = ROOT / 'src/config/house-v4-orientation.json'
        orientation = candidate if candidate.is_file() else None
    job = identity()
    with delivery_lock(OUT):
        config = ROOT / 'src/config'
        expected_config = {name: (config / name).read_bytes() if (config / name).exists() else None
                           for name in ['house-v4-frames.json', 'house-v4-manifest.json']}
        status_path = OUT / 'pipeline-status.json'
        activated = False
        try:
            status(status_path, 'validating', job)
            progress = verified_production(job)
            orientation_record = orientation_source(orientation)
            frames, aliases = schedule()
            export_job = {'render': job, 'manifest': MANIFEST, 'webpQuality': ENCODING}
            export_path = OUT / 'export-progress.json'
            encoded = load_progress(export_path, export_job)
            report = {'revision': REVISION, 'nativeFrames': len(frames), 'timelinePositions': FRAME_COUNT,
                      'renderer': 'Cycles', 'settings': SETTINGS, 'blender': progress.get('blender'),
                      'nativeAnimationSha256': job['nativeAnimationSha256'], 'profiles': {},
                      'orientationSource': orientation_record}
            for profile, dimensions in MANIFEST['profiles'].items():
                destination = ROOT / 'public' / MANIFEST['assetPath'] / profile
                destination.mkdir(parents=True, exist_ok=True)
                hashes = {}
                for index, frame in enumerate(frames):
                    name = f'frame-{frame:04d}.webp'
                    target = destination / name
                    key = profile + '/' + name
                    previous = encoded['completed'].get(key)
                    if not (resume and previous and target.is_file() and sha(target) == previous['sha256']):
                        temporary = target.with_name(target.stem + '.pending.webp')
                        with Image.open(RENDERS / f'frame-{frame:04d}.png') as source:
                            image = source.convert('RGB')
                            if image.size != (dimensions['width'], dimensions['height']):
                                image = image.resize((dimensions['width'], dimensions['height']), Image.Resampling.LANCZOS)
                            image.save(temporary, 'WEBP', quality=ENCODING[profile], method=6)
                        inspect_image(temporary, (dimensions['width'], dimensions['height']), 'WEBP')
                        temporary.replace(target)
                        encoded['completed'][key] = {'sha256': sha(target)}
                        write_json(export_path, encoded)
                    hashes[name] = sha(target)
                    status(status_path, 'exporting', job, len(frames), profile=profile,
                           encodedFrames=index + 1, profileFrames=len(frames), activated=False)
                for chapter in CHAPTERS:
                    frame = 1 + round(chapter['rest'] * (FRAME_COUNT - 1) / STEP) * STEP
                    source = aliases.get(str(frame), frame)
                    name = chapter['id'] + '.webp'
                    shutil.copyfile(destination / f'frame-{source:04d}.webp', destination / name)
                    hashes[name] = sha(destination / name)
                report['profiles'][profile] = {
                    'width': dimensions['width'], 'height': dimensions['height'], 'webpQuality': ENCODING[profile],
                    'sequenceBytes': sum((destination / name).stat().st_size for name in hashes if name.startswith('frame-')),
                    'posterBytes': (destination / 'planning.webp').stat().st_size,
                    'decodedCacheBytes': dimensions['width'] * dimensions['height'] * 4 * dimensions['cacheFrames'],
                    'sha256': hashes,
                }
            # Recheck every produced asset before the manifest can name it.
            status(status_path, 'validating_export', job, len(frames), activated=False)
            for profile, details in report['profiles'].items():
                folder = ROOT / 'public' / MANIFEST['assetPath'] / profile
                for name, digest in details['sha256'].items():
                    if sha(folder / name) != digest:
                        raise RuntimeError('Exported asset changed: ' + name)
                    inspect_image(folder / name, (details['width'], details['height']), 'WEBP')
            if identity() != job or orientation_source(orientation) != orientation_record:
                raise RuntimeError('Native animation or orientation source changed during export.')
            report['validatedAt'] = now()
            write_json(OUT / 'export-report.json', report)
            activate(MANIFEST, aliases, expected_config)
            activated = True
            status(status_path, 'complete', job, len(frames), activated=True, assetPath=MANIFEST['assetPath'])
            print('CONTINUOUS_ACTIVATED', REVISION, len(frames), 'verified native frames', flush=True)
            return report
        except Exception as exc:
            status(status_path, 'failed', job, error=str(exc), activated=activated)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--render', action='store_true')
    action.add_argument('--export', action='store_true')
    action.add_argument('--verify', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--frames', default='')
    parser.add_argument('--orientation', help='Read-only JSON source recorded in the export report.')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:])
    if args.preview and not args.render:
        parser.error('--preview is valid only with --render and never exports or activates assets.')
    if args.frames and not args.render:
        parser.error('--frames is valid only with --render.')
    if args.render:
        render(args)
    elif args.export:
        export(args.resume, args.orientation)
    else:
        with delivery_lock(OUT):
            verified_production()
        print('CONTINUOUS_PRODUCTION_VERIFIED', len(schedule()[0]), 'native frames', flush=True)


if __name__ == '__main__':
    main()
