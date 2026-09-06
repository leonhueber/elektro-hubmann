"""One consistent two-storey building with actual openings and stair void."""
import math
from . import core as c

ROOTS = {}
W,D,H=9.6,10.8,3.0


def mark(obj,cut=False):
    if cut: obj['cutaway_upper']=True
    return obj


def wall(name,axis,start,end,fixed,thick,holes=(),cut=False,height=2.78):
    # Build around real rectangular openings; never paint windows onto a solid wall.
    us=sorted(set([start,end]+[v for h in holes for v in h[:2]]))
    zs=sorted(set([0,1.18,height]+[v for h in holes for v in h[2:4]]))
    groups={False:[],True:[]}
    for a,b in zip(us,us[1:]):
        for low,high in zip(zs,zs[1:]):
            if high-low<.001 or b-a<.001:continue
            if any(h[0]<(a+b)/2<h[1] and h[2]<(low+high)/2<h[3] for h in holes):continue
            loc=((a+b)/2,fixed,(low+high)/2) if axis=='X' else (fixed,(a+b)/2,(low+high)/2)
            size=(b-a,thick,high-low) if axis=='X' else (thick,b-a,high-low)
            groups[cut and low>=1.18].append((loc,size))
    for upper,cells in groups.items():
        if not cells:continue
        verts=[];indices={};faces={}
        for loc,size in cells:
            ids=[]
            for sx,sy,sz in [(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]:
                co=tuple(round(loc[i]+s*size[i]/2,6) for i,s in enumerate([sx,sy,sz]))
                if co not in indices:indices[co]=len(verts);verts.append(co)
                ids.append(indices[co])
            for face in [(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]:
                f=tuple(ids[i] for i in face);key=tuple(sorted(f))
                if key in faces:del faces[key]
                else:faces[key]=f
        o=mark(c.mesh(name+(' | removable upper' if upper else ' | continuous plaster'),verts,list(faces.values()),'plaster',bevel=.0015),upper)
        o.data.materials.append(c.M['cut'])
        for face in o.data.polygons:
            at_head=all(abs(o.data.vertices[v].co.z-height)<.001 for v in face.vertices)
            at_cut=cut and not upper and all(abs(o.data.vertices[v].co.z-1.18)<.001 for v in face.vertices)
            if at_head or at_cut:face.material_index=1


def window(name,center,width,bottom,height,axis='X',cut=False):
    root=c.empty(name,center,0 if axis=='X' else math.pi/2)
    for x in [-width/2+.035,width/2-.035]:
        mark(c.box(name+' | outer jamb',(x,0,bottom+height/2),(.07,.15,height),'charcoal',.008,root),cut)
        mark(c.box(name+' | sash jamb',(x+(.045 if x<0 else -.045),-.012,bottom+height/2),(.035,.07,height-.11),'charcoal',.006,root),cut)
    for z in [bottom+.035,bottom+height-.035]:
        mark(c.box(name+' | outer rail',(0,0,z),(width,.15,.07),'charcoal',.008,root),cut and z>1.18)
    panes=2 if width>1.4 else 1
    for i in range(panes):
        x=-width/2+width*(i+.5)/panes
        pane=mark(c.box(name+' | recessed double glazing',(x,.019,bottom+height/2),(width/panes-.09,.014,height-.13),'glass',.001,root),cut)
        pane.visible_shadow=False
    if panes==2:
        mark(c.box(name+' | central meeting stile',(0,-.022,bottom+height/2),(.065,.105,height-.07),'charcoal',.006,root),cut)
    c.box(name+' | projecting sill',(0,-.075,bottom-.025),(width+.13,.29,.035),'charcoal',.007,root)
    return root


def skirting(name,axis,start,end,fixed):
    loc=((start+end)/2,fixed,.055) if axis=='X' else (fixed,(start+end)/2,.055)
    size=(end-start,.018,.11) if axis=='X' else (.018,end-start,.11)
    c.box(name,loc,size,'oak pale',.003)


def door(name,x,y,angle=0,width=.85,opened=.62):
    root=c.empty(name,(x,y,0),angle)
    root['interior_door']=True
    for xx in [-width/2-.032,width/2+.032]:
        c.box(name+' | lower flush lining',(xx,0,.59),(.055,.17,1.18),'plaster',.003,root)
        mark(c.box(name+' | upper flush lining',(xx,0,1.64),(.055,.17,.92),'plaster',.003,root),True)
    mark(c.box(name+' | lining head',(0,0,2.105),(width+.12,.17,.065),'plaster',.003,root),True)
    pivot=c.empty(name+' | hinge',(-width/2,0,0),opened,root)
    mark(c.box(name+' | flush white leaf',(width/2,0,1.015),(width-.015,.044,2.03),'plaster',.004,pivot),True)
    # Complete leaves and hardware disappear with the upper cut walls. The
    # retained low jambs show real openings without isolated doors in the rooms.
    for side in [-1,1]:
        mark(c.cylinder(name+' | handle rosette',(width-.14,side*.029,1.02),.026,.012,'charcoal',pivot,(math.pi/2,0,0)),True)
        mark(c.rod(name+' | lever',(width-.14,side*.05,1.02),(width-.27,side*.05,1.02),.011,'charcoal',pivot),True)
    for z in [.28,1.76]:mark(c.cylinder(name+' | hinge barrel',(.008,0,z),.01,.065,'steel',pivot),True)
    return root


def boards(name,rect,mat='oak pale',void=None,tile=False):
    x0,y0,x1,y1=rect
    width,length=(.6,.6) if tile else (.19,1.75)
    row=0;x=x0
    while x<x1-.002:
        y=y0-(0 if tile else (row%3)*length/3)
        while y<y1:
            a,b=max(y,y0),min(y+length,y1)
            xx=min(x+width,x1)
            if b>a+.008:
                cells=[(x,a,xx,b)]
                if void:
                    vx0,vy0,vx1,vy1=void
                    if x<vx1 and xx>vx0 and a<vy1 and b>vy0:
                        cells=[]
                        for ax,bx,ay,by in [(x,min(xx,vx0),a,b),(max(x,vx1),xx,a,b),
                                             (max(x,vx0),min(xx,vx1),a,min(b,vy0)),
                                             (max(x,vx0),min(xx,vx1),max(a,vy1),b)]:
                            if bx-ax>.008 and by-ay>.008:cells.append((ax,ay,bx,by))
                for ax,ay,bx,by in cells:
                    c.box(name,((ax+bx)/2,(ay+by)/2,.025),(bx-ax-.002,by-ay-.002,.045),mat,.0007 if tile else .001)
            y+=length
        x+=width;row+=1


def floor(level,parent):
    c.collection(f'V4 | {level} 01 Floor',parent,level)
    if level=='EG':
        c.box('EG | slab',(4.8,5.4,-.125),(9.6,10.8,.25),'stone',.008)
        boards('EG | oak plank',(.3,.3,6.30,10.5))
        boards('EG | office oak plank',(6.45,5.40,9.3,10.5))
        boards('EG | HWR limestone tile',(6.45,.3,9.3,3.45),'tile',tile=True)
        boards('EG | WC limestone tile',(6.45,3.60,9.3,5.25),'tile',tile=True)
    else:
        # Four slab rectangles leave the real stairwell completely open.
        for x0,y0,x1,y1 in [(0,0,9.6,6.6),(0,6.6,3.95,10.8),(6.3,6.6,9.6,10.8),(3.95,10.35,6.3,10.8)]:
            c.box('OG | slab with stair void',((x0+x1)/2,(y0+y1)/2,-.11),(x1-x0,y1-y0,.22),'plaster',.001)
        boards('OG | oak plank',(.3,.3,9.3,6.45))
        boards('OG | child oak plank',(.3,6.6,3.8,10.5))
        boards('OG | landing oak plank',(3.8,6.45,6.3,10.5),void=(3.95,6.6,6.3,10.35))
        boards('OG | family bath tile',(6.45,6.6,9.3,10.5),'tile',tile=True)


def facade(level,parent):
    c.collection(f'V4 | {level} 02 Facade',parent,level)
    front=[(.85,4.25,.07,2.30),(4.95,6.55,0,2.44),(7.65,8.53,.85,2.05)] if level=='EG' else [(1.0,3.5,.65,2.43),(6.82,8.85,.65,2.43)]
    left=[(1.35,3.45,.7,2.3),(7.75,9.35,1.13,2.36)]
    right=[(1.35,2.25,.83,2.1),(7.45,8.45,.83,2.1)]
    back=[(1.05,3.3,1.2,2.38),(7.0,8.75,1.12,2.35)]
    wall(level+' | front','X',0,W,.15,.30,front,True)
    wall(level+' | left','Y',.3,D, .15,.30,left,False)
    wall(level+' | right','Y',.3,D,9.45,.30,right,True)
    wall(level+' | rear','X',.3,9.3,10.65,.30,back,False)
    # Storey edge is part of that storey, not a floating decorative belt.
    for axis,a,b,f in ([('X',0,W,.15),('X',0,W,10.65),('Y',.3,10.5,.15),('Y',.3,10.5,9.45)] if level=='OG' else []):
        mark(c.box(level+' | wall head',((a+b)/2,f,2.89) if axis=='X' else (f,(a+b)/2,2.89),
                   (b-a,.30,.22) if axis=='X' else (.30,b-a,.22),'plaster',.001),True)
    for axis,f,holes in [('X',.15,front),('Y',.15,left),('Y',9.45,right),('X',10.65,back)]:
        for i,(a,b,z0,z1) in enumerate(holes):
            if level=='EG' and axis=='X' and f==.15 and a==4.95:continue
            center=((a+b)/2,f,0) if axis=='X' else (f,(a+b)/2,0)
            window(f'{level} | {axis}{f} window {i}',center,b-a,z0,z1-z0,axis,cut=((f in [.15,9.45] and axis=='X') or f==9.45) and not(level=='OG' and axis=='X' and f==.15))
    for axis,a,b,f in [('Y',.4,10.4,.317),('Y',.4,10.4,9.283),('X',.4,9.2,10.48)]:
        skirting(level+' | perimeter skirting',axis,a,b,f)


def partitions(level,parent):
    c.collection(f'V4 | {level} 03 Partitions and doors',parent,level)
    if level=='EG':
        wall('EG | living / hall','Y',.3,6.4,4.8,.15,[(3.35,6.4,0,2.6)],True)
        wall('EG | service spine','Y',.3,10.5,6.375,.15,[(1.6,2.5,0,2.1),(3.8,4.7,0,2.1),(5.65,6.55,0,2.1)],True)
        wall('EG | WC front','X',6.45,9.3,3.525,.15,cut=True)
        wall('EG | WC back','X',6.45,9.3,5.325,.15,cut=False)
        wall('EG | stair side','Y',6.6,10.5,3.875,.15,cut=True)
        # The living/dining zone has a broad open passage. Only private/service
        # rooms need doors; these swing into their rooms instead of into the hall.
        for name,y in [('HWR',2.05),('WC',4.25),('office',6.1)]:
            door('EG | '+name+' door',6.375,y,math.pi/2,opened=-math.radians(85))
        skirting('EG | living skirting','Y',.35,3.30,4.70)
        skirting('EG | office skirting','X',6.45,9.25,5.425)
    else:
        wall('OG | parents hall','Y',.3,5.1,4.625,.15,[(3.6,4.5,0,2.1)],True)
        wall('OG | child hall','Y',.3,5.1,6.375,.15,[(3.6,4.5,0,2.1)],True)
        wall('OG | parents back','X',.3,4.7,5.175,.15,cut=False)
        wall('OG | child front back','X',6.3,9.3,5.175,.15,cut=False)
        wall('OG | child rear front','X',.3,3.95,6.525,.15,[(2.65,3.55,0,2.1)],True)
        wall('OG | bath front','X',6.3,9.3,6.525,.15,[(6.62,7.52,0,2.1)],True)
        wall('OG | child stair','Y',6.6,10.5,3.875,.15,cut=True)
        wall('OG | bath stair','Y',6.6,10.5,6.375,.15,cut=True)
        for name,x,y,angle in [('parents',4.625,4.05,math.pi/2),('child front',6.375,4.05,math.pi/2),('child rear',3.1,6.525,0),('bath',7.07,6.525,0)]:
            door('OG | '+name+' door',x,y,angle)


def stairs(parent):
    c.collection('V4 | EG 04 U stair',parent,'EG / OG staircase')
    for i in range(9):
        y=6.65+i*.30;z=(i+1)/6
        c.box('U stair | lower riser',(4.51,y+.14,z-.08),(1.04,.28,.16),'oak pale',.004)
        c.box('U stair | lower nosing',(4.51,y+.135,z+.015),(1.075,.31,.035),'oak',.005)
        y2=9.05-i*.30;z2=1.5+(i+1)/6
        c.box('U stair | upper riser',(5.74,y2+.14,z2-.08),(1.04,.28,.16),'oak pale',.004)
        c.box('U stair | upper nosing',(5.74,y2+.135,z2+.015),(1.075,.31,.035),'oak',.005)
        if i%2==0:
            for x,yy,zz in [(5.02,y+.15,z),(5.23,y2+.15,z2)]:
                c.rod('U stair | steel baluster',(x,yy,zz),(x,yy,zz+.9),.012,'charcoal')
    c.box('U stair | intermediate landing',(5.125,9.87,1.44),(2.27,1.14,.12),'oak pale',.008)
    c.rod('U stair | lower oak handrail',(5.02,6.65,1.08),(5.02,9.28,2.5),.029,'oak')
    c.rod('U stair | upper oak handrail',(5.23,6.65,3.92),(5.23,9.28,2.5),.029,'oak')
    c.rod('U stair | landing handrail',(5.02,9.28,2.5),(5.23,9.28,2.5),.029,'oak')


def isolated_stairwell_context(parent):
    """Retain only the actual EG shaft surfaces when isolating the upper floor."""
    c.collection('V4 | 92 Isolated stairwell context',parent,'EG / OG staircase')
    # Same wall positions/thicknesses as the EG rear, service spine and stair side.
    # These clipped presentation copies are hidden in all other model views.
    for name,loc,size,mat in [
        ('left lining',(3.875,8.475,1.39),(.15,3.75,2.78),'plaster'),
        ('right lining',(6.375,8.475,1.39),(.15,3.75,2.78),'plaster'),
        ('rear lining',(5.125,10.65,1.39),(2.65,.30,2.78),'plaster'),
        ('floor below void',(5.125,8.55,.025),(2.35,3.90,.045),'oak pale')
    ]:
        obj=c.box('Isolated OG | retained stairwell '+name,loc,size,mat,.001)
        obj['og_stairwell_context']=True
        obj.hide_render=True;obj.hide_set(True)


def roof(parent):
    c.collection('V4 | Roof 01 Standing seam and gables',parent,'Roof')
    c.box('Roof | attic floor and OG ceiling',(4.8,5.4,-.11),(9.0,10.2,.22),'plaster',.002)
    angle=math.radians(35);ridge=4.8*math.tan(angle)
    for y in [.15,10.65]:
        verts=[(0,y-.15,0),(9.6,y-.15,0),(4.8,y-.15,ridge),(0,y+.15,0),(9.6,y+.15,0),(4.8,y+.15,ridge)]
        c.mesh('Roof | solid plaster gable',verts,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'plaster',bevel=.004)
    slope=5.02/math.cos(angle)
    for side in [-1,1]:
        x=4.8+side*2.51;z=ridge-2.51*math.tan(angle)+.065
        o=c.box('Roof | folded metal plane',(x,5.4,z),(slope,11.25,.09),'roof',.008)
        o.rotation_euler.y=side*angle
        for i in range(24):
            yy=-.21+i*11.22/23
            c.rod('Roof | standing seam',(4.8,yy,ridge+.126),(4.8+side*5.02,yy,-.154+.126),.012,'roof')
        for yy in [-.225,11.025]:
            c.rod('Roof | folded verge',(4.8,yy,ridge+.13),(4.8+side*5.06,yy,-.16+.1),.048,'roof')
        # Half-round eaves channel, modelled with open cross-section.
        points=[(4.8+side*5.05+.065*math.cos(math.pi+i*math.pi/20),-.2,-.10+.065*math.sin(math.pi+i*math.pi/20)) for i in range(21)]
        verts=[(x,yy,z) for yy in [-.2,11.03] for x,_,z in points]
        c.mesh('Roof | half-round rain gutter',verts,[(i,i+1,22+i,21+i) for i in range(20)],'charcoal',smooth=True)
    c.rod('Roof | ridge cap',(4.8,-.26,ridge+.15),(4.8,11.07,ridge+.15),.062,'roof')
    c.collection('V4 | Roof 02 Photovoltaic 10 modules',parent,'Photovoltaic')
    # Two rows down slope; five modules along ridge, centred on the usable roof.
    # The reference field fills most of the slope and has equal gable setbacks.
    length,width,gap=2.20,1.40,.05
    glass_length,glass_width=length-.05,width-.05
    for row in range(2):
        distance=2.04+row*(length+gap)
        for col in range(5):
            x=4.8+distance*math.cos(angle);y=5.4+(col-2)*(width+gap);z=ridge-distance*math.sin(angle)+.20
            module=c.empty(f'PV | module {row*5+col+1:02d}',(x,y,z))
            module.rotation_euler.y=angle
            c.box('PV | anodised perimeter frame',(0,0,0),(length,width,.038),'charcoal',.005,module)
            c.box('PV | dark glass laminate',(0,0,.022),(glass_length,glass_width,.012),'pv',.003,module)
            for u in range(1,12):c.box('PV | cell joint',(-glass_length/2+u*glass_length/12,0,.029),(.0012,glass_width-.005,.0008),'pv grid',0,module)
            for v in range(1,6):c.box('PV | cell joint',(0,-glass_width/2+v*glass_width/6,.029),(glass_length-.005,.0012,.0008),'pv grid',0,module)
            for yy in [-.46,.46]:c.box('PV | mounting rail',(0,yy,-.045),(length-.04,.025,.05),'steel',.002,module)


def build():
    c.collection('V4 | 00 Assembly roots')
    ROOTS['EG']=c.empty('V4 | EG assembly')
    ROOTS['OG']=c.empty('V4 | OG assembly',(0,0,3))
    ROOTS['Roof']=c.empty('V4 | Roof assembly',(0,0,6))
    for level in ['EG','OG']:
        floor(level,ROOTS[level]);facade(level,ROOTS[level]);partitions(level,ROOTS[level])
    stairs(ROOTS['EG']);roof(ROOTS['Roof'])
    c.collection('V4 | EG 05 Entrance and terrace',ROOTS['EG'],'Entrance')
    c.box('Entrance | recessed return left',(5.03,.43,1.2),(.16,.56,2.4),'plaster',.005)
    c.box('Entrance | recessed return right',(6.47,.43,1.2),(.16,.56,2.4),'plaster',.005)
    c.box('Entrance | recessed soffit',(5.75,.42,2.38),(1.6,.55,.14),'plaster',.004)
    for x in [5.15,6.35]:c.box('Entrance | oak jamb',(x,.66,1.1),(.065,.12,2.2),'oak',.006)
    c.box('Entrance | oak head',(5.75,.66,2.2),(1.27,.12,.065),'oak',.006)
    c.box('Entrance | thick oak door',(5.75,.69,1.09),(1.15,.068,2.15),'oak',.009)
    for x in [5.40,5.60,5.80,6.0,6.2]:c.box('Entrance | fine vertical board joint',(x,.654,1.09),(.0015,.001,2.12),'oak dark',0)
    c.cylinder('Entrance | handle rose',(5.32,.635,1.0),.031,.016,'charcoal',rotation=(math.pi/2,0,0))
    c.rod('Entrance | door lever',(5.31,.595,1.0),(5.49,.595,1.0),.015,'charcoal')
    c.cylinder('Entrance | key cylinder',(5.32,.625,.85),.016,.022,'charcoal',rotation=(math.pi/2,0,0))
    c.box('Entrance | stone step',(5.75,-.46,-.08),(2.0,1.5,.24),'stone',.012)
    c.box('Entrance | recessed stone threshold',(5.75,.41,.056),(1.35,.83,.028),'stone',.005)
    c.box('Terrace | stone base',(2.32,-.70,-.12),(4.66,1.75,.16),'stone',.01)
    for i in range(9):c.box('Terrace | oak decking',(2.32,-1.44+i*.18,-.014),(4.65,.176,.049),'oak pale',.003)
    for x in [.05,9.55]:
        for level in ['EG','OG']:
            parent=ROOTS[level]
            c.tube(f'Facade | {level} downpipe lower',[(x,-.19,0),(x,-.19,1.17)],.039,'charcoal',parent)
            mark(c.tube(f'Facade | {level} downpipe upper',[(x,-.19,1.17),(x,-.19,2.79)],.039,'charcoal',parent),True)
            if level=='OG':
                mark(c.tube('Facade | downpipe swan neck',[(x,-.19,2.79),(x,-.10,2.87),(x,-.05,2.94)],.039,'charcoal',parent),True)
            else:
                mark(c.tube('Facade | storey pipe joint',[(x,-.19,2.79),(x,-.19,3)],.039,'charcoal',parent),True)
            for z in [.5,2.6]:mark(c.cylinder('Facade | pipe collar',(x,-.19,z),.045,.035,'charcoal',parent),z>1.18)
    c.box('Facade | plinth front left',(2.45,.05,-.12),(4.9,.35,.24),'stone',.004)
    c.box('Facade | plinth right',(9.48,5.4,-.12),(.24,10.8,.24),'stone',.004)
    return ROOTS
