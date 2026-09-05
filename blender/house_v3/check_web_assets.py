"""Check the exported contract, dimensions, budgets and complete frame coverage."""
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'src/config/house-v3-manifest.json').read_text(encoding='utf-8'))
aliases=json.loads((ROOT/'src/config/house-v3-frames.json').read_text(encoding='utf-8'))
report={}
for profile,config in manifest['profiles'].items():
    folder=ROOT/'public'/manifest['assetPath']/profile
    expected=set()
    for frame in range(1,manifest['frameCount']+1,config['step']):
        source=aliases[profile].get(str(frame),frame)
        assert 1<=source<=manifest['frameCount'] and (source-1)%config['step']==0
        expected.add(folder/f'frame-{source:04d}.webp')
    expected.update(folder/(chapter['id']+'.webp') for chapter in manifest['chapters'])
    for file in expected:
        assert file.exists(), f'Missing web asset: {file}'
        with Image.open(file) as image:
            assert image.size==(config['width'],config['height']),str(file)
            assert image.mode=='RGB',str(file)
    actual=set(folder.glob('*.webp'))
    assert expected==actual,f'Unexpected generated assets: {actual-expected}'
    sequence=sum(p.stat().st_size for p in expected if p.name.startswith('frame-'))
    budget=(12 if profile=='desktop' else 5)*1024*1024
    assert sequence<budget,f'{profile} exceeds sequence budget'
    assert (folder/'planning.webp').stat().st_size<250_000
    report[profile]={'complete':True,'files':len(expected),'sequenceBytes':sequence,'budgetBytes':budget}
(ROOT/'docs/version-g-qa/blender-v3/asset-validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
