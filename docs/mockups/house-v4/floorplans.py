"""Draw reproducible, schematic SVG plans; no raster mockup manipulation."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent
S, X, Y = 75, 210, 1035


class Plan:
    def __init__(self, floor, subtitle):
        self.parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200" role="img" aria-labelledby="title desc">
<title id="title">Haus V4 – {floor}</title><desc id="desc">{escape(subtitle)}. Schematische Entwurfsgrundlage, Eingang unten.</desc>
<defs><pattern id="oak" width="26" height="115" patternUnits="userSpaceOnUse"><rect width="26" height="115" fill="#f1e8d9"/><path d="M0 0V115M0 114H26" stroke="#e4d8c7" stroke-width=".8"/></pattern><pattern id="tile" width="45" height="45" patternUnits="userSpaceOnUse"><rect width="45" height="45" fill="#e5e6e3"/><path d="M0 0H45V45" fill="none" stroke="#cbd0cb" stroke-width="1"/></pattern></defs>
<rect width="1200" height="1200" fill="#fafaf7"/>
<text x="80" y="65" font-family="Arial,sans-serif" font-size="14" font-weight="700" fill="#ba1325" letter-spacing="2">ELEKTRO HUBMANN / HAUS V4</text>
<text x="80" y="125" font-family="Arial,sans-serif" font-size="44" font-weight="700" fill="#222826">{floor}</text>
<text x="80" y="163" font-family="Arial,sans-serif" font-size="18" fill="#67706a">{escape(subtitle)}</text>''']
        self.rect(0, 0, 9.6, 10.8, '#4d5550')
        self.rect(.3, .3, 9, 10.2, 'url(#oak)')

    def point(self, x, y):
        return X+x*S, Y-y*S

    def rect(self, x, y, w, h, fill, stroke='none', radius=0, width=1):
        px, py = self.point(x, y+h)
        self.parts.append(f'<rect x="{px:.2f}" y="{py:.2f}" width="{w*S:.2f}" height="{h*S:.2f}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')

    def line(self, x, y, x2, y2, color='#646e67', width=1, dash=''):
        a,b = self.point(x,y); c,d = self.point(x2,y2)
        self.parts.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')

    def text(self, x, y, value, size=16, color='#303a33', weight=600):
        a,b = self.point(x,y)
        self.parts.append(f'<text x="{a}" y="{b}" text-anchor="middle" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>')

    def circle(self,x,y,r,fill='#ddd2c1',stroke='#b0a590'):
        a,b=self.point(x,y)
        self.parts.append(f'<circle cx="{a}" cy="{b}" r="{r*S}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')

    def wall(self,x,y,w,h): self.rect(x,y,w,h,'#677169')
    def furniture(self,x,y,w,h,color='#e0d8cc',radius=5): self.rect(x,y,w,h,color,'#a79e90',radius,1.1)

    def door(self,x,y,orientation='vertical',direction=1):
        # Opening cut plus a schematic open leaf. Door sweeps require Blender validation.
        if orientation=='vertical':
            self.rect(x-.025,y-.025,.2,1.0,'#f1e8d9')
            self.line(x+.075,y,x+.075+direction*.9,y,'#a3865c',2)
            self.line(x+.075+direction*.9,y,x+.075,y+.9,'#bfb6a7',.8,'3 3')
        else:
            self.rect(x-.025,y-.025,1.0,.2,'#f1e8d9')
            self.line(x,y+.075,x,y+.075+direction*.9,'#a3865c',2)
            self.line(x,y+.075+direction*.9,x+.9,y+.075,'#bfb6a7',.8,'3 3')

    def window(self,x,y,w,h):
        self.rect(x,y,w,h,'#f6fcfd','#384540',0,2)
        if w>h: self.line(x,y+h/2,x+w,y+h/2,'#90a2a0',1)
        else: self.line(x+w/2,y,x+w/2,y+h,'#90a2a0',1)

    def stairs(self,upper=False):
        self.rect(3.95,6.7,2.35,3.8,'#fafaf7','#8d968e',0,1.5)
        self.rect(4.05,9.55,2.15,.8,'#dacfbc','#a79e90')
        for i in range(10):
            y=6.85+i*.3
            self.line(4.05,y,5.05,y,'#a79e90',1)
            self.line(5.20,y,6.20,y,'#a79e90',1)
        self.line(5.125,6.75,5.125,9.55,'#6f7770',3)
        self.line(4.55,7.05,4.55,9.2,'#bd2030',1.8)
        self.line(4.55,9.2,4.45,8.98,'#bd2030',1.8)
        self.line(4.55,9.2,4.65,8.98,'#bd2030',1.8)
        self.text(5.1,6.38,'Treppe / Podest',13)

    def bed(self,x,y,w,h):
        self.furniture(x-.06,y-.06,w+.12,h+.15,'#cbb593')
        self.furniture(x,y,w,h,'#eee9df',8)
        for j in range(2 if w>1.4 else 1):
            n=2 if w>1.4 else 1
            self.furniture(x+.1+j*w/n,y+h-.47,w/n-.2,.35,'#fffdf7',7)
        self.rect(x+.02,y+.12,w-.04,.5,'#9d9d83')

    def finish(self,name):
        self.line(0,11.3,9.6,11.3,'#949c95')
        for x in [0,9.6]: self.line(x,10.8,x,11.5,'#949c95')
        self.text(4.8,11.42,'9,60 m',16,'#6c756d',400)
        self.line(-.62,0,-.62,10.8,'#949c95')
        for y in [0,10.8]: self.line(-.8,y,0,y,'#949c95')
        a,b=self.point(-.82,5.4)
        self.parts.append(f'<text x="{a}" y="{b}" transform="rotate(-90 {a} {b})" text-anchor="middle" font-family="Arial" font-size="16" fill="#6c756d">10,80 m</text>')
        self.text(5.65,-.55,'EINGANG / GIEBELSEITE',13,'#ba1325')
        self.parts.append('<text x="80" y="1135" font-family="Arial,sans-serif" font-size="16" fill="#505b53">Zwei Vollgeschosse · Satteldach 35° · durchgehende Erschließung</text><text x="80" y="1165" font-family="Arial,sans-serif" font-size="13" fill="#778077">Schematische Raumorganisation. Kein Ausführungsplan; Treppe, Türen und Maße vor dem Modellbau prüfen.</text></svg>')
        (ROOT/name).write_text('\n'.join(self.parts),encoding='utf-8')


def ground():
    p=Plan('Erdgeschoss','Wohnen und Arbeiten unten. Technik in einem eigenen Raum.')
    p.rect(6.45,.3,2.85,3.15,'url(#tile)')
    p.rect(6.45,3.6,2.85,1.65,'url(#tile)')
    p.wall(4.8,.3,.15,5.7)
    p.wall(3.8,6.6,.15,3.9)
    p.wall(6.3,.3,.15,10.2)
    p.wall(6.45,3.45,2.85,.15)
    p.wall(6.45,5.25,2.85,.15)
    for y in [1.6,3.8,5.65]: p.door(6.3,y,direction=1)
    p.door(4.8,3.35,direction=-1)
    p.rect(4.77,5.1,.22,1.3,'#f1e8d9')
    p.window(.85,0,3.1,.3)
    p.window(7.65,0,.8,.3)
    p.rect(5.1,0,1.1,.32,'#c6aa7f','#a3865c')
    p.window(0,1.15,.3,2.6)
    p.window(0,7.55,.3,1.6)
    p.window(1.05,10.5,2.0,.3)
    p.window(7.0,10.5,1.65,.3)
    p.window(9.3,1.0,.3,1.1)
    p.window(9.3,4.0,.3,.8)
    p.window(9.3,7.2,.3,1.5)
    p.furniture(.7,.75,3.5,3.0,'#e7e1d4',10)
    p.furniture(.8,.9,.9,2.7,'#d0cbbb',12)
    p.furniture(.8,.9,2.15,.85,'#d0cbbb',12)
    p.furniture(2.1,2.0,1.35,.7,'#c5ad86',12)
    p.furniture(4.35,1.0,.32,1.9,'#bcaa91',2)
    p.furniture(1.05,5.05,2.45,1.0,'#cfb58c',8)
    for x in [1.25,2.3,3.0]:
        p.furniture(x,4.57,.45,.4,'#d1cfbd',7)
        p.furniture(x,6.14,.45,.4,'#d1cfbd',7)
    p.furniture(.45,9.8,3.0,.55,'#dad7cd',2)
    p.furniture(.45,7.15,.55,2.65,'#dad7cd',2)
    p.furniture(2.2,9.84,.65,.43,'#f2f3ee',4)
    p.rect(.48,7.5,.5,.65,'#404943')
    p.furniture(3.1,9.0,.65,.7,'#c2bba9',2)
    p.text(2.55,4.04,'Wohnen / Essen',18)
    p.text(2.25,8.42,'Küche',18)
    p.text(5.64,2.72,'Diele',16)
    p.text(7.85,2.24,'HWR / Technik',16)
    p.furniture(6.75,2.87,1.5,.35,'#e7e8e3',2)
    p.rect(6.85,2.95,.52,.18,'#6a716e')
    p.rect(7.5,2.95,.55,.18,'#46534d')
    for y in [.6,1.4]:
        p.furniture(8.5,y,.62,.62,'#f5f6f1',2)
        p.circle(8.81,y+.31,.2,'#dce2df','#77877e')
    p.furniture(8.4,4.3,.65,.6,'#fafbf7',14)
    p.furniture(6.75,4.68,.6,.42,'#fafbf7',5)
    p.text(8.0,3.93,'Gäste-WC',15)
    p.furniture(6.75,8.0,.85,2.0,'#d0cbbb',10)
    p.furniture(8.55,8.0,.6,1.8,'#cdb58e',3)
    p.circle(8.13,8.9,.25,'#d2d1c1')
    p.text(7.84,7.16,'Büro / Gast',16)
    p.stairs()
    p.finish('09-grundriss-eg.svg')


def upper():
    p=Plan('Obergeschoss','Drei Schlafzimmer, Familienbad und dieselbe Treppe.')
    p.rect(6.45,6.6,2.85,3.9,'url(#tile)')
    p.wall(4.55,.3,.15,4.8)
    p.wall(6.3,.3,.15,4.8)
    p.wall(.3,5.1,4.4,.15)
    p.wall(6.3,5.1,3.0,.15)
    p.wall(.3,6.45,3.65,.15)
    p.wall(6.3,6.45,3.0,.15)
    p.wall(3.8,6.6,.15,3.9)
    p.wall(6.3,6.6,.15,3.9)
    p.door(4.55,3.6,direction=-1)
    p.door(6.3,3.6,direction=1)
    p.door(2.65,6.45,'horizontal',1)
    p.door(6.62,6.45,'horizontal',1)
    p.window(1.0,0,2.5,.3)
    p.window(7.05,0,1.85,.3)
    p.window(0,1.8,.3,1.7)
    p.window(0,7.8,.3,1.5)
    p.window(1.1,10.5,1.8,.3)
    p.window(7.0,10.5,1.7,.3)
    p.window(9.3,1.3,.3,1.5)
    p.window(9.3,8.0,.3,1.4)
    p.bed(1.3,1.0,1.8,2.05)
    p.furniture(.65,2.4,.5,.55,'#c6ae88')
    p.furniture(3.25,2.4,.5,.55,'#c6ae88')
    p.furniture(.55,4.35,3.25,.6,'#cdb894',1)
    p.text(2.35,3.78,'Eltern',18)
    p.bed(6.7,1.35,1.05,2.0)
    p.furniture(8.55,.65,.55,1.6,'#cdb894',3)
    p.furniture(8.25,4.38,.85,.55,'#cdb894',1)
    p.text(7.89,3.86,'Kind 2',18)
    p.bed(.65,7.38,1.05,2.0)
    p.furniture(2.5,9.8,1.0,.55,'#cdb894',3)
    p.furniture(3.1,7.75,.55,1.5,'#cdb894',1)
    p.text(2.02,7.02,'Kind 1',18)
    p.furniture(6.7,9.5,2.2,.75,'#fafbf6',24)
    p.furniture(8.6,6.88,.5,1.4,'#cdb894',2)
    p.furniture(8.62,7.02,.44,.5,'#fafbf6',8)
    p.furniture(8.62,7.69,.44,.5,'#fafbf6',8)
    p.furniture(6.62,8.3,1.05,1.05,'#f0f4f0',2)
    p.line(6.64,8.31,7.65,9.33,'#c0cdc3',.8)
    p.furniture(8.36,8.74,.65,.57,'#fafbf6',20)
    p.text(7.58,8.0,'Familienbad',15)
    p.text(5.0,5.7,'Diele / alle Zimmer direkt erreichbar',15)
    p.stairs(True)
    p.finish('10-grundriss-og.svg')


if __name__=='__main__':
    if (ROOT / 'reference-lock.json').exists():
        raise SystemExit('V4 reference is sealed. Work in a new revision folder; do not overwrite the selected plans.')
    ground()
    upper()
    print('Wrote 09-grundriss-eg.svg and 10-grundriss-og.svg')
