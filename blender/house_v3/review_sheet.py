"""Create a compact review sheet from the final exported chapter posters."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
manifest=json.loads((ROOT/'src/config/house-v3-manifest.json').read_text(encoding='utf-8'))
names=['Planung','Installation','Beleuchtung','Smart Home','Sicherheit','Photovoltaik']
sheet=Image.new('RGB',(1800,1200),'#f5f4f1')
draw=ImageDraw.Draw(sheet)
font_path=Path('C:/Windows/Fonts/segoeui.ttf')
font=ImageFont.truetype(str(font_path),22) if font_path.exists() else ImageFont.load_default()
title=ImageFont.truetype(str(font_path),32) if font_path.exists() else font
draw.text((35,20),'Elektro Hubmann · Haus V3',fill='#242629',font=title)
for index,chapter in enumerate(manifest['chapters']):
    x=20+(index%3)*595;y=85+(index//3)*550
    card=Image.new('RGB',(575,525),'white')
    with Image.open(ROOT/'public'/manifest['assetPath']/'desktop'/(chapter['id']+'.webp')) as image:
        image.thumbnail((555,465),Image.Resampling.LANCZOS)
        card.paste(image,((575-image.width)//2,8))
    sheet.paste(card,(x,y))
    draw.text((x+22,y+483),f'{index+1:02}  {names[index]}',fill='#25272a',font=font)
out=ROOT/'docs/version-g-qa/blender-v3/storyboard.jpg'
sheet.save(out,quality=92)
for proof in (out.parent/'proofs').glob('frame-*.png'):
    final=out.parent/'renders'/'desktop'/proof.name
    if final.exists():
        proof.write_bytes(final.read_bytes())
print(out)
