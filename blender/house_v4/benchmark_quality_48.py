"""One isolated 48-sample Smart Home comparison, with no native-file save.

blender -b assets/3d/elektro-hubmann-house-v4-continuous-r1-web.blend \
  --python-exit-code 1 --python blender/house_v4/benchmark_quality_48.py

Use regular Python with --plan to inspect the exact settings without rendering.
All output stays in benchmarks/: quality-48-smart.png, its JSON report and
temporary files. Production frames, progress records and website configuration
are never modified.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'blender'))
from house_v4.continuous_delivery import (
    ANIMATION, OUT as PRODUCTION_OUT, REVISION, SETTINGS,
    configure_scene, delivery_lock, inspect_blender_png, now, sha, write_json,
)

FRAME = 771
EXPECTED_ANIMATION_SHA256 = 'ded7efb86c4d89581f223262a61bfc2c6656909157cc3ace07debc33df40255d'
OUT = PRODUCTION_OUT.parent / 'benchmarks'
IMAGE = OUT / 'quality-48-smart.png'
REPORT = OUT / 'quality-48-smart.json'


def specification():
    baseline = {**deepcopy(SETTINGS), 'samples': 96, 'adaptiveThreshold': .025}
    if baseline['size'] != 1200:
        raise RuntimeError('The output dimensions changed; review this comparison before using it again.')
    profile = {**baseline, 'samples': 48, 'adaptiveThreshold': .035}
    actual = sha(ANIMATION)
    if actual != EXPECTED_ANIMATION_SHA256:
        raise RuntimeError('Load the reviewed ded7ef native animation; a different model is not a comparable benchmark.')
    return {'revision': REVISION, 'nativeFrame': FRAME, 'nativeAnimation': str(ANIMATION),
            'nativeAnimationSha256': actual, 'productionBaseline': baseline, 'settings': profile,
            'settingsChanged': ['samples', 'adaptiveThreshold'], 'image': str(IMAGE),
            'report': str(REPORT), 'activated': False, 'visualApproval': False,
            'nativeFileSaved': False, 'productionProfileChanged': False}


def production_reference(spec):
    """Read the preserved 96-sample comparison, never the tuned production job."""
    reference_folder = OUT / 'quality-96-reference'
    progress_path = reference_folder / 'render-progress.json'
    image = reference_folder / 'renders' / f'frame-{FRAME:04d}.png'
    reference = {'image': str(image), 'available': False}
    if not progress_path.is_file() or not image.is_file():
        return reference
    progress = json.loads(progress_path.read_text(encoding='utf-8'))
    job = progress.get('identity', {})
    record = progress.get('completed', {}).get(str(FRAME))
    if not record:
        return reference
    if (job.get('nativeAnimationSha256') != spec['nativeAnimationSha256'] or
            job.get('settings') != spec['productionBaseline'] or sha(image) != record['sha256']):
        raise RuntimeError('The completed production counterpart has different geometry, settings or image provenance.')
    return {**reference, 'available': True, 'sha256': record['sha256'],
            'productionRecordedSeconds': record.get('seconds'),
            'timingNote': 'The production duration may include its older, slower PNG validation.'}


def run():
    import bpy
    if Path(bpy.data.filepath).resolve() != ANIMATION.resolve():
        raise RuntimeError('Open the reviewed continuous-r1-web.blend explicitly.')
    scene = bpy.context.scene
    if scene.get('web_revision') != REVISION or scene.camera is None:
        raise RuntimeError('Expected the saved continuous animation with its active native camera.')
    spec = specification()
    original_frame = scene.frame_current
    report = {**spec, 'blender': bpy.app.version_string, 'startedAt': now(), 'phase': 'preparing',
              'scriptSha256': sha(Path(__file__)), 'productionReference': production_reference(spec)}
    with delivery_lock(OUT):
        write_json(REPORT, report)
        total_started = time.perf_counter()
        try:
            configure_scene(scene, spec['settings'])
            scene.frame_set(FRAME)
            scene.render.film_transparent = spec['settings']['filmTransparent']
            temporary = IMAGE.with_name('quality-48-smart.pending.png')
            scene.render.filepath = str(temporary)
            report.update(phase='rendering', camera=scene.camera.name, updatedAt=now())
            write_json(REPORT, report)
            print('QUALITY_48_SMART_START', json.dumps(spec['settings']), flush=True)
            started = time.perf_counter()
            bpy.ops.render.render(write_still=True)
            report['renderSeconds'] = round(time.perf_counter() - started, 4)
            started = time.perf_counter()
            report['pixels'] = inspect_blender_png(temporary, spec['settings']['size'])
            report['validationSeconds'] = round(time.perf_counter() - started, 4)
            if sha(ANIMATION) != spec['nativeAnimationSha256']:
                raise RuntimeError('The native file changed during the comparison; output was not accepted.')
            temporary.replace(IMAGE)
            report.update(phase='complete', finishedAt=now(), totalSeconds=round(time.perf_counter() - total_started, 4),
                          imageSha256=sha(IMAGE), imageBytes=IMAGE.stat().st_size, nativeAnimationUnchanged=True,
                          productionReference=production_reference(spec))
            write_json(REPORT, report)
            print('QUALITY_48_SMART_COMPLETE', json.dumps(report), flush=True)
        except Exception as exc:
            report.update(phase='failed', error=str(exc), updatedAt=now(),
                          totalSeconds=round(time.perf_counter() - total_started, 4))
            write_json(REPORT, report)
            raise
        finally:
            # Restore the inspected frame in memory. There is deliberately no save.
            scene.frame_set(original_frame)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', action='store_true')
    arguments = (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else
                 [] if '--python' in sys.argv else sys.argv[1:])
    args = parser.parse_args(arguments)
    if args.plan:
        print(json.dumps(specification(), indent=2))
    else:
        run()
