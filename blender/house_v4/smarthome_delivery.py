"""Render Smart Home A and reuse verified, unchanged native B exterior frames."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'blender'))
from house_v4 import exterior_delivery as delivery
from house_v4.smarthome_motion import REVISION, schedule, changed

BASE_OUT = delivery.OUT
BASE_ANIMATION = delivery.ANIMATION
BASE_IDENTITY = delivery.identity()
BASE_SETTINGS = deepcopy(delivery.SETTINGS)
BASE_ALIAS = delivery.schedule()[1]
delivery.REVISION = REVISION
delivery.SOURCE = ROOT/'assets/3d/elektro-hubmann-house-v4-smarthome-r1.blend'
delivery.ANIMATION = ROOT/'assets/3d/elektro-hubmann-house-v4-smarthome-r1-web.blend'
delivery.OUT = ROOT/'docs/version-g-qa/blender-v4-smarthome-r1/frontend'
delivery.RENDERS = delivery.OUT/'renders'
delivery.SETTINGS = {**BASE_SETTINGS, 'concurrentExteriorThreads': 4}
delivery.schedule = schedule
delivery.MANIFEST = deepcopy(delivery.MANIFEST)
delivery.MANIFEST.update(revision=REVISION, assetPath='images/version-g/house-v4-smarthome-r1/')


def validate_source():
    proof = json.loads((delivery.OUT.parent/'web-validation.json').read_text(encoding='utf-8'))
    if (not proof['allPassed'] or proof['outsideChanges'] or proof['outsideFramesVerified'] < 600
            or proof['sha256'] != delivery.sha(delivery.ANIMATION)
            or proof['baseSha256'] != delivery.sha(BASE_ANIMATION)):
        raise RuntimeError('Native outside-frame validation no longer matches the saved sources.')
    return proof


def validate_native():
    import bpy
    validate_source()
    scene = bpy.context.scene
    if scene.get('smarthome_revision') != REVISION:
        raise RuntimeError('Expected selected native Smart Home A.')
    if len([o for o in scene.objects if o.get('smart_blind')]) != 15:
        raise RuntimeError('Native blind slats missing.')
    if bpy.data.objects['Smart A | room controller'].get('mounting_height_m') != 1.22:
        raise RuntimeError('Room controller missing or changed.')


delivery.validate_native = validate_native


def render_threads():
    status = BASE_OUT/'pipeline-status.json'
    if status.exists() and json.loads(status.read_text(encoding='utf-8'))['phase'] != 'complete':
        return delivery.SETTINGS['concurrentExteriorThreads']
    return delivery.SETTINGS['threads']


delivery.render_threads = render_threads


def reuse():
    proof = validate_source()
    source = json.loads((BASE_OUT/'render-progress.json').read_text(encoding='utf-8'))
    if source['identity'] != BASE_IDENTITY:
        raise RuntimeError('Base exterior renders have a different model or quality identity.')
    path = delivery.OUT/'render-progress.json'
    progress = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {
        'identity': delivery.identity(), 'blender': source['blender'], 'completed': {}}
    if progress['identity'] != delivery.identity():
        raise RuntimeError('Smart Home render identity changed.')
    delivery.RENDERS.mkdir(parents=True, exist_ok=True)
    for frame in schedule()[0]:
        if changed(frame):
            continue
        original = BASE_ALIAS.get(str(frame), frame)
        if proof['reuse'].get(str(frame)) != original:
            raise RuntimeError('Frame reuse does not match the native validation.')
        record = source['completed'].get(str(original))
        native = BASE_OUT/'renders'/f'frame-{original:04d}.png'
        if not record or not native.is_file() or delivery.sha(native) != record['sha256']:
            raise RuntimeError('Missing or changed base render: '+str(original))
        destination = delivery.RENDERS/f'frame-{frame:04d}.png'
        shutil.copyfile(native, destination)
        progress['completed'][str(frame)] = {
            **record, 'reusedFrom': f'blender-v4-exterior-r1/frontend/renders/frame-{original:04d}.png',
            'sourceAnimationSha256': BASE_IDENTITY['nativeAnimationSha256']}
    delivery.write_json(path, progress)
    print('SMART_HOME_REUSED', len(proof['reuse']), 'verified native frames', flush=True)


def export():
    validate_source()
    delivery.export()
    report_path = delivery.OUT/'export-report.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    report.update(selectedSmartHomeVariant='A', changedNativeFrames=sum(changed(f) for f in schedule()[0]),
                  reusedNativeFrames=sum(not changed(f) for f in schedule()[0]),
                  baseAnimationSha256=BASE_IDENTITY['nativeAnimationSha256'],
                  reuseValidation='../web-validation.json')
    delivery.write_json(report_path, report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--render', action='store_true')
    action.add_argument('--reuse', action='store_true')
    action.add_argument('--export', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--frames', default='')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:])
    if args.render:
        validate_source()
        args.frames = args.frames or ','.join(str(f) for f in schedule()[0] if changed(f))
        delivery.render(args)
    elif args.reuse:
        reuse()
    else:
        export()
