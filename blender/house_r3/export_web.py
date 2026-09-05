"""Validate a complete sampled R3 sequence, encode it, then switch the web manifest.

Run with regular Python and Pillow. Earlier model assets are preserved.
"""
import hashlib
import argparse
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'docs/version-g-qa/blender-v3-r3/web-preview'


def main():
    global QA
    parser = argparse.ArgumentParser()
    parser.add_argument('--detail', action='store_true')
    args = parser.parse_args()
    if args.detail:
        QA = ROOT / 'docs/version-g-qa/blender-v3-r3/web-detail'
    manifest = json.loads((QA / 'manifest.json').read_text(encoding='utf-8'))
    aliases = {profile: {} for profile in manifest['profiles']}
    report = {'revision': manifest['revision'], 'profiles': {}}
    # Check both sequences before touching the active website configuration.
    for profile, config in manifest['profiles'].items():
        for frame in range(1, manifest['frameCount'] + 1, config['step']):
            source = QA / 'renders' / profile / f'frame-{frame:04d}.png'
            with Image.open(source) as im:
                if im.size != (config['width'], config['height']):
                    raise RuntimeError(f'Unexpected dimensions: {source} {im.size}')
                im.verify()
    for profile, config in manifest['profiles'].items():
        output = ROOT / 'public' / manifest['assetPath'] / profile
        output.mkdir(parents=True, exist_ok=True)
        frames = list(range(1, manifest['frameCount'] + 1, config['step']))
        seen = {}
        total = 0
        for frame in frames:
            source = QA / 'renders' / profile / f'frame-{frame:04d}.png'
            with Image.open(source) as im:
                rgba = im.convert('RGBA')
                white = Image.new('RGBA', rgba.size, 'white')
                white.alpha_composite(rgba)
                rgb = white.convert('RGB')
                digest = hashlib.sha256(rgb.tobytes()).hexdigest()
                if digest in seen:
                    aliases[profile][str(frame)] = seen[digest]
                    continue
                seen[digest] = frame
                target = output / f'frame-{frame:04d}.webp'
                rgb.save(target, 'WEBP', quality=88 if args.detail else 82, method=6)
                total += target.stat().st_size
        for chapter in manifest['chapters']:
            intended = 1 + chapter['rest'] * (manifest['frameCount'] - 1)
            sample = min(frames, key=lambda frame: abs(frame-intended))
            sample = aliases[profile].get(str(sample), sample)
            shutil.copyfile(output / f'frame-{sample:04d}.webp', output / (chapter['id']+'.webp'))
        report['profiles'][profile] = {
            'sampledFrames': len(frames), 'uniqueFrames': len(seen),
            'sequenceBytes': total, 'width': config['width'], 'height': config['height'],
            'posterBytes': (output/'planning.webp').stat().st_size,
        }
    (QA/'export-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    config = ROOT / 'src/config'
    (config/'house-v3-frames.json').write_text(json.dumps(aliases, indent=2)+'\n', encoding='utf-8')
    shutil.copyfile(QA/'annotations.json', config/'house-v3-annotations.json')
    shutil.copyfile(QA/'manifest.json', config/'house-v3-manifest.json')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
