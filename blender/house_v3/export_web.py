"""Convert actual Blender output into bounded, opaque WebP frames and posters.

Run with normal Python + Pillow, after rendering both profiles. --pilot uses
the sparse proof images only, for an early local player check.
"""
import argparse
import json
import hashlib
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
MANIFEST=json.loads((ROOT/'src/config/house-v3-manifest.json').read_text(encoding='utf-8'))
if str(MANIFEST.get('revision', '')).startswith('r3'):
    raise SystemExit('R3 is active. Use blender/house_r3/export_web.py; this legacy exporter must not replace R3 assets.')
QA=ROOT/'docs/version-g-qa/blender-v3'
OUT=ROOT/'public'/MANIFEST['assetPath']


def convert(source,destination,size,quality):
    with Image.open(source) as source_image:
        rgba=source_image.convert('RGBA')
        result=Image.new('RGBA',rgba.size,'white')
        result.alpha_composite(rgba)
        result=result.convert('RGB')
        if result.size!=size:
            result.thumbnail(size,Image.Resampling.LANCZOS)
            canvas=Image.new('RGB',size,'white')
            canvas.paste(result,((size[0]-result.width)//2,(size[1]-result.height)//2))
            result=canvas
        result.save(destination,'WEBP',quality=quality,method=6)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    parser.add_argument('--quality',type=int,default=80)
    args=parser.parse_args()
    report={'pilot':args.pilot,'profiles':{}}
    aliases={'desktop':{},'mobile':{}}
    for profile,config in MANIFEST['profiles'].items():
        output=OUT/profile
        output.mkdir(parents=True,exist_ok=True)
        source_dir=QA/'proofs' if args.pilot else QA/'renders'/profile
        frames=list(range(1,MANIFEST['frameCount']+1,config['step']))
        if args.pilot:
            frames=[int(p.stem.split('-')[1]) for p in source_dir.glob('frame-*.png')]
        missing=[frame for frame in frames if not (source_dir/f'frame-{frame:04d}.png').exists()]
        if missing:
            raise RuntimeError(f'{profile}: missing render frames {missing}')
        if not frames:
            raise RuntimeError(f'{profile}: no rendered source frames')
        size=(config['width'],config['height'])
        seen={}
        for frame in frames:
            source=source_dir/f'frame-{frame:04d}.png'
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            if digest in seen and not args.pilot:
                aliases[profile][str(frame)]=seen[digest]
                # Remove only a stale generated V3 frame from a previous export.
                stale=output/f'frame-{frame:04d}.webp'
                if stale.exists():
                    stale.unlink()
            else:
                convert(source,output/f'frame-{frame:04d}.webp',size,args.quality)
                seen[digest]=frame
        for chapter in MANIFEST['chapters']:
            rest=round(chapter['rest']*(MANIFEST['frameCount']-1))+1
            nearest=min(frames,key=lambda frame:abs(frame-rest))
            nearest=aliases[profile].get(str(nearest),nearest)
            (output/(chapter['id']+'.webp')).write_bytes((output/f'frame-{nearest:04d}.webp').read_bytes())
        if not args.pilot:
            expected={f'frame-{frame:04d}.webp' for frame in frames if str(frame) not in aliases[profile]}
            for stale in output.glob('frame-*.webp'):
                if stale.name not in expected:
                    stale.unlink()
        total=sum((output/f'frame-{frame:04d}.webp').stat().st_size for frame in frames if str(frame) not in aliases[profile])
        report['profiles'][profile]={'frames':len(frames),'uniqueFrames':len(frames)-len(aliases[profile]),'sequenceBytes':total,
                                    'posterBytes':(output/'planning.webp').stat().st_size,
                                    'width':size[0],'height':size[1]}
    (QA/'web-export.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if not args.pilot:
        (ROOT/'src/config/house-v3-frames.json').write_text(json.dumps(aliases,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
