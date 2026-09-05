"""Prepare lightweight white-background proof files from transparent Blender renders."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/version-g-qa/blender-v3-r3'
PREVIEW=OUT/'preview'
PREVIEW.mkdir(exist_ok=True)
labels={
    'open':'R3 | Vollstaendiges Haus - Installation',
    'closed':'R3 | Geschlossenes Haus',
    'plan':'R3 | Grundriss und Raumzugang',
    'lighting':'R3 | Beleuchtung',
    'technical':'R3 | Technikraum',
    'smart-home':'R3 | Smart Home - Beschattung',
    'opening':'R3 | Dachbewegung',
    'closing':'R3 | Abschluss',
    'mobile':'R3 | Mobile Lesbarkeit',
    'security':'R3 | Eingang und Sicherheit',
}
for name in labels:
    path=OUT/(name+'.png')
    if not path.exists():
        continue
    image=Image.open(path).convert('RGBA')
    white=Image.new('RGBA',image.size,'white')
    white.alpha_composite(image)
    rgb=white.convert('RGB')
    rgb.save(PREVIEW/(name+'.jpg'),quality=93,subsampling=0,optimize=True)
    if name in ('open','technical'):
        mobile=rgb.copy()
        mobile.thumbnail((390,460),Image.Resampling.LANCZOS)
        mobile.save(PREVIEW/(name+'-390.jpg'),quality=92,subsampling=0,optimize=True)
    print(name,image.size)
names=[n for n in ['closed','open','plan','lighting','technical','smart-home'] if (PREVIEW/(n+'.jpg')).exists()]
if names:
    sheet=Image.new('RGB',(1440,((len(names)+1)//2)*765),'#f4f3f0')
    draw=ImageDraw.Draw(sheet)
    try:
        font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
    except OSError:
        font=ImageFont.load_default()
    for i,name in enumerate(names):
        x=(i%2)*720;y=(i//2)*765
        thumb=ImageOps.contain(Image.open(PREVIEW/(name+'.jpg')),(700,700),Image.Resampling.LANCZOS)
        sheet.paste(thumb,(x+(720-thumb.width)//2,y+15+(700-thumb.height)//2))
        draw.text((x+25,y+726),labels[name],fill='#202323',font=font)
    sheet.save(PREVIEW/'overview.jpg',quality=92,subsampling=0,optimize=True)
