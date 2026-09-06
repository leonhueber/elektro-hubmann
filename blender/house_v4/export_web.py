"""Verify every distinct native frame, encode responsive WebP assets, activate V4.

Run with regular Python and Pillow after web.py --all has finished. No partial
sequence can become active: validation completes before configuration writes.
"""
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image
from motion import FRAME_COUNT, MANIFEST, STEP, schedule

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/version-g-qa/blender-v4/web'


def main():
    frames, aliases = schedule()
    for frame in frames:
        source = OUT/'renders'/f'frame-{frame:04d}.png'
        with Image.open(source) as image:
            if image.size != (1000, 1000):
                raise RuntimeError(f'Wrong frame dimensions: {source} {image.size}')
            image.verify()
    report = {'revision': MANIFEST['revision'], 'nativeFrames': len(frames),
              'timelinePositions': FRAME_COUNT, 'sampledPositions': len(range(1, FRAME_COUNT+1, STEP)),
              'renderer': 'Cycles', 'samples': 12, 'profiles': {}}
    report['nativeSourceSha256'] = hashlib.sha256((ROOT/'assets/3d/elektro-hubmann-house-v4.blend').read_bytes()).hexdigest()
    report['nativeAnimationSha256'] = hashlib.sha256((ROOT/'assets/3d/elektro-hubmann-house-v4-web.blend').read_bytes()).hexdigest()
    for profile, config in MANIFEST['profiles'].items():
        destination = ROOT/'public'/MANIFEST['assetPath']/profile
        destination.mkdir(parents=True, exist_ok=True)
        hashes = {}
        for frame in frames:
            name = f'frame-{frame:04d}.webp'
            with Image.open(OUT/'renders'/f'frame-{frame:04d}.png') as image:
                image = image.convert('RGB')
                if image.size != (config['width'], config['height']):
                    image = image.resize((config['width'], config['height']), Image.Resampling.LANCZOS)
                image.save(destination/name, 'WEBP', quality=88, method=6)
            hashes[name] = hashlib.sha256((destination/name).read_bytes()).hexdigest()
        for chapter in MANIFEST['chapters']:
            frame = 1+round(chapter['rest']*(FRAME_COUNT-1)/STEP)*STEP
            source = aliases.get(str(frame), frame)
            shutil.copyfile(destination/f'frame-{source:04d}.webp', destination/(chapter['id']+'.webp'))
        report['profiles'][profile] = {
            'sequenceBytes': sum((destination/name).stat().st_size for name in hashes),
            'posterBytes': (destination/'planning.webp').stat().st_size,
            'decodedCacheBytes': config['width']*config['height']*4*config['cacheFrames'],
            'sha256': hashes,
        }
    config = ROOT/'src/config'
    (config/'house-v4-manifest.json').write_text(json.dumps(MANIFEST, indent=2)+'\n', encoding='utf-8', newline='\n')
    (config/'house-v4-frames.json').write_text(json.dumps({p: aliases for p in MANIFEST['profiles']}, indent=2)+'\n', encoding='utf-8', newline='\n')
    (OUT/'export-report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({**report, 'profiles': {p: {k:v for k,v in c.items() if k != 'sha256'} for p,c in report['profiles'].items()}}, indent=2))


if __name__ == '__main__':
    main()
